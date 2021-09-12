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

#from pytube import YouTube
#import pytube.request
#import pytube.extract

credentials = None
offset = 0


# token.pickle stores the user's credentials from previously successful logins
if os.path.exists('token.pickle'):
    print('Loading Credentials From File...')
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)

'''
try:
    with open("credentials.json", "r") as credentials:
        cred_json = json.load(credentials)

except FileNotFoundError:

    print(File credentials.json not found, please create one with the following syntax:
{
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_id_here",
    "youtube_api": "your_youtube_api_key_here"
}

)
sys.exit()

if len(sys.argv) <= 1:
print("Usage: playlist_transfer.py playlist_url ")
sys.exit()
'''
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


#yt_service = build('youtube', 'v3',)
'''
client_credentials_manager = SpotifyClientCredentials(client_id=cred_json.get(
    'client_id'), client_secret=cred_json.get('client_secret'))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

total = sp.playlist_items(sys.argv[1], fields='total').get('total')


while offset < total:
    if offset == total:
        break
    # Get artist name and song name using the spotify API

    artist = sp.playlist_items(sys.argv[1], offset=offset, fields='items.track.artists.name').get(
        'items')[0].get('track').get('artists')[0].get('name')
    song_name = sp.playlist_items(sys.argv[1], offset=offset, fields='items.track.name').get(
        'items')[0].get('track').get('name')

offset += 1

yt_link = VideosSearch(f"{artist} {song_name}", limit=1).result().get(
    'result')[0].get('link')
'''
