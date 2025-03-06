import spotipy, sys, json, os, pickle
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


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
        maxResults=50  # Set a limit for the number of results per request (adjust as needed)
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
    playlist = create_youtube_playlist(yt_service, playlist_name, playlist_desc)
    playlist_id = playlist["id"]

    total_tracks = sp.playlist_items(sys.argv[1], fields='total').get('total')
    for offset in range(total_tracks):
        artist = sp.playlist_items(sys.argv[1], offset=offset, fields='items.track.artists.name').get(
            'items')[0].get('track').get('artists')[0].get('name')
        song_name = sp.playlist_items(sys.argv[1], offset=offset, fields='items.track.name').get(
            'items')[0].get('track').get('name')

        video_id = search_video(f"{artist} {song_name}", yt_service)

        if video_id:
            # Check if the video is already added to the playlist
            if not check_if_video_exists_in_playlist(yt_service, playlist_id, video_id):
                add_video_to_playlist(yt_service, playlist_id, video_id)


if __name__ == "__main__":
    main()
