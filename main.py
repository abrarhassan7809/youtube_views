from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.support.wait import WebDriverWait
import time

# Your API key
API_KEY = "AIzaSyBJDTJSGAlIVziT1IjkJ01JjvpReBOz7LA"


def get_channel_id(video_url):
    parsed_url = urlparse(video_url)
    video_id = parse_qs(parsed_url.query).get("v")
    if video_id:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        video_response = youtube.videos().list(part="snippet", id=video_id[0]).execute()
        if "items" in video_response:
            channel_id = video_response["items"][0]["snippet"]["channelId"]
            return channel_id
        else:
            print("Video not found")
            return None
    else:
        print("Invalid video URL")
        return None


def get_all_videos(api_key, channel_id):
    youtube = build("youtube", "v3", developerKey=api_key)

    try:
        # Get the playlist ID of the uploaded videos
        uploads_playlist_response = youtube.channels().list(
            part="contentDetails",
            id=channel_id
        ).execute()

        # Ensure that the response contains items
        if "items" in uploads_playlist_response:
            playlist_id = uploads_playlist_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

            # Get all videos from the uploads playlist
            videos = []
            next_page_token = None
            while True:
                playlist_items_response = youtube.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()

                videos.extend(playlist_items_response["items"])

                next_page_token = playlist_items_response.get("nextPageToken")
                if not next_page_token:
                    break

            return videos
        else:
            print("No items found in the channel response.")
            return []
    except Exception as e:
        print("An error occurred:")
        print(e)
        return []


def watch_video(video_url):
    driver = webdriver.Chrome()
    driver.get(video_url)
    driver.maximize_window()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'video')))
    play_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ytp-play-button')))
    play_button.click()
    time.sleep(2)  # Adjust the wait time as needed
    driver.execute_script("document.querySelector('video').play()")
    time.sleep(60)  # Adjust the video playback duration as needed
    driver.quit()


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=8kc27tgNjsQ"
    channel_id = get_channel_id(video_url)
    if channel_id:
        all_videos = get_all_videos(API_KEY, channel_id)
        for index, video in enumerate(all_videos):
            video_id = video["snippet"]["resourceId"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(index, video_url)
            watch_video(video_url)
        print("All videos watched!")
    else:
        print("No videos found!")
