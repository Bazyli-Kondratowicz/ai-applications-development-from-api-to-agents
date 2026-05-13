import base64
from datetime import datetime

import requests

from commons.constants import OPENAI_API_KEY, OPENAI_HOST


# https://developers.openai.com/api/reference/resources/images/methods/edit
# ---
# Request (multipart/form-data, NOT json):
# curl -X POST "https://api.openai.com/v1/images/edits" \
#     -H "Authorization: Bearer $OPENAI_API_KEY" \
#     -F "model=gpt-image-1" \
#     -F "image=@logo.png" \
#     -F "prompt=Add magical sparkles and glowing aura around the logo"
# Response:
# {
#   "created": 1699900000,
#   "data": [
#     {
#       "b64_json": "Qt0n6ArYAEABGOhEoYgVAJFdt8jM79uW2DO..."
#     }
#   ]
# }


def main(model_name: str, image_path: str, prompt: str, **kwargs):
    url = OPENAI_HOST + "/v1/images/edits"
    headers = {"Authorization": "Bearer " + OPENAI_API_KEY}

    with open(image_path, "rb") as image_file:
        files = {"image": (image_path, image_file, "image/png")}
        data = {"model": model_name, "prompt": prompt, **kwargs}

        print({"url": url, "data": data, "files": list(files.keys())})

        response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    payload = response.json()
    image_base64 = payload["data"][0]["b64_json"]

    image_bytes = base64.b64decode(image_base64)
    filename = f"edited_{datetime.now()}.png"
    with open(filename, "wb") as f:
        f.write(image_bytes)

    print(f"Edited image saved as {filename}")


main(
    model_name="gpt-image-1",
    image_path="logo.png",
    prompt=(
        "Transform this DIALX Community logo by adding magical sparkles, "
        "glowing stars, and a soft mystical aura around the letters. "
        "Keep the original text and shape clearly readable."
    ),
)