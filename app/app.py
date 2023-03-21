import asyncio
from typing import Optional
import aiohttp
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from app.models import Recipe, RecipeSearchCollection

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# providers
from app.edamam_api import EdamamAPI
from app.themealdb_api import TheMealDBAPI
from app.tasty_api import TastyAPI

edamam = EdamamAPI()
themealdb = TheMealDBAPI()
tasty = TastyAPI()

@app.get("/", response_class=HTMLResponse)
async def root(requset: Request):
    return templates.TemplateResponse("index.html", {"request": requset})

@app.get("/api/recipes")
async def get_recipes(name: str, category: Optional[str] = "",  area: Optional[str] = "", ingredient: Optional[str] = "", start: int = 0, size: int = 10) -> RecipeSearchCollection:


    try:
        # bad api requires workaround
        tasks = [
            asyncio.create_task(themealdb.get_recipes_by_name(name))
        ]
        i = 0
        if category != "":
            tasks.append(asyncio.create_task(themealdb.get_recipes_by_category(category)))
            i+=1
            cat_i = i
        if area != "":
            tasks.append(asyncio.create_task(themealdb.get_recipes_by_area(area)))
            i+=1
            area_i = i
        if ingredient!= "":
            tasks.append(asyncio.create_task(themealdb.get_recipes_by_ingredient(ingredient)))
            i+=1
            ing_i = i

        
        tasks.append(asyncio.create_task(tasty.get_recipes(name, category, area, ingredient)))

        results = await asyncio.gather(*tasks)

        # get only results that match all filters
        recipes = []
        for recipe in results[0].recipes:
            if category != "" and recipe.id not in [r.id for r in results[cat_i].recipes]:
                continue
            if area != "" and recipe.id not in [r.id for r in results[area_i].recipes]:
                continue
            if ingredient != "" and recipe.id not in [r.id for r in results[ing_i].recipes]:
                continue
            recipes.append(recipe)

        recipes.extend(results[-1].recipes)

    except aiohttp.ClientResponseError:
        return JSONResponse(status_code=500, content={"message": "Internal Server Error."})
        
    if len(recipes) == 0:
        return JSONResponse(status_code=404, content={"message": "No recipes found."})

    recipesCollection = RecipeSearchCollection(recipes=recipes, total=len(recipes))
       

    # sort by name
    recipesCollection.recipes.sort(key=lambda x: x.name)

    # slice
    recipesCollection.recipes = recipesCollection.recipes[start:start+size]

    # return results
    return recipesCollection
    
    
@app.get("/api/recipes/{id}")
async def get_recipe(id: str) -> Recipe:
    try:
        if id.startswith("tmd_"):
            recipe = await themealdb.get_recipe_by_id(id.replace("tmd_", ""))
        elif id.startswith("tt_"):
            recipe = await tasty.get_recipe_by_id(id.replace("tt_", ""))
        else:
            return JSONResponse(status_code=420, content={"message": "Invalid recipe id."})
    except aiohttp.ClientResponseError as e:
        if e.status == 404 or e.status == 204:
            return JSONResponse(status_code=404, content={"message": "Recipe not found."})
        else:
            return JSONResponse(status_code=500, content={"message": "Internal Server Error."})


    for ingredient in recipe.ingredients:
        try:
            ingredient.nutrition = await edamam.get_nutrition_by_name(ingredient.name)
        except aiohttp.ClientResponseError:
            ingredient.nutrition = None
    
    return recipe
