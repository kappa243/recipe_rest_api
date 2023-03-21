import json
import asyncio
import aiohttp

from app.models import Nutrition


class EdamamAPI():

    def __init__(self) -> None:
        settings = json.load(open('app/settings.json'))

        self.__url = settings['api']['edamam']['url'] + 'nutrition-data'
        self.__id = settings['api']['edamam']['app_id']
        self.__key = settings['api']['edamam']['app_key']

    async def get_nutrition_by_name(self, name: str) -> Nutrition:
        query = f'{self.__url}?app_id={self.__id}&app_key={self.__key}&nutrition-type=cooking&ingr={name}'

        async with aiohttp.ClientSession() as session:
            async with session.get(query) as response:
                data = await response.json()

                if data['totalWeight'] == 0:
                    response.status = 404

                if (response.status in [404, 422, 555]):
                    err = aiohttp.ClientResponseError(None, tuple())
                    err.request_info = response.request_info
                    err.status = response.status

                    if(response.status == 404):
                        err.message = 'Ingredient not found or insufficient data'
                    elif(response.status == 422):
                        err.message = 'Couldn\'t parse the recipe or extract the nutritional info'
                    elif(response.status == 555):
                        err.message = 'Recipe with insufficient quality to process correctly'

                    raise err

                return self.parse_raw_ingredient(data)

    def parse_raw_ingredient(self, data) -> Nutrition:
        weight = data['totalWeight']

        if data['totalNutrients'].get('FAT') is None:
            fat = 0
        else:
            fat = data['totalNutrients']['FAT']['quantity']

        if data['totalNutrients'].get('FASAT') is None:
            saturated_fat = 0
        else:
            saturated_fat = data['totalNutrients']['FASAT']['quantity']

        if data['totalNutrients'].get('CHOCDF') is None:
            carbohydrate = 0
        else:
            carbohydrate = data['totalNutrients']['CHOCDF']['quantity']

        if data['totalNutrients'].get('FIBTG') is None:
            fiber = 0
        else:
            fiber = data['totalNutrients']['FIBTG']['quantity']

        if data['totalNutrients'].get('PROCNT') is None:
            protein = 0
        else:
            protein = data['totalNutrients']['PROCNT']['quantity']

        if data['totalNutrients'].get('CHOLE') is None:
            cholesterol = 0
        else:
            cholesterol = data['totalNutrients']['CHOLE']['quantity']


        energy_kcal = data['totalNutrientsKCal']['ENERC_KCAL']['quantity']
        protein_kcal = data['totalNutrientsKCal']['PROCNT_KCAL']['quantity']
        fat_kcal = data['totalNutrientsKCal']['FAT_KCAL']['quantity']
        carbohydrate_kcal = data['totalNutrientsKCal']['CHOCDF_KCAL']['quantity']

        return Nutrition(weight=weight,
                         fat=fat,
                         saturated_fat=saturated_fat,
                         carbohydrate=carbohydrate,
                         fiber=fiber,
                         protein=protein,
                         cholesterol=cholesterol,
                         energy_kcal=energy_kcal,
                         protein_kcal=protein_kcal,
                         fat_kcal=fat_kcal,
                         carbohydrate_kcal=carbohydrate_kcal)


async def main():
    collector = EdamamAPI()

    try:
        data = await collector.get_nutrition_by_name('1 (12 oz.) stir-fry vegetables')
        # data = await collector.get_ingredient('butter')
        # data = await collector.get_ingredient('2/3 cup')
        print(data)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    asyncio.run(main())
