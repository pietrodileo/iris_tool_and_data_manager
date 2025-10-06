import requests
import json

actions = {
    "get_response": "chat",
    "get_stream": "chat",
    "get_models": "tags"
}

class OllamaRequest:
    def __init__(self, api_url:str):
        self.api_url = api_url

    def get_response(self, content, model, format:str | None = None) -> str:
        # define payload
        """
        Get a response from the Ollama API.

        This method sends a request to the Ollama API with the
        model name and a message with the role 'user' and the
        content 'Hello, how are you?'. It then prints out the
        response from the API, which is a JSON object with the
        message content.

        :return: None
        """
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "stream": False
        }

        if format:
            payload["format"] = format

        # Send HTTP request to the ollama API
        response = requests.post(self.api_url+"/"+actions["get_response"], json=payload, stream=False)

        if response.status_code != 200:
            raise Exception(f"Ollama error {response.status_code}: {response.text}")
        try:
            return response.json()
        except Exception as e:
            raise Exception(f"Invalid JSON from Ollama: {e}\nResponse text: {response.text}")
            
    def get_stream(self, content, model, format:str | None = None):
        # define payload
        """
        Get a response from the Ollama API.

        This method sends a request to the Ollama API with the
        model name and a message with the role 'user' and the
        content 'Hello, how are you?'. It then prints out the
        response from the API, which is a JSON object with the
        message content.

        :return: None
        """
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }

        if format is not None:
            payload["format"] = format

        # Send HTTP request to the ollama API
        response = requests.post(self.api_url, json=payload, stream=True)

        # Check if response is ok
        if response.status_code == 200:
            # print("Streaming response from Ollama API:")
            for line in response.iter_lines(decode_unicode=True):
                if line: # ignore empty lines
                    try:
                        json_data = json.loads(line)
                        if "message" in json_data and "content" in json_data["message"]:
                            yield json_data["message"]["content"]
                    except json.JSONDecodeError as e:
                        yield f"Error decoding JSON: {e}. \nFailed to parse line: {line}"
        else:
            yield f"Error: {response.status_code} - {response.text}"
            
    def __repr__(self) -> str:
        return f"OllamaRequest(api_url={self.api_url})"
            
    def get_models(self) -> list[str]:
        response = requests.get(self.api_url+"/"+actions["get_models"])
        if response.status_code == 200:
            json = response.json()
            models = json['models']
            models_list = []
            for model in models:
                models_list.append(model["name"])
            return models_list
        else:
            raise Exception(f"Error getting models: {response.status_code} - {response.text}")