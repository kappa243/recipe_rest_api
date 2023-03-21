import json
import os

with open('app/settings.json') as f:
    settings = json.load(f)

    settings['api']['edamam']['url'] = os.environ.get('EDAMAM_URL')
    settings['api']['edamam']['app_id'] = os.environ.get('EDAMAM_APP_ID')
    settings['api']['edamam']['app_key'] = os.environ.get('EDAMAM_APP_KEY')

    settings['api']['themealdb']['url'] = os.environ.get('THEMEALDB_URL')

    settings['api']['tasty']['url'] = os.environ.get('TASTY_URL')
    settings['api']['tasty']['api_key'] = os.environ.get('TASTY_API_KEY')
    settings['api']['tasty']['api_host'] = os.environ.get('TASTY_API_HOST')

with open('app/settings.json', 'w') as f:
    json.dump(settings, f)
    
    
