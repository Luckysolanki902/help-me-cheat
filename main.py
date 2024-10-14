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
from lib.gemini_utils import send_to_gemini  # Ensure this is async
from lib.gpt_utils import send_to_gpt  # Ensure this is async
from lib.twilio_utils import send_whatsapp_message

# Load environment variables from .env file
load_dotenv()

# Set the root directory where screenshots will be saved
root_directory = r"D:\Desktop\cheat"
image_directory = os.path.join(root_directory, "images")
os.makedirs(image_directory, exist_ok=True)  # Ensure the images folder exists

# Global variable to control the main loop
exit_program = False
unstop_mode = True

if(unstop_mode):
    text_process_prompt = (
        "First solve the question accurately step by step and when the question is solved, "
        "provide a answer of that the question in the following format in the end: "
        "'AptitudeCtrs' and then the correct answer from new line: "
        "*Q<number>* (<option like a, b, c>) <answer>."
    )
else:
        text_process_prompt = (
        "First solve the question/questions accurately step by step and when that/all is/are solved, "
        "provide a summary of all the question/questions in the following format in the end: "
        "'AptitudeCtrs' and then the list of correct answers from new line: "
        "*Q<number>* (<option like a, b, c>) <answer>."
    )

async def generate_random_string(length=6):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

async def capture_screenshot():
    try:
        # Generate the screenshot file path
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        random_suffix = await generate_random_string()
        filename = f"screenshot_{timestamp}_{random_suffix}.png"
        filepath = os.path.join(image_directory, filename)

        # Take a screenshot using PyAutoGUI
        screenshot = pyautogui.screenshot()

        # Save the screenshot to the file path
        screenshot.save(filepath)
        print(f"Screenshot saved at: {filepath}")

        return filepath
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None

async def capture_extract_copy_text_send():
    screenshot_path = None
    try:
        # Capture the screenshot
        screenshot_path = await capture_screenshot()

        # Check if screenshot was captured
        if not screenshot_path or not os.path.exists(screenshot_path):
            raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")

        print("Ctrl+I detected. Extracting text and processing...")

        # Extract text from the image using OCR
        extracted_text = await extract_text_from_image(screenshot_path)

        # Copy the extracted text to the clipboard
        pyperclip.copy(extracted_text)

        # Prompt for Ctrl+M use case


        # Run both GPT and Gemini tasks asynchronously: text goes to GPT, image goes to Gemini
        gemini_task = send_to_gemini(screenshot_path, text_process_prompt)  # Image sent to Gemini
        gpt_task = send_to_gpt(text=extracted_text, prompt=text_process_prompt, model="gpt-4o")  # Text sent to GPT

        # Await both tasks to complete
        gemini_response, gpt_response = await asyncio.gather(gemini_task, gpt_task)

        # Regex to extract the final answer part from both GPT and Gemini responses
        pattern = r"AptitudeCtrs([\s\S]*)"
        
        # Extract answers from GPT response
        gpt_match = re.search(pattern, gpt_response)
        gpt_answer = gpt_match.group(1).strip() if gpt_match else gpt_response.strip()[-100:]

        # Extract answers from Gemini response
        gemini_match = re.search(pattern, gemini_response)
        gemini_answer = gemini_match.group(1).strip() if gemini_match else gemini_response.strip()[-100:]

        # Combine both answers in the final message
        final_message = f"GPT: {gpt_answer}\n\nGemini: {gemini_answer}"
        send_whatsapp_message(final_message)

    except Exception as e:
        print(f"Error in capture_extract_copy_text_send: {e}")

    finally:
        # Clean up: remove the screenshot file if it exists
        if screenshot_path and os.path.exists(screenshot_path):
            os.remove(screenshot_path)

async def capture_extract_copy_gemini_gpt_send():
    screenshot_path = None
    try:
        # Capture the screenshot
        screenshot_path = await capture_screenshot()

        # Check if screenshot was captured
        if not screenshot_path or not os.path.exists(screenshot_path):
            raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")

        print("Ctrl+M detected. Processing the screenshot...")

        # Extract text from the image using OCR
        extracted_text = await extract_text_from_image(screenshot_path)

        # Copy the extracted text to clipboard
        pyperclip.copy(extracted_text)
        
        # Run both GPT and Gemini tasks asynchronously, passing the image to both
        gemini_task = send_to_gemini(screenshot_path, text_process_prompt)  # Image sent to Gemini
        gpt_task = send_to_gpt(image_path=screenshot_path, prompt=text_process_prompt, model="gpt-4o-mini")  # Image sent to GPT

        # Await for both tasks to complete
        gemini_response, gpt_response = await asyncio.gather(gemini_task, gpt_task)

        # Regex to extract the final answer part from both GPT and Gemini responses
        pattern = r"AptitudeCtrs([\s\S]*)"
        # Extract answers from GPT response
        gpt_match = re.search(pattern, gpt_response)
        gpt_answer = gpt_match.group(1).strip() if gpt_match else gpt_response.strip()[-100:]

        # Extract answers from Gemini response
        gemini_match = re.search(pattern, gemini_response)
        gemini_answer = gemini_match.group(1).strip() if gemini_match else gemini_response.strip()[-100:]

        # Combine both answers in the final message
        final_message = f"GPT: {gpt_answer}\n\nGemini: {gemini_answer}"
        send_whatsapp_message(final_message)

    except Exception as e:
        print(f"Error in capture_extract_copy_gemini_gpt_send: {e}")

    finally:
        # Clean up: remove the screenshot file if it exists
        if screenshot_path and os.path.exists(screenshot_path):
            os.remove(screenshot_path)

async def check_hotkeys():
    global exit_program
    try:
        # Check if the Ctrl+I key combination is pressed
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('i'):
            await capture_extract_copy_text_send()
            await asyncio.sleep(2)  # Wait for 2 seconds before detecting next input
            
        # Check if the Ctrl+M key combination is pressed
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('m'):
            await capture_extract_copy_gemini_gpt_send()
            await asyncio.sleep(2)  # Wait for 2 seconds before detecting next input
            
        cursor_x, cursor_y = pyautogui.position()
        screen_width, screen_height = pyautogui.size()

        # Define the bottom-right corner area (last 10% of width and height)
        if cursor_x > screen_width * 0.9 and cursor_y > screen_height * 0.9:
            await capture_extract_copy_text_send()
            await asyncio.sleep(2)  # Wait for 2 seconds before detecting next input

        # Define the bottom-left corner area
        if cursor_x < screen_width * 0.1 and cursor_y > screen_height * 0.9:
            await capture_extract_copy_text_send()
            await asyncio.sleep(2)  # Wait for 2 seconds before detecting next input            

    except Exception as e:
        print(f"Error checking hotkeys: {e}")
    finally:
        # Small delay to prevent excessive CPU usage
        await asyncio.sleep(0.05)

async def main():
    print("Started Key Detection for solving Quiz")
    while not exit_program:
        await check_hotkeys()
    print("Exiting program...")

# Run the asynchronous event loop
asyncio.run(main())
