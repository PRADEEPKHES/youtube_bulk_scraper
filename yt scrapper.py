import os
import openai
import requests
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from openpyxl import Workbook

def get_video_details(youtube, video_url):
    # Extract video ID from the URL
    video_id = video_url.split("v=")[-1]
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    if response["items"]:
        snippet = response["items"][0]["snippet"]
        title = snippet.get("title", "No Title")
        description = snippet.get("description", "No Description")
        thumbnail = snippet["thumbnails"]["high"]["url"]
        return title, description, thumbnail
    else:
        return None, None, None

def get_video_transcript(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    transcript = soup.find("div", {"id": "transcript"})
    return transcript.text if transcript else "Transcript not available"

def generate_summary_and_recipe(text, prompt_type="summary"):
    prompt = (
        f"Summarize this text briefly: {text}"
        if prompt_type == "summary"
        else f"Optimize this text as a professional recipe: {text}"
    )
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)

def save_to_excel(data):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "YouTube Data"
    headers = [
        "Serial No",
        "Thumbnail Image Link",
        "Video Title",
        "Video URL",
        "Brief Description",
        "Transcript/Subtitle",
        "Optimized Recipe",
    ]
    sheet.append(headers)

    for row in data:
        sheet.append(row)

    workbook.save("youtube_videos.xlsx")
    print("Data saved to youtube_videos.xlsx")

def main():
    # Get user inputs
    openai_api_key = input("Paste your OpenAI API key: ").strip()
    youtube_api_key = input("Paste your YouTube API key: ").strip()
    print("Paste your video URLs (one per line, up to 500), and type 'END' to finish:")
    
    video_urls = []
    while True:
        url = input().strip()
        if url.upper() == "END":
            break
        video_urls.append(url)

    # Initialize APIs
    openai.api_key = openai_api_key
    youtube = build("youtube", "v3", developerKey=youtube_api_key)

    # Process video URLs
    data = []
    for i, video_url in enumerate(video_urls, start=1):
        video_id = video_url.split("v=")[-1]
        print(f"Processing {i}/{len(video_urls)}: {video_url}")

        # Get video details
        title, description, thumbnail_url = get_video_details(youtube, video_url)
        if not title:
            print(f"Could not fetch details for {video_url}")
            continue

        # Get transcript and AI enhancements
        transcript = get_video_transcript(video_id)
        brief_description = generate_summary_and_recipe(title, prompt_type="summary")
        optimized_recipe = generate_summary_and_recipe(transcript, prompt_type="recipe")

        # Append data
        data.append([
            i,
            thumbnail_url,
            title,
            video_url,
            brief_description,
            transcript,
            optimized_recipe,
        ])

    # Save data to Excel
    save_to_excel(data)

if __name__ == "__main__":
    main()
