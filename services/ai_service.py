import requests

AI_URL = "http://127.0.0.1:5001/predict-issue"

def get_ai_caption(image_path):
    with open(image_path, "rb") as img:
        response = requests.post(
            AI_URL,
            files={"image": img}
        )
    response.raise_for_status()
    return response.json()["caption"]
