import json
import aiohttp
import asyncio

from app.models import Ingredient, Recipe, RecipeSearch, RecipeSearchCollection


class TheMealDBAPI():

    def __init__(self) -> None:
        settings = json.load(open('app/settings.json'))

        self.__url = settings['api']['themealdb']['url']

    async def get_recipes_by_name(self, name: str) -> RecipeSearchCollection:
        name = name.lower()
        query = f'{self.__url}/search.php?s={name}'

        async with aiohttp.ClientSession() as session:
            async with session.get(query) as response:
                data = await response.json()

                raw_recipes = data['meals']

                if (raw_recipes is None):
                    return RecipeSearchCollection(recipes=[], total=0)

                recipes = []
                for raw_recipe in raw_recipes:
                    id = "tmd_" + str(raw_recipe['idMeal'])
                    name = raw_recipe['strMeal']
                    thumbnail = raw_recipe['strMealThumb']

                    recipe = RecipeSearch(id=id,
                                          name=name,
                                          thumbnail=thumbnail)
                    recipes.append(recipe)

                return RecipeSearchCollection(recipes=recipes, total=len(recipes))

    async def get_recipe_by_id(self, id: int) -> Recipe:
        query = f'{self.__url}/lookup.php?i={id}'

        async with aiohttp.ClientSession() as session:
            async with session.get(query) as response:
                data = await response.json()

                raw_recipe = data['meals']

                if (raw_recipe is None):
                    err = aiohttp.ClientResponseError(None, tuple())
                    err.request_info = response.request_info
                    err.status = 404
                    err.message = 'Recipe not found'

                    raise err

                return self.__parse_raw_recipe(raw_recipe[0])

    async def get_recipes_by_category(self, category: str) -> RecipeSearchCollection:
        category = category.lower()
        query = f'{self.__url}/filter.php?c={category}'

        async with aiohttp.ClientSession() as session:
            async with session.get(query) as response:
                data = await response.json()

                raw_recipes = data['meals']

                if (raw_recipes is None):
                    return RecipeSearchCollection(recipes=[], total=0)

                recipes = []
                for raw_recipe in raw_recipes:
                    id = "tmd_" + str(raw_recipe['idMeal'])
                    name = raw_recipe['strMeal']
                    thumbnail = raw_recipe['strMealThumb']

                    recipe = RecipeSearch(id=id,
                                          name=name,
                                          thumbnail=thumbnail)
                    recipes.append(recipe)

                return RecipeSearchCollection(recipes=recipes, total=len(recipes))

    async def get_recipes_by_area(self, area: str) -> RecipeSearchCollection:
        area = area.lower()
        query = f'{self.__url}/filter.php?a={area}'

        async with aiohttp.ClientSession() as session:
            async with session.get(query) as response:
                data = await response.json()

                raw_recipes = data['meals']

                if (raw_recipes is None):
                    return RecipeSearchCollection(recipes=[], total=0)

                recipes = []
                for raw_recipe in raw_recipes:
                    id = "tmd_" + str(raw_recipe['idMeal'])
                    name = raw_recipe['strMeal']
                    thumbnail = raw_recipe['strMealThumb']

                    recipe = RecipeSearch(id=id,
                                          name=name,
                                          thumbnail=thumbnail)
                    recipes.append(recipe)

                return RecipeSearchCollection(recipes=recipes, total=len(recipes))

    async def get_recipes_by_ingredient(self, ingredient: str) -> RecipeSearchCollection:
        ingredient = ingredient.lower()
        query = f'{self.__url}/filter.php?i={ingredient}'

        async with aiohttp.ClientSession() as session:
            async with session.get(query) as response:
                data = await response.json()

                raw_recipes = data['meals']

                if (raw_recipes is None):
                    return RecipeSearchCollection(recipes=[], total=0)

                recipes = []
                for raw_recipe in raw_recipes:
                    id = "tmd_" + str(raw_recipe['idMeal'])
                    name = raw_recipe['strMeal']
                    thumbnail = raw_recipe['strMealThumb']

                    recipe = RecipeSearch(id=id,
                                          name=name,
                                          thumbnail=thumbnail)
                    recipes.append(recipe)

                return RecipeSearchCollection(recipes=recipes, total=len(recipes))

    def __parse_raw_recipe(self, raw_recipe) -> Recipe:
        id = "tmd_" + str(raw_recipe['idMeal'])
        name = raw_recipe['strMeal']
        category = [raw_recipe['strCategory']]
        area = [raw_recipe['strArea']]
        instructions = raw_recipe['strInstructions'].replace('\r', '')
        thumbnail = raw_recipe['strMealThumb']
        video = raw_recipe['strYoutube']

        ingredients = []

        for i in range(1, 21):
            ingredient = raw_recipe[f'strIngredient{i}']
            measure = raw_recipe[f'strMeasure{i}']

            if (ingredient == "" or measure == ""):
                continue

            ingredients.append(Ingredient(name=measure + " " + ingredient))

        return Recipe(id=id,
                      name=name,
                      category=category,
                      area=area,
                      instructions=instructions,
                      thumbnail=thumbnail,
                      video=video,
                      ingredients=ingredients)


async def main():
    collector = TheMealDBAPI()

    # data = await collector.get_recipes_by_name('chicken')
    # print(data)

    try:
        data = await collector.get_recipe_by_id(52765)
        print(data)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    asyncio.run(main())
