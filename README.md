## Spotipy2YTMusic Playlists

Dirty and quick script in Python to transfer Spotify playlists to Youtube Playlists, [used old code as base](https://github.com/Klairm/spotipy-downloader).

## Requirements

All the requirements are listed in the requirements.txt, use `python3 -m pip install -r requirements.txt` to install them.

## Credentials

Credentials are needed in a separate file named `credentials.json` following this structure:

```
{
    "client_id":"your_client_id_here",
    "client_secret":"your_client_secret_id_here"
}
```
Also 0auth is needed from google API, for more info visit [this link](https://developers.google.com/identity/protocols/oauth2)

## Syntax:

```
	python3 playlist_transfer.py [playlist_url]

```
