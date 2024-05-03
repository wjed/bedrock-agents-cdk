import json
from bs4 import BeautifulSoup
import requests

"""
Input from Bedrock Agent looks like
{
    "messageVersion": "1.0",
    "agent": {
        "alias": "TSTALIASID",
        "name": "budget-bytes-getter",
        "version": "DRAFT",
        "id": "HR4FHXL0RQ",
    },
    "sessionId": "855290146028435",
    "sessionAttributes": {},
    "promptSessionAttributes": {},
    "inputText": "What's a good recipe for pancakes?",
    "apiPath": "/recipe",
    "requestBody": {
        "content": {
            "application/json": {
                "properties": [
                    {"name": "recipeSearch", "type": "string", "value": "pancakes"}
                ]
            }
        }
    },
    "actionGroup": "action-group-quick-start-der93",
    "httpMethod": "GET",
    "parameters": [],
}
"""


def lambda_handler(event, context):
    # This is the format of the event object that is passed to the lambda function from Bedrock
    search = event["requestBody"]["content"]["application/json"]["properties"][0][
        "value"
    ]
    print(f"Searching on Budget bytes for {search}")
    query = search.replace(" ", "+").lower().replace("recipe", "")
    # download the search results page
    search_url = f"https://www.budgetbytes.com/?s={query}"
    response = requests.get(search_url, headers={"User-Agent": "curl/7.64.1"})
    text = response.text
    # grab the URL for the first search result
    soup = BeautifulSoup(text, "html.parser")
    # the links are in the class archive-post-listing
    recipe = soup.find("div", class_="archive-post-listing").find("a")["href"]
    # if recipe is undefined, return an error
    if recipe is None:
        result = {
            "url": "No recipe found",
            "ingredients": "No recipe found",
            "instructions": "No recipe found",
        }
    else:
        # download the html and then parse out the ingredients and instructions. Pretend that we're curl so that we get past cloudflare
        response = requests.get(recipe, headers={"User-Agent": "curl/7.64.1"})
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        ingredients = [
            ingredient.text
            for ingredient in soup.find_all("li", class_="wprm-recipe-ingredient")
        ]
        instructions = [
            instruction.text
            for instruction in soup.find_all("li", class_="wprm-recipe-instruction")
        ]

        # Execute your business logic here. For more information, refer to: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html
        result = {
            "url": recipe,
            "ingredients": ingredients,
            "instructions": instructions,
        }

    response_body = {"application/json": {"body": json.dumps(result)}}

    action_response = {
        "actionGroup": event["actionGroup"],
        "apiPath": event["apiPath"],
        "httpMethod": event["httpMethod"],
        "httpStatusCode": 200,
        "responseBody": response_body,
    }

    final_response = {
        "messageVersion": "1.0",
        "response": action_response,
    }
    print(f"Response: {final_response}")

    return final_response
