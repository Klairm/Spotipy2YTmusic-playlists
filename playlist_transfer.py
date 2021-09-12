import spotipy
import sys
import json
import os
import re
import pickle
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

credentials = None
offset = 0


if len(sys.argv) <= 1:
    print("Usage: playlist_transfer.py playlist_url ")
    sys.exit()
try:
    with open("credentials.json", "r") as credentials:
        cred_json = json.load(credentials)

except FileNotFoundError:

    print('''File credentials.json not found, please create one with the following syntax:
          {
              "client_id": "your_client_id_here",
              "client_secret": "your_client_secret_id_here",
              "youtube_api": "your_youtube_api_key_here"
          }

          ''')
    sys.exit()


# Used this snippets for the 0auth https://gist.github.com/CoreyMSchafer/ea5e3129b81f47c7c38eb9c2e6ddcad7
# token.pickle stores the user's credentials from previously successful logins
if os.path.exists('token.pickle'):
    print('Loading Credentials From File...')
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)
# If there are no valid credentials available, then either refresh the token or log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing Access Token...')
        credentials.refresh(Request())
    else:
        print('Fetching New Tokens...')
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=[
                'https://www.googleapis.com/auth/youtube'
            ]
        )

        flow.run_local_server(port=8080, prompt='consent',
                              authorization_prompt_message='')
        credentials = flow.credentials

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)


client_credentials_manager = SpotifyClientCredentials(client_id=cred_json.get(
    'client_id'), client_secret=cred_json.get('client_secret'))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

yt_service = build('youtube', 'v3', credentials=credentials)

playlist_name = sp.playlist(sys.argv[1], fields='name').get('name')
playlist_desc = sp.playlist(
    sys.argv[1], fields='description').get('description')


playlists_insert_response = yt_service.playlists().insert(
    part='snippet,status',
    body={
        "snippet": {
            "title": playlist_name,
            "description": playlist_desc
        },
        "status": {
            "privacyStatus": "private"
        }}
).execute()


playlist_id = playlists_insert_response["id"]
total = sp.playlist_items(sys.argv[1], fields='total').get('total')


while offset < total:
    if offset == total:
        break
    # Get artist name and song name using the spotify API

    artist = sp.playlist_items(sys.argv[1], offset=offset, fields='items.track.artists.name').get(
        'items')[0].get('track').get('artists')[0].get('name')
    song_name = sp.playlist_items(sys.argv[1], offset=offset, fields='items.track.name').get(
        'items')[0].get('track').get('name')
    video_id = VideosSearch(f"{artist} {song_name}",
                            limit=1).result().get('result')[0].get('id')

    print(f"Adding {artist} {song_name} to playlist...")
    playlist_add_response = yt_service.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    ).execute()

    offset += 1
