from django.http import response
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from rest_framework import viewsets, permissions, status
from api.permissions import PostOrIsOwner
from rest_framework.permissions import IsAuthenticated
from api.serializers import UserSerializer, RoomWriteSerializer, TrackSerializer
from api.models import UserRoom, Room, Track
from rest_framework.authtoken.models import Token
import uuid
import requests
import logging

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserRoom.objects.all()
    serializer_class = UserSerializer
    permission_classes = [PostOrIsOwner]

    def get_queryset(self):
        # after get all products on DB it will be filtered by its owner and return the queryset
        owner_queryset = self.queryset.filter(username=self.request.user.username)
        return owner_queryset

    def create(self, request):
        try:
            user = UserRoom.objects.create(username=request.data["username"], friendly_name=request.data["friendly_name"])
            token = Token.objects.create(user=user)
            return response.HttpResponse(response.JsonResponse({"token": token.key}), content_type='application/json') 
        except: 
            return response.HttpResponseBadRequest(response.JsonResponse({"message": "username_already_exists"}), content_type='application/json') 
        

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomWriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # after get all products on DB it will be filtered by its owner and return the queryset
        owner_queryset = self.queryset.filter(user=self.request.user)
        return owner_queryset

    def create(self, request):
        try:
            user = UserRoom.objects.get(username=request.user.username)
            room = Room.objects.create(name=request.data["name"], access_code= str(uuid.uuid4()), spotify_token=request.data["spotify_token"], user=user)
            return response.HttpResponse(response.JsonResponse({"room": {"name": room.name, "access_code": room.access_code}}), content_type='application/json') 
        except IntegrityError as err: 
            return response.HttpResponseBadRequest(response.JsonResponse({"message": str(err)}), content_type='application/json') 
        except: 
            return response.HttpResponseBadRequest(response.JsonResponse({"message": "unknown_error"}), content_type='application/json') 

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.user.username == request.user.username :
                self.perform_destroy(instance)
                return response.HttpResponse()
            else :
                return response.HttpResponseForbidden()
        except BaseException as err:
            return response.HttpResponseNotFound(response.JsonResponse({"message": str(err)}), content_type='application/json')
        

class SearchTrackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q')
        access_code = self.request.META['HTTP_ACCESS_CODE']
        room = Room.objects.get(access_code=access_code)
        endpoint = "https://api.spotify.com/v1/search?q="+str(query)+"&type=track&market=FR&limit=10"
        logger.error(access_code)
        logger.error(endpoint)
        logger.error(room.spotify_token)
        headers = {"Authorization": "Bearer "+str(room.spotify_token)}
        res = requests.get(endpoint, headers=headers).json()
        logger.error(res)
        result = []
        # after get all products on DB it will be filtered by its owner and return the queryset
        for track in res["tracks"]["items"]:
            result.append(Track(uri=track["uri"], title=track["name"], duration=track["duration_ms"], artist=track["artists"][0]["name"], picture_url=track["album"]["images"][0]["url"]))
        return result