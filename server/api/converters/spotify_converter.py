from api.serializers import TrackSerializer
from api.models import Track

class SpotifyConverter:
    @staticmethod
    def from_spotify_result_to_list_track_serialized(spotify_result, context):
        result = []
        if "tracks" in spotify_result and "items" in spotify_result["tracks"]:
            # after get all products on DB it will be filtered by its owner and return the queryset
            for track in spotify_result["tracks"]["items"]:
                result.append(Track(uri=track["uri"], title=track["name"], duration=track["duration_ms"], artist=track["artists"][0]["name"], picture_url=track["album"]["images"][0]["url"]))
        return TrackSerializer(result, many=True, context=context)