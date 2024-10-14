async def capture_extract_copy_gemini_gpt_send():
    screenshot_path = None
    try:
        # Capture the screenshot
        screenshot_path = await capture_screenshot()

        # Check if screenshot was captured
        if not screenshot_path or not os.path.exists(screenshot_path):
            raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")

        print("Ctrl+I detected. Processing the screenshot...")

        # Extract text from the image using Tesseract or another OCR tool
        extracted_text = await extract_text_from_image(screenshot_path)

        # Copy the extracted text to clipboard
        pyperclip.copy(extracted_text)

        # Prompt to solve the question
        quiz_solve_prompt = (
            "First solve the questions accurately step by step and when all are solved then in the end provide the summary of all questions - start with a text 'AptitudeCtrs\n' and then the list of correct answers in followring format"
            "in the following format: *Q<number>* (<option number like a, b, c>) <answer>, "
            "with each answer on a new line."
        )

    # Run both GPT and Gemini tasks asynchronously
        
        # Run both GPT and Gemini tasks asynchronously
        gemini_task = send_to_gemini(screenshot_path, quiz_solve_prompt)  # Ensure this is async
        gpt_task = send_to_gpt(screenshot_path, quiz_solve_prompt)  # Ensure this is async

        # Await for both tasks to complete
        gemini_response, gpt_response = await asyncio.gather(gemini_task, gpt_task)

        # Regex to extract the final answer part from both GPT and Gemini responses
        pattern = r"AptitudeCtrs: (.+)"  # Adjusted regex to match new prompt
        
        try:
            gemini_match = re.search(pattern, gemini_response)
            if gemini_match:
                gemini_answer = gemini_match.group(1).strip()
            else:
                raise ValueError("Gemini response did not contain expected format.")

        except Exception:
            gemini_answer = gemini_response.strip()[-100:]  # Extract last 50 characters if extraction fails

        try:
            gpt_match = re.search(pattern, gpt_response)
            if gpt_match:
                gpt_answer = gpt_match.group(1).strip()
            else:
                raise ValueError("GPT response did not contain expected format.")

        except Exception:
            gpt_answer = gpt_response.strip()[-100:]  # Extract last 50 characters if extraction fails

        # Remove 'AptitudeCtrs:' from both answers if present
        gemini_answer = gemini_answer.replace("AptitudeCtrs:", "").strip()
        gpt_answer = gpt_answer.replace("AptitudeCtrs:", "").strip()

        # Combine both answers in the final message
        final_message = f"GPT: {gpt_answer}\n\n\nGemini: {gemini_answer}"
        send_whatsapp_message(final_message)

    except Exception as e:
        print(f"Error in capture_extract_copy_gemini_gpt_send: {e}")

    finally:
        # Clean up: remove the screenshot file if it exists
        if screenshot_path and os.path.exists(screenshot_path):
            os.remove(screenshot_path)
