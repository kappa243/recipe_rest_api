
import asyncio
import json

import aiohttp
from app.models import Ingredient, Recipe, RecipeSearch, RecipeSearchCollection


class TastyAPI():

    def __init__(self) -> None:
        settings = json.load(open('app/settings.json'))

        self.__url = settings['api']['tasty']['url']
        self.__headers = {
            'X-RapidAPI-Key': settings['api']['tasty']['api_key'],
            'X-RapidAPI-Host': settings['api']['tasty']['api_host']
        }

    async def get_recipes(self, name: str = "", category: str = "", area: str = "", ingredient: str = "", start: int = 0, size: int = 20) -> RecipeSearchCollection:
        url = f'{self.__url}recipes/list'

        name = name.lower()
        category = category.lower()
        area = area.lower()
        ingredient = ingredient.lower()

        query = f'{name} {category} {area} {ingredient}'
        query = query.strip()
        params = {
            'from': start,
            'size': size,
            'q': query
        }

        async with aiohttp.ClientSession(headers=self.__headers) as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

                raw_recipes = data['results']

                if (data['count'] == 0):
                    return RecipeSearchCollection(recipes=[], total=0)
                
                recipes = []

                iter_recipes = []
                for raw_recipe in raw_recipes:
                    # if contains 'recipes' (bundle of recipes), then iterate over it
                    if raw_recipe.get('recipes') is not None:
                        for sub_recipe in raw_recipe['recipes']:
                            iter_recipes.append(sub_recipe)
                    else:
                        iter_recipes.append(raw_recipe)

                for raw_recipe in iter_recipes:
                    if name not in raw_recipe['name']:
                        continue
                    
                    category_match = False
                    area_match = False
                    
                    if category == "": category_match = True
                    if area == "": area_match = True
                    
                    for tag in raw_recipe['tags']:
                        if category_match and area_match:
                            break

                        if tag['type'] == 'meal' and not category_match:
                            if category in tag['display_name']:
                                category_match = True
                        elif tag['type'] == 'cuisine' and not area_match:
                            if area in tag['display_name']:
                                area_match = True
                    
                    if not category_match or not area_match:
                        continue


                    ingredient_match = False
                    if ingredient == "": ingredient_match = True

                    for part in raw_recipe['sections']:
                        for component in part['components']:
                            if ingredient in component['raw_text']:
                                ingredient_match = True
                                break
                    
                    if not ingredient_match:
                        continue

                    id = "tt_" + str(raw_recipe['id'])
                    name = raw_recipe['name']
                    thumbnail = raw_recipe['thumbnail_url']

                    recipe = RecipeSearch(id=id, name=name, thumbnail=thumbnail)
                    recipes.append(recipe)

                return RecipeSearchCollection(recipes=recipes, total=data['count'])

    async def get_recipe_by_id(self, id: int) -> Recipe:
        url = f'{self.__url}recipes/get-more-info'
        params = {
            'id': id
        }

        async with aiohttp.ClientSession(headers=self.__headers) as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

                raw_recipe = data

                if (response.status == 204):
                    err = aiohttp.ClientResponseError(None, tuple())
                    err.request_info = response.request_info
                    err.status = response.status
                    err.message = 'Recipe not found.'

                    raise err

                return self.__parse_raw_recipe(raw_recipe)
            
    def __parse_raw_recipe(self, raw_recipe: dict) -> Recipe:
        id = "tt_" + str(raw_recipe['id'])
        name = raw_recipe['name']

        category = []
        area = []

        for tag in raw_recipe['tags']:
            if tag['type'] == 'meal':
                category.append(tag['display_name'])
            elif tag['type'] == 'cuisine':
                area.append(tag['display_name'])

        instructions = ""
        for line in raw_recipe['instructions']:
            instructions += line['display_text'] + "\n"

        thumbnail = raw_recipe['thumbnail_url']
        video = raw_recipe['video_url']

        ingredients = []
        for part in raw_recipe['sections']:
            for component in part['components']:
                ingredient = component['raw_text']

                ingredients.append(Ingredient(name=ingredient))
        
        return Recipe(id=id,
                      name=name,
                      category=category,
                      area=area,
                      instructions=instructions,
                      thumbnail=thumbnail,
                      video=video,
                      ingredients=ingredients)
        



async def main():
    list = await TastyAPI().get_recipe_by_name('chicken', start=0, size=20)
    print(list)

    # recipe = await TastyAPI().get_recipe_by_id(3500)
    # print(recipe)

if __name__ == '__main__':
    asyncio.run(main())
