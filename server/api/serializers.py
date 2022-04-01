from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.models import UserRoom, Room, Track


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserRoom
        fields = ['url', 'username', 'friendly_name']

class RoomWriteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = ['url', 'name', 'spotify_token']

class RoomReadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = ['url', 'name', 'access_code']

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['title', 'artist', 'duration', 'picture_url', 'uri']