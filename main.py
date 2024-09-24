import os
import asyncio
import keyboard
import pyautogui
import pyperclip
import re
import time
import random
import string
from dotenv import load_dotenv
from lib.extract_text_utils import extract_text_from_image
from lib.gemini_utils import send_to_gemini
from lib.twilio_utils import send_whatsapp_message

# Load environment variables from .env file
load_dotenv()

# Set the root directory where screenshots will be saved
root_directory = r"D:\Desktop\cheat"
image_directory = os.path.join(root_directory, "images")
os.makedirs(image_directory, exist_ok=True)

# Global variable to control the main loop
exit_program = False

async def generate_random_string(length=6):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

async def capture_screenshot():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    random_suffix = await generate_random_string()
    filename = f"screenshot_{timestamp}_{random_suffix}.png"
    filepath = os.path.join(image_directory, filename)
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    return filepath

async def capture_extract_copy_gemini_send():
    screenshot_path = None
    try:
        screenshot_path = await capture_screenshot()
        print("Ctrl+I detected. Starting to process the screenshot...")

        extracted_text = await extract_text_from_image(screenshot_path)
        pyperclip.copy(extracted_text)

        code_solve_prompt = "Solve this question accurately and provide the correct option in the end, as the string 'Project AptitudeCtrs, final answer of the question is': and then the correct option"
        gemini_response = await send_to_gemini(screenshot_path, code_solve_prompt)

        # Regex to extract only the part starting from "Project AptitudeCtrs" and ending at the correct answer.
        pattern = r"(Project AptitudeCtrs, final answer of the question is.*)"
        match = re.search(pattern, gemini_response)

        if match:
            trimmed_response = match.group(1)
        else:
            trimmed_response = "Unable to find the answer in the response."

        trimmed_message = trimmed_response.replace('Project AptitudeCtrs, final answer of the question is:', '').strip()
        send_whatsapp_message(trimmed_message)

    except Exception as e:
        print(f"Error in capture_extract_copy_gemini_send: {e}")
    finally:
        if screenshot_path and os.path.exists(screenshot_path):
            os.remove(screenshot_path)

async def check_hotkeys():
    global exit_program
    try:
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('w'):
            print("Ctrl+W detected. Exiting the program...")
            exit_program = True
            return
        
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('i'):
            await capture_extract_copy_gemini_send()
    except Exception as e:
        print(f"Error checking hotkeys: {e}")
    finally:
        await asyncio.sleep(0.05)

async def main():
    print("Started Key Detection in Quiz Mode.")
    while not exit_program:
        await check_hotkeys()
    print("Exiting program...")

# Run the asynchronous event loop
asyncio.run(main())
