from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.models import UserRoom


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserRoom
        fields = ['url', 'username', 'friendly_name']