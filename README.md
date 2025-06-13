## Spotipy2YTMusic Playlists

Dirty and quick script in Python to transfer Spotify playlists to Youtube Playlists

## Requirements

All the requirements are listed in the requirements.txt, use `python3 -m pip install -r requirements.txt` to install them.

## Credentials

Spotify Credentials are needed in a separate file named `credentials.json` following this structure:

```
{
    "client_id":"your_client_id_here",
    "client_secret":"your_client_secret_id_here"
}
```
Also `client_secrets.json` is neeed which is taken from youtube API,for more info visit [this link](https://developers.google.com/identity/protocols/oauth2)

## Syntax:

```
	python3 playlist_transfer.py [playlist_url] [youtube_playlist_id] 

```
The `youtube_playlist_id` is optional
