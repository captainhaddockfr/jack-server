

import base64
import os
import requests
from api.models import UserRoom, Room, Track

class SpotifyHelper: 

    @staticmethod
    def refreshToken(room): 
        endpoint_refresh_token = "https://accounts.spotify.com/api/token"
        data_refresh_token = {"grant_type": "refresh_token", "refresh_token": room.refresh_token}
        str_to_encode = (os.environ.get("SPOTIFY_CLIENT_ID")+":"+os.environ.get("SPOTIFY_CLIENT_SECRET")).encode("utf-8")
        base64_bytes = base64.b64encode(str_to_encode)
        headers_refresh_token = {"Authorization": "Basic "+base64_bytes.decode("utf-8"), "Content-Type": "application/x-www-form-urlencoded"}
        res_refresh_token = requests.post(endpoint_refresh_token, data=data_refresh_token, headers=headers_refresh_token)
        if res_refresh_token.status_code == 200:
            res_refresh_token_json = res_refresh_token.json()
            if "access_token" in res_refresh_token_json:
                room.spotify_token = res_refresh_token_json["access_token"]
                room.save(update_fields=["spotify_token"])
                print("Change Access Token : ")
            else:
                print("Error")
        else:
            print("Error bis")
        return room

    @staticmethod
    def searchTrack(room, query):
        endpoint = "https://api.spotify.com/v1/search?q="+str(query)+"&type=track&market=FR&limit=10"
        headers = {"Authorization": "Bearer "+str(room.spotify_token)}
        res = requests.get(endpoint, headers=headers)
        return res