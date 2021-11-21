from __future__ import print_function

import json
import re
import speech_recognition as sr
import spoonacular
from googletrans import Translator, constants
from os import getenv
from random import choice

API_KEY = getenv('SPOONACULAR_API_KEY')
CDN_BASE_URL = 'https://spoonacular.com/cdn/'

cuisines = ['African',
            'American',
            'British',
            'Cajun',
            'Caribbean',
            'Chinese',
            'Eastern European',
            'European',
            'French',
            'German',
            'Greek',
            'Indian',
            'Irish',
            'Italian',
            'Japanese',
            'Jewish',
            'Korean',
            'Latin American',
            'Mediterranean',
            'Mexican',
            'Middle Eastern',
            'Nordic',
            'Southern',
            'Spanish',
            'Thai',
            'Vietnamese']


# ingredients, equipment,

def recognize():
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("""
African
American
British
Cajun
Caribbean
Chinese
Eastern European
European
French
German
Greek
Indian
Irish
Italian
Japanese
Jewish
Korean
Latin American
Mediterranean
Mexican
Middle Eastern
Nordic
Southern
Spanish
Thai
Vietnamese
        """)
        print("Say 'Find me a recipe'!")
        print("- from the Italian cuisine")
        print("- with tomato, rice and chicken")
        audio = r.listen(source)

    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        result = r.recognize_google(audio, language='nl-BE')
        print(f'Google Speech Recognition thinks you said "{result}"')
        return result
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def parse(keyword):
    print(keyword)
    params = {}

    words = re.sub(r'[^\w\s_]+', '', keyword).strip().split()
    parse_cuisine(params, words)
    query_index = words.index('with') + 1
    query_string = " ".join(words[query_index:])
    params['query'] = query_string
    if 'vegetarian' in keyword:
        params['diet'] = 'vegetarian'
    params['intolerances'] = 'peanut'
    print(params)
    return params


def parse_cuisine(params, words):
    for cuisine in cuisines:
        if cuisine.lower() in words:
            params['cuisine'] = cuisine


def format_recipe(resp_json):
    ingredients = "\n".join(
        [f"\t{index + 1}. {item['originalString']}" for index, item in enumerate(resp_json['extendedIngredients'])])
    steps = "\n".join(
        [f"\t{index + 1}. {item['step']}" for index, item in enumerate(resp_json['analyzedInstructions'][0]['steps'])])
    return (
        f"RECIPE: {resp_json['title']}\n"
        f"{'ingredients'.upper()}\n"
        f"{ingredients}\n"
        f"{'preparation'.upper()}\n"
        f"{steps}\n"
        f"image: {resp_json['image']}\n"
        f"source: {resp_json['sourceUrl']}"
    )


def search_recipes(keyword):
    params = parse(keyword)
    api = spoonacular.API(API_KEY)
    try:
        api_response = api.search_recipes_complex(**params)
        print(api_response.request.url)
        # print(json.dumps(api_response.json(), indent=3, sort_keys=True))
        recipe_id = choice(api_response.json()['results'])['id']
        # print(recipe_id)
        recipe_resp = api.get_recipe_information(recipe_id, includeNutrition=False)
        print(recipe_resp.request.url)
        resp_json = recipe_resp.json()
        # print(json.dumps(resp_json, indent=3, sort_keys=True))
        print(format_recipe(resp_json))
        # print(recipe_resp.headers)
    except IndexError as ie:
        print("no recipes found")
    except RuntimeError as e:
        print("Exception when calling IngredientsApi->autocomplete_ingredient_search: %s\n" % e)


if __name__ == '__main__':
    term = recognize()
    # term = "find me a recipe from the italian cuisine with pork, mushrooms"
    # term = "Ik zoek een Recept uit de Mexicaanse keuken met kip, koriander en rijst"
    translation = Translator().translate(term, src='nl', dest='en')
    print(translation.text)
    search_recipes(translation.text.lower())
