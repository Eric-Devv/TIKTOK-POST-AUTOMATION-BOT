# Imorting all the nessesary modules:

import openai
import random
from PIL import Image, ImageDraw, ImageFont
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler
from tiktok_uploader import TikTokUploader

# setting openai API key.
openai.api_key = "key???"

# setting TikTok credentials(api wrapper or sdk)
TIKTOK_USERNAME = "username????"
TIKTOK_PASSWORD = "password???"

# setting directory for temporary files.
TEMP_DIR = 'temp_files'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


# function to get the facts and tips
def get_coding_tip():
    prompt = "give me an important coding tip or fact that is engaging and educational."
    response = openai.ChatCompletion.create(
        model = "gpt-4",
        messages = [{"role":"user", "content":prompt}]
    )
    return response["choices"][0]["message"]["content"]


# function fetch the background image
def fetch_background_image():
    keywords = ["coding", "technology", "abstract", "programming"]
    keyword = random.choice(keywords)

    url = f"http://source.unsplash.com/1024x1024/?{keyword}"
    response = requests.get(url, stream = True)

    if response.status_code == 200:
        file_path = os.path.join(TEMP_DIR, "background.jpg")
        with open(file_path, "wb") as file:
            file.write(response.content)
        
        return file_path
    return None


# function to create a video with text overlay.
def create_video_with_text(text, background_image_path):
    output_image_path = os.path.join(TEMP_DIR, "output.jpg")
    font_path = "arial.ttf"

    #open the background image
    img = Image.open(background_image_path)
    draw = ImageDraw.Draw(img)

    #choose font size dynamically
    font_size = int(img.size[0] * 0.05)
    font = ImageFont.truetype(font_path, font_size)

    # add text overlay
    text_width, text_height = draw.textsize(text, font=font)
    x = (img.width - text_width) /2
    y = (img.height - text_height) /2

    draw.text((x, y), text, font=font, fill="white", align = "center")
    img.save(output_image_path)
    return output_image_path


# function to post the video on tiktok
def post_on_tiktok(video_path):
    uploader = TikTokUploader(TIKTOK_USERNAME, TIKTOK_PASSWORD)

    caption = "here's a useful coding tip for you! #coding #programming #learn"
    uploader.upload(video_path, caption)

# main function to automate the process
def automate_posting():
    try:
        print("Fetching coding tip...")
        tip = get_coding_tip()
        print("Fetching background image...")
        background_image_path = fetch_background_image()
        print("Creating video with text overlay...")
        video_path = create_video_with_text(tip, background_image_path)
        print("Posting on TikTok...")
        post_on_tiktok(video_path)
        print("Posted Successfully!")
    except Exception as e:
        print("Error occured: {e}")

# Schedule the bot to run every 2days
scheduler = BackgroundScheduler()
scheduler.add_job(automate_posting, 'interval', days=2)
scheduler.start()

print("Bot is running. Press ctrl+c to exit.")

# keeping the script running
try:
    while True:
        pass
except(KeyboardInterrupt, SystemExit):
    scheduler.shutdown()