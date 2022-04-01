

import base64
import os
import requests
from api.models import Track

class SpotifyHelper: 

    @staticmethod
    def refresh_token(host): 
        endpoint_refresh_token = "https://accounts.spotify.com/api/token"
        data_refresh_token = {"grant_type": "refresh_token", "refresh_token": host.refresh_token}
        str_to_encode = (os.environ.get("SPOTIFY_CLIENT_ID")+":"+os.environ.get("SPOTIFY_CLIENT_SECRET")).encode("utf-8")
        base64_bytes = base64.b64encode(str_to_encode)
        headers_refresh_token = {"Authorization": "Basic "+base64_bytes.decode("utf-8"), "Content-Type": "application/x-www-form-urlencoded"}
        res_refresh_token = requests.post(endpoint_refresh_token, data=data_refresh_token, headers=headers_refresh_token)
        if res_refresh_token.status_code == 200:
            res_refresh_token_json = res_refresh_token.json()
            if "access_token" in res_refresh_token_json:
                host.spotify_token = res_refresh_token_json["access_token"]
                host.save(update_fields=["spotify_token"])
                
            else:
                print(res_refresh_token_json) 
                raise BadSpotifyFormatException
        else:
            print(res_refresh_token) 
            raise HttpErrorSpotifyException
        return host

    @staticmethod
    def get_spotify_user(spotify_token):
        endpoint = "https://api.spotify.com/v1/me"
        headers = {"Authorization": "Bearer "+spotify_token}
        user_request = requests.get(endpoint, headers=headers)

        if user_request.status_code == 200:
            user = user_request.json()
            print(user)
            if "id" in user and "display_name" in user:
                return user["id"], user["display_name"]
            else: 
                raise BadSpotifyFormatException
        else:
            raise HttpErrorSpotifyException

    @staticmethod
    def search_track(spotify_token, query):
        endpoint = "https://api.spotify.com/v1/search?q="+str(query)+"&type=track&market=FR&limit=10"
        headers = {"Authorization": "Bearer "+str(spotify_token)}
        res = requests.get(endpoint, headers=headers)
        return res

    @staticmethod
    def add_track_to_queue(uri, spotify_token):
        endpoint = "https://api.spotify.com/v1/me/player/queue?uri="+str(uri)
        headers = {"Authorization": "Bearer "+str(spotify_token)}
        res = requests.post(endpoint, headers=headers)
        return res

class BadSpotifyFormatException(Exception):
    pass

class HttpErrorSpotifyException(Exception):
    pass