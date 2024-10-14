import os
import base64
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Function to encode an image to base64 format
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Async function to send text or image to GPT-4 Vision or GPT-4 text completion
async def send_to_gpt(image_path=None, text=None, prompt=None, model="gpt-4o"):
    try:
        # If both image and text are provided, prioritize the image
        if image_path:
            # Encode the image as base64
            base64_image = encode_image(image_path)

            # Prepare the payload for the image-based API request
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000  # Adjust as needed
            }

            # Set up the request headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            # Send the request to the OpenAI API for image-based completion
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            # Raise an exception for unsuccessful requests
            response.raise_for_status()

            # Extract the content of the response
            response_json = response.json()
            total_tokens = response_json['usage']['total_tokens']
            print(f"Total tokens used: {total_tokens}")
            gpt_message_content = response_json['choices'][0]['message']['content']

            return gpt_message_content

        elif text:
            # If only text is provided, use the OpenAI chat completion API
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # Adjust model as needed
                messages=[
                    {"role": "system", "content": "You are good at logical aptitude or maths questions."},
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nQuestions: {text}"
                    }
                ]
            )

            # Calculate the total number of tokens used
            total_tokens = completion.usage.total_tokens   
            print(f"Total tokens used: {total_tokens}")
            # Return the response from GPT
            return completion.choices[0].message.content

    except Exception as e:
        print(f"Error processing with GPT: {e}")
        return "Failed to process input with GPT."
