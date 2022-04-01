import base64
from http.client import HTTPException
from multiprocessing import context
import os
from django.http import response
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from rest_framework import viewsets, permissions, status
from api.permissions import PostOrIsOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from api.serializers import UserSerializer, RoomWriteSerializer, TrackSerializer
from api.models import UserRoom, Room, Track
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
import uuid
import requests
import logging
from api.business.spotify_helper import SpotifyHelper
from api.converters.spotify_converter import SpotifyConverter

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
            return response.HttpResponseBadRequest(response.JsonResponse({"error": {"code": "username_already_exists"}}), content_type='application/json') 
        

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
            room = Room.objects.create(name=request.data["name"], access_code= str(uuid.uuid4()), spotify_token=request.data["spotify_token"], refresh_token=request.data["refresh_token"], user=user)
            return response.HttpResponse(response.JsonResponse({"room": {"name": room.name, "access_code": room.access_code}}), content_type='application/json') 
        except IntegrityError as err: 
            return response.HttpResponseBadRequest(response.JsonResponse({"message": str(err)}), content_type='application/json') 
        except: 
            return response.HttpResponseBadRequest(response.JsonResponse({"error": {"code": "unknown_error"}}), content_type='application/json') 

    def perform_destroy(self, instance):
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.user.username == request.user.username :
                self.perform_destroy(instance)
                return response.HttpResponse()
            else :
                return response.HttpResponseForbidden()
        except BaseException as err:
            return response.HttpResponseNotFound(response.JsonResponse({"message": str(err)}), content_type="application/json")
        
class SearchTrackAPIView(APIView): 

    def get(self, *args, **kwargs):
        query = self.request.query_params.get('q')
        access_code = self.request.META['HTTP_CODE']
        room = Room.objects.get(access_code=access_code)
        spotify_result = SpotifyHelper.searchTrack(room=room, query=query)
        if spotify_result.status_code == 401:
            room_new_token = SpotifyHelper.refreshToken(room=room)
            spotify_result = SpotifyHelper.searchTrack(room=room_new_token, query=query)
        if spotify_result.status_code == 200:
            context = {
                'request': self.request,
            }
            list_track = SpotifyConverter.from_spotify_result_to_list_track_serialized(spotify_result=spotify_result.json(), context=context)
            return Response(list_track.data)
        else : 
            return response.HttpResponseServerError(response.JsonResponse({"message": "cannot get spotify search result"}))

class AddTrackToQueueAPIView(APIView): 

    def post(self, *args, **kwargs):
        try:
            access_code = self.request.META['HTTP_CODE']
            uri = self.request.data["uri"]
            room = Room.objects.get(access_code=access_code)
            endpoint = "https://api.spotify.com/v1/me/player/queue?uri="+str(uri)
            headers = {"Authorization": "Bearer "+str(room.spotify_token)}
            res = requests.post(endpoint, headers=headers).json()
            if res.ok(): 
                return Response({'message': 'Add to queue'})
            else:
                return Response({'message': 'Spotify error'},
                                status=status.HTTPException)
        except: 
            return response.HttpResponseServerError(response.JsonResponse({"error": {"code": "unknown_error"}}), content_type="application/json")