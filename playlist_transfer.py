import spotipy
import sys
import json
import os
import pickle
import sqlite3
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Set up the SQLite database
def setup_db():
    conn = sqlite3.connect('video_cache.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS video_cache (
                        artist TEXT,
                        song_name TEXT,
                        video_id TEXT,
                        PRIMARY KEY (artist, song_name))''')
    conn.commit()
    return conn, cursor

def get_cached_video_id(cursor, artist, song_name):
    cursor.execute("SELECT video_id FROM video_cache WHERE artist=? AND song_name=?", (artist, song_name))
    result = cursor.fetchone()
    return result[0] if result else None

def cache_video(cursor, artist, song_name, video_id):
    cursor.execute("INSERT OR REPLACE INTO video_cache (artist, song_name, video_id) VALUES (?, ?, ?)",
                   (artist, song_name, video_id))
    cursor.connection.commit()

def search_video(query, yt_service):
    response = yt_service.search().list(part='snippet', maxResults=1, q=query).execute()
    return response['items'][0]['id']['videoId'] if 'items' in response else None

def load_credentials():
    try:
        with open("credentials.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("File credentials.json not found.")
        sys.exit()

def load_token():
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            return pickle.load(token)
    return None

def refresh_or_get_new_token(credentials):
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json', scopes=['https://www.googleapis.com/auth/youtube']
        )
        flow.run_local_server(port=8080, prompt='consent')
        credentials = flow.credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return credentials

def get_spotify_playlist_info(playlist_url, sp):
    playlist_name = sp.playlist(playlist_url, fields='name').get('name')
    playlist_desc = sp.playlist(playlist_url, fields='description').get('description')
    return playlist_name, playlist_desc

def create_youtube_playlist(yt_service, playlist_name, playlist_desc):
    return yt_service.playlists().insert(
        part='snippet,status',
        body={
            "snippet": {"title": playlist_name, "description": playlist_desc},
            "status": {"privacyStatus": "private"}
        }
    ).execute()

def add_video_to_playlist(yt_service, playlist_id, video_id):
    yt_service.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id}
            }
        }
    ).execute()

def check_if_video_exists_in_playlist(yt_service, playlist_id, video_id):
    response = yt_service.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    ).execute()

    # Check if the video is already in the playlist
    for item in response['items']:
        if item['snippet']['resourceId']['videoId'] == video_id:
            return True
    return False

def main():
    if len(sys.argv) <= 1:
        print("Usage: playlist_transfer.py playlist_url ")
        sys.exit()

    credentials_data = load_credentials()

    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=credentials_data.get('client_id'), client_secret=credentials_data.get('client_secret')
    ))

    token = load_token()
    credentials = refresh_or_get_new_token(token)

    yt_service = build('youtube', 'v3', credentials=credentials)

    playlist_name, playlist_desc = get_spotify_playlist_info(sys.argv[1], sp)
    playlist_id = 0
    yt_id = sys.argv[2] if len(sys.argv) >= 2 else False
    if yt_id != False:
        print(f"Using provided YouTube ID: {yt_id}")
        playlist_id = yt_id
    else:
        # Create a new YouTube playlist
        print(f"Creating new YouTube playlist: {playlist_name}")
        playlist = create_youtube_playlist(yt_service, playlist_name, playlist_desc)
        playlist_id = playlist["id"]

    conn, cursor = setup_db()

    total_tracks = sp.playlist_items(sys.argv[1], fields='total').get('total')
    for offset in range(total_tracks):
        artist = sp.playlist_items(sys.argv[1], offset=offset, fields='items.track.artists.name').get(
            'items')[0].get('track').get('artists')[0].get('name')
        song_name = sp.playlist_items(sys.argv[1], offset=offset, fields='items.track.name').get(
            'items')[0].get('track').get('name')

        print(song_name)
        # Try to get cached video ID
        cached_video_id = get_cached_video_id(cursor, artist, song_name)
        if cached_video_id:
            video_id = cached_video_id
        else:
            video_id = search_video(f"{artist} {song_name}", yt_service)
            if video_id:
                # Cache the result
                cache_video(cursor, artist, song_name, video_id)
                
        if video_id:
            # Check if the video is already added to the playlist
            if not check_if_video_exists_in_playlist(yt_service, playlist_id, video_id):
                print("adding track")
                add_video_to_playlist(yt_service, playlist_id, video_id)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()

