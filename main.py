# Importing all the necessary modules
import openai
import random
from PIL import Image, ImageDraw, ImageFont
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler
from time import sleep

# Placeholder for TikTokUploader import (adjust according to the library's documentation)
try:
    from tiktok_uploader import TikTokUploader
except ImportError:
    print("TikTokUploader library import failed. Verify installation or library structure.")

# Setting OpenAI API key
openai.api_key = "key???"

# Setting TikTok credentials
TIKTOK_USERNAME = "username????"
TIKTOK_PASSWORD = "password???"

# Setting directory for temporary files
TEMP_DIR = 'temp_files'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


# Function to get the facts and tips
def get_coding_tip():
    prompt = "Give me an important coding tip or fact that is engaging and educational."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]


# Function to fetch the background image
def fetch_background_image():
    keywords = ["coding", "technology", "abstract", "programming"]
    keyword = random.choice(keywords)

    url = f"http://source.unsplash.com/1024x1024/?{keyword}"
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        file_path = os.path.join(TEMP_DIR, "background.jpg")
        with open(file_path, "wb") as file:
            file.write(response.content)

        return file_path
    else:
        print(f"Failed to fetch background image. HTTP Status: {response.status_code}")
        return None


# Function to create a video with text overlay
def create_video_with_text(text, background_image_path):
    output_image_path = os.path.join(TEMP_DIR, "output.jpg")

    # Try to locate a system font dynamically
    try:
        font_path = "arial.ttf"  # Adjust to a valid font path if necessary
        font = ImageFont.truetype(font_path, 40)
    except IOError:
        from PIL import ImageFont
        font_path = ImageFont.load_default()
        font = font_path

    # Open the background image
    try:
        img = Image.open(background_image_path)
        draw = ImageDraw.Draw(img)

        # Choose font size dynamically
        font_size = int(img.size[0] * 0.05)
        font = ImageFont.truetype(font_path, font_size)

        # Add text overlay
        text_width, text_height = draw.textsize(text, font=font)
        x = (img.width - text_width) / 2
        y = (img.height - text_height) / 2

        draw.text((x, y), text, font=font, fill="white", align="center")
        img.save(output_image_path)
    except Exception as e:
        print(f"Failed to create video with text: {e}")
        return None

    return output_image_path


# Function to post the video on TikTok
def post_on_tiktok(video_path):
    try:
        uploader = TikTokUploader(TIKTOK_USERNAME, TIKTOK_PASSWORD)
        uploader.login()  # Explicit login
        caption = "Here's a useful coding tip for you! #coding #programming #learn"
        uploader.upload(video_path, caption)
    except Exception as e:
        print(f"Failed to post on TikTok: {e}")


# Main function to automate the process
def automate_posting():
    try:
        print("Fetching coding tip...")
        tip = get_coding_tip()

        print("Fetching background image...")
        background_image_path = fetch_background_image()
        if not background_image_path:
            print("Background image fetch failed. Skipping posting.")
            return

        print("Creating video with text overlay...")
        video_path = create_video_with_text(tip, background_image_path)
        if not video_path:
            print("Video creation failed. Skipping posting.")
            return

        print("Posting on TikTok...")
        post_on_tiktok(video_path)
        print("Posted Successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")


# Schedule the bot to run every 2 days
scheduler = BackgroundScheduler()
scheduler.add_job(automate_posting, 'interval', days=2)
scheduler.start()

print("Bot is running. Press Ctrl+C to exit.")

# Keeping the script running
try:
    while True:
        sleep(1)  # Prevent CPU overuse
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
