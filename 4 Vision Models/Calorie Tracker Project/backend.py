"""
backend.py

Backend of the Calorie Tracker project.
Contains all the logic for connecting with OpenAI Vision to analyze food images
and return structured JSON with nutritional information.

Loads the key from .env (OPENAI_API_KEY).
"""

import os
import io
import base64
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import json

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise EnvironmentError("OPENAI_API_KEY not found in .env file")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

def encode_image_to_base64(image_path_or_pil):
    """
    Encodes an image to base64 to send to the OpenAI API.

    Parameters:
        image_path_or_pil (str | PIL.Image.Image): path to file or PIL image.
    Returns:
        str: base64 string of the image.
    """
    if isinstance(image_path_or_pil, str):
        if not os.path.exists(image_path_or_pil):
            raise FileNotFoundError(f"Image file not found at: {image_path_or_pil}")
        with open(image_path_or_pil, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    elif isinstance(image_path_or_pil, Image.Image):
        buffer = io.BytesIO()
        image_format = image_path_or_pil.format or "JPEG"
        image_path_or_pil.save(buffer, format=image_format)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    else:
        raise ValueError("Input must be a file path (str) or a PIL Image object.")

def query_openai_vision(client, image, prompt, model="gpt-4o", max_tokens=300):
    """
    Calls the OpenAI Vision model with an image and a prompt.

    Args:
        client: OpenAI client already initialized.
        image: PIL.Image.Image to analyze.
        prompt: string with the structured prompt.
        model: model to use (default: gpt-4o).
        max_tokens: maximum response tokens.

    Returns:
        str: model response (JSON as string).
    """
    base64_image = encode_image_to_base64(image)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content

# Structured prompt from notebook
structured_nutrition_prompt = """
# Nutritional Analysis Task

## Context
You are a nutrition expert analyzing food images to provide accurate nutritional information.

## Instructions
Analyze the food item in the image and provide estimated nutritional information based on your knowledge.

## Input
- An image of a food item

## Output
Provide the following estimated nutritional information for a typical serving size or per 100g:
- food_name (string)
- serving_description (string, e.g., '1 slice', '100g', '1 cup')
- calories (float)
- fat_grams (float)
- protein_grams (float)
- confidence_level (string: 'High', 'Medium', or 'Low')

**IMPORTANT:** Respond ONLY with a single JSON object containing these fields. Do not include any other text, explanations, or apologies. The JSON keys must match exactly: "food_name", "serving_description", "calories", "fat_grams", "protein_grams", "confidence_level". If you cannot estimate a value, use `null`.
"""

def analyze_image(image):
    """
    Analyzes a food image with OpenAI Vision and returns a dict with nutritional results.

    Parameters:
        image (PIL.Image.Image | str): image to analyze (PIL or path).

    Returns:
        dict: parsed JSON result or error.
    """
    if isinstance(image, str):
        image = Image.open(image)

    result_str = query_openai_vision(client, image, structured_nutrition_prompt)

    import re
    try:
        # First try to extract JSON between ``` ```
        fenced = re.search(r"```(?:json)?(.*?)```", result_str, re.DOTALL | re.IGNORECASE)
        if fenced:
            json_str = fenced.group(1).strip()
            return json.loads(json_str)

        # If not, look for any { ... } block
        match = re.search(r"\{.*\}", result_str, re.DOTALL)
        if match:
            return json.loads(match.group(0))

        return {"error": "No valid JSON found in response", "raw_output": result_str}
    except Exception as e:
        return {"error": f"Could not parse model response: {e}", "raw_output": result_str}

if __name__ == "__main__":
    # Demo: load a sample image and show analysis
    sample_path = "images/pizza_slice.png"
    if os.path.exists(sample_path):
        print("Analyzing sample image...")
        result = analyze_image(sample_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Sample image not found. Run analyze_image(path) with your own image.")