import requests
import base64
import os
import datetime
from dotenv import load_dotenv
from src.server.lib.api_error import ApiError

load_dotenv(dotenv_path=os.path.abspath('src/configs/.env'))

# Client ID assigned when application is registered
CLIENT_ID = os.environ.get('CLIENT_ID')
# Authorization code for requesting access tokens [TODO - do something about this]
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_URL = 'https://api.spotify.com/v1'


class SpotifyClient:
    token = ''
    token_expiration = None

    def __init__(self):
        self.request_access_token_client_auth_flow()

    def is_token_expired(self):
        """
        Does a simple timestamp comparison to check if the current access token is expired or not.
        """

        return self.token_expiration <= datetime.datetime.now()

    def extract_items_from_paging_obj(self, paging_obj, items):
        """
        Extracts all items from the given paging object. A paging object can contain links for
        retrieving items from additional pages and these items should be included in the returned
        list.

        API Reference: https://developer.spotify.com/documentation/web-api/reference/object-model/#paging-object
        """

        if 'next' not in paging_obj:
            return paging_obj

        if paging_obj['next'] is None:
            return paging_obj['items']
        else:
            items.extend(paging_obj['items'])
            new_paging_obj = self.send_api_request(paging_obj['next'])
            return self.extract_items_from_paging_obj(new_paging_obj, items)

    def format_playlist_tracks(self, playlist):
        """
        Returns a formatted dict containing the given playlist's id, name, and list of track
        objects.
        """

        return {
            'id': playlist.id,
            'playlist': playlist.name,
            'tracks': self.get_all_playlist_tracks(playlist.id)
        }

    def send_api_request(self, url, options=None):
        """
        Helper method for sending requests to Spotify's API with the proper access token.
        """

        # requests a new access token if the current one is expired
        if self.is_token_expired():
            self.request_access_token_client_auth_flow()

        headers = {
            'Authorization': 'Bearer {}'.format(self.token)
        }

        req = requests.get(url, headers=headers, params=options)
        json = req.json()

        if 'error' in json:
            raise ApiError(json['error']['status'], json['error']['message'])

        return req.json()

    def send_auth_request(self, type):
        """
        """

        credentials_str = '{0}:{1}'.format(CLIENT_ID, CLIENT_SECRET)
        encoded_credentials_str = base64.urlsafe_b64encode(credentials_str.encode()).decode()

        headers = {
            'Authorization': 'Basic {}'.format(encoded_credentials_str),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': type
        }

        token_req = requests.post(SPOTIFY_AUTH_URL, headers=headers, data=body)
        return token_req.json()

    def request_access_token_client_auth_flow(self):
        """
        Requests an access token from Spotify by following the Client Credentials Flow. This is
        used for operations that do not require authentication (e.g. read-only public data).
        Example object returned from Spotify API:
            {
                "access_token": "NgCXRKc...MzYjw",
                "token_type": "bearer",
                "expires_in": 3600,
            }

        API Reference: https://developer.spotify.com/documentation/general/guides/authorization-guide/#client-credentials-flow
        """

        token_obj = self.send_auth_request('client_credentials')
        self.token = token_obj['access_token']
        # calculates a new expiration timestamp based on the received auth token expiration
        self.token_expiration = datetime.datetime.now() \
            + datetime.timedelta(0, token_obj['expires_in'])

    def request_access_token_auth_code_flow(self):
        """
        Requests an access token from Spotify by following the Authorization Code flow.

        API reference: https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow
        """

        credentials_str = '{0}:{1}'.format(CLIENT_ID, CLIENT_SECRET)
        encoded_credentials_str = base64.urlsafe_b64encode(credentials_str.encode()).decode()

        headers = {
            'Authorization': 'Basic {}'.format(encoded_credentials_str),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'client_credentials'
        }

        token_req = requests.post(SPOTIFY_AUTH_URL, headers=headers, data=body)
        self.token = token_req.json()

    def get_current_user_playlist_tracks(self):
        """
        Retrieves all the tracks for the current user's playlists. Returns a list of dicts
        containing a playlist's id, name, and list of track objects.

        API reference: https://developer.spotify.com/documentation/web-api/reference/playlists/get-playlists-tracks/
        """

        # playlists objects are wrapped in a paging object so items need to be extracted
        playlists = self.extract_items_from_paging_obj(self.get_current_user_playlists(), [])
        return [self.format_playlist_tracks(p) for p in playlists]

    def get_user_profile(self):
        """
        Retrieves the user profile matching the given token.

        API reference: https://developer.spotify.com/documentation/web-api/reference/users-profile/get-current-users-profile/
        """

        user_profile_url = '{}/me'.format(SPOTIFY_API_URL)
        return self.send_api_request(user_profile_url)

    def get_current_user_playlists(self):
        """
        Retrieves all the playlists for the *current* user. Returns a list of playlist objects. The
        list is wrapped in a paging object.

        API reference: https://developer.spotify.com/documentation/web-api/reference/playlists/get-a-list-of-current-users-playlists/
        """

        playlists_url = '{0}/me/playlists'.format(SPOTIFY_API_URL)
        return self.send_api_request(playlists_url)

    def get_user_playlists(self, user_id):
        """
        Retrieves all the playlists for the given user id. Returns a list of playlist objects. The
        list is wrapped in a paging object.

        API reference: https://developer.spotify.com/documentation/web-api/reference/playlists/get-list-users-playlists/
        """

        playlists_url = '{0}/users/{1}/playlists'.format(SPOTIFY_API_URL, user_id)

        try:
            return self.send_api_request(playlists_url)
        except ApiError:
            return {}

    def get_all_playlist_tracks(self, playlist_id):
        """
        Retrieves all the tracks for the given playlist id. Returns a list of track objects. The
        returned track objects will only contain the following fields: album, artists, href, id,
        name, and type.

        API reference: https://developer.spotify.com/documentation/web-api/reference/playlists/get-playlists-tracks/
        """

        tracks_url = '{0}/{1}/tracks'.format(SPOTIFY_API_URL, playlist_id)

        # List of track properties to include in API response. Can be modified if desired.
        fields = 'items=(album, artists, href, id, name, type)'
        tracks_paging_obj = self.send_api_request(tracks_url, options=fields)
        return self.extract_items_from_paging_obj(tracks_paging_obj, [])
