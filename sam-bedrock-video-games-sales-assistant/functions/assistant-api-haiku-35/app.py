import json
import os
import uuid
from datetime import date, datetime
import requests

DOCUMENT_GENERATOR_URL = os.environ["DOCUMENT_GENERATOR_URL"]
QUESTION_ANSWERS_TABLE = os.environ["QUESTION_ANSWERS_TABLE"]

def get_size(string):
    return len(string.encode("utf-8"))

def generate_proposal(input_text):
    headers = {"Content-Type": "application/json"}
    print(f"Input text: {input_text}")
    try:
        # Parse the input_text JSON string to get requerimiento and cliente
        input_data = json.loads(input_text)
        json_payload = {
            "requerimiento": input_data.get("requerimiento", ""),
            "cliente": input_data.get("cliente", "")
        }
        
        print(f"Sending payload to {DOCUMENT_GENERATOR_URL}/generar_propuesta: {json_payload}")
        
        response = requests.post(f"{DOCUMENT_GENERATOR_URL}/generar_propuesta", headers=headers, json=json_payload, timeout=60)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content length: {len(response.text)}")
        
        response.raise_for_status()
        
        # Check if response has content
        if not response.text.strip():
            print("Empty response from Document Generator API")
            result = {"error": "Empty response from Document Generator API"}
            response_code = 500
        else:
            # Check if response is JSON or plain text
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                try:
                    result = response.json()
                    response_code = 200
                    print("Successfully parsed JSON response")
                except json.JSONDecodeError as json_err:
                    print(f"Invalid JSON response: {response.text}")
                    result = {"error": f"Invalid JSON response: {str(json_err)}"}
                    response_code = 500
            else:
                # Handle plain text response
                result = {"proposal": response.text}
                response_code = 200
                print(f"Successfully received plain text response of {len(response.text)} characters")
                
    except json.JSONDecodeError as e:
        print(f"Error parsing input JSON: {e}")
        result = {"error": "Invalid JSON format in inputText"}
        response_code = 400
    except requests.RequestException as e:
        print(f"Error calling Document Generator API: {e}")
        result = {"error": str(e)}
        response_code = 500
    
    return result, response_code

def generate_document(input_text):
    headers = {"Content-Type": "application/json"}
    print(f"Input text: {input_text}")
    try:
        # Parse the input_text JSON string to get prompt
        input_data = json.loads(input_text)
        json_payload = {
            "prompt": input_data.get("prompt", "")
        }
        
        print(f"Sending payload to {DOCUMENT_GENERATOR_URL}/generar_documento: {json_payload}")
        
        response = requests.post(f"{DOCUMENT_GENERATOR_URL}/generar_documento", headers=headers, json=json_payload, timeout=60)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content length: {len(response.text)}")
        
        response.raise_for_status()
        
        # Check if response has content
        if not response.text.strip():
            print("Empty response from Document Generator API")
            result = {"error": "Empty response from Document Generator API"}
            response_code = 500
        else:
            # Check if response is JSON or plain text
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                try:
                    result = response.json()
                    response_code = 200
                    print(f"Successfully parsed JSON response: {result}")
                except json.JSONDecodeError as json_err:
                    print(f"Invalid JSON response: {response.text}")
                    result = {"error": f"Invalid JSON response: {str(json_err)}"}
                    response_code = 500
            else:
                # Handle plain text response
                result = {"document": response.text}
                response_code = 200
                print(f"Successfully received plain text response of {len(response.text)} characters")
                
    except json.JSONDecodeError as e:
        print(f"Error parsing input JSON: {e}")
        result = {"error": "Invalid JSON format in inputText"}
        response_code = 400
    except requests.RequestException as e:
        print(f"Error calling Document Generator API: {e}")
        result = {"error": str(e)}
        response_code = 500
    
    return result, response_code

def lambda_handler(event, context):
    print(event)
    action_group = event.get("actionGroup")
    api_path = event.get("apiPath")
    input_text = event.get("inputText")
    promptSessionAttributes = event.get("promptSessionAttributes", {})

    if "queryUuid" in promptSessionAttributes:
        query_uuid = promptSessionAttributes["queryUuid"]
    else:
        query_uuid = str(uuid.uuid4())

    print("api_path: ", api_path)

    result = ""
    response_code = 200

    if api_path == "/runDocumentGenerator":
        for item in event["requestBody"]["content"]["application/json"]["properties"]:
            if item["name"] == "inputText":
                input_text = item["value"]
        result, response_code = generate_document(input_text)

    elif api_path == "/runProposalGenerator":
        for item in event["requestBody"]["content"]["application/json"]["properties"]:
            if item["name"] == "inputText":
                input_text = item["value"]
        result, response_code = generate_proposal(input_text)

    elif api_path == "/getCurrentDate":
        # Return the current date in YYYY/MM/DD format
        current_date = datetime.now().strftime("%Y/%m/%d")
        result = {"currentDate": current_date}

    else:
        response_code = 404
        result = {"error": f"Unrecognized api path: {action_group}::{api_path}"}

    response_body = {"application/json": {"body": result}}

    action_response = {
        "actionGroup": action_group,
        "apiPath": api_path,
        "httpMethod": event.get("httpMethod"),
        "httpStatusCode": response_code,
        "responseBody": response_body,
    }

    api_response = {"messageVersion": "1.0", "response": action_response}

    print(get_size(json.dumps(api_response)))

    return api_response