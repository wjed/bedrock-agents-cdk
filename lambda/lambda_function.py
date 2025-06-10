import json
from bs4 import BeautifulSoup
import requests

"""
Input from Bedrock Agent looks like
{
    "messageVersion": "1.0",
    "agent": {
        "alias": "TSTALIASID",
    "name": "aws-cert-study-getter",
        "version": "DRAFT",
        "id": "HR4FHXL0RQ",
    },
    "sessionId": "855290146028435",
    "sessionAttributes": {},
    "promptSessionAttributes": {},
    "inputText": "What's a good study resource for IAM?",
    "apiPath": "/study",
    "requestBody": {
        "content": {
            "application/json": {
                "properties": [
                    {"name": "topicSearch", "type": "string", "value": "IAM"}
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
    print(f"Searching AWS for {search}")
    query = search.replace(" ", "+")
    # download the search results page
    search_url = f"https://aws.amazon.com/search/?searchQuery={query}"
    response = requests.get(search_url, headers={"User-Agent": "curl/7.64.1"})
    text = response.text
    # grab the URL for the first search result
    soup = BeautifulSoup(text, "html.parser")
    link = soup.find("a")
    resource = link["href"] if link else None
    # if resource is undefined, return an error
    if resource is None:
        result = {
            "url": "No resource found",
            "title": "No resource found",
            "summary": "No resource found",
        }
    else:
        # download the html and then parse out the title and summary. Pretend that we're curl so that we get past any blocks
        response = requests.get(resource, headers={"User-Agent": "curl/7.64.1"})
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else ""
        paragraphs = [p.text.strip() for p in soup.find_all("p")][:5]
        summary = " ".join(paragraphs)

        # Execute your business logic here. For more information, refer to: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html
        result = {
            "url": resource,
            "title": title,
            "summary": summary,
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
