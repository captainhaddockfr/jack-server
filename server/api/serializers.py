from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.models import Track


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['title', 'artist', 'duration', 'picture_url', 'uri']