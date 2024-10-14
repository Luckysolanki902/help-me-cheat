import random
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Google Generative AI
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")
# Available models: 'gemini-1.5-pro', 'Gemini 1.0 Pro', 'gemini-1.5-flash'

async def send_to_gemini(image_path, prompt):
    try:
        myfile = genai.upload_file(path=image_path,
                            display_name=f"quiz_screenshot{random.randint(100000, 999999)}")
        result = model.generate_content([myfile, prompt])
        return result.text
    except Exception as e:
        print(f"Error processing image with Gemini AI: {e}")
        return "Failed to process image with Gemini AI."
