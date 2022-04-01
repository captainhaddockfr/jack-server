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
from api.serializers import TrackSerializer
from api.models import Track, Host
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
import uuid
import requests
import logging
from api.business.spotify_helper import SpotifyHelper, BadSpotifyFormatException, HttpErrorSpotifyException
from api.converters.spotify_converter import SpotifyConverter

logger = logging.getLogger(__name__)
        
class HostAPIView(APIView):
    """
    API endpoint that allows to create host
    """
    def post(self, *args, **kwargs):
        try:
            if "spotify_token" in self.request.data and "refresh_token" in self.request.data:
                username, friendly_name = SpotifyHelper.get_spotify_user(self.request.data["spotify_token"])
                user_db = Host.objects.filter(username=username)
                user = None
                if user_db.exists():
                    user_to_update = user_db.first()
                    user_to_update.friendly_name = friendly_name
                    user_to_update.access_code = str(uuid.uuid4())
                    user_to_update.spotify_token = self.request.data["spotify_token"]
                    user_to_update.refresh_token = self.request.data["refresh_token"]
                    user_to_update.save(update_fields=["spotify_token", "refresh_token", "friendly_name", "access_code"])
                    user = user_to_update
                else :
                    user = Host.objects.create(username=username, friendly_name=friendly_name, spotify_token=self.request.data["spotify_token"], refresh_token=self.request.data["refresh_token"], access_code=str(uuid.uuid4()))
                token = Token.objects.get_or_create(user=user)
                return response.HttpResponse(response.JsonResponse({"token": token[0].key, "access_code": user.access_code}), content_type='application/json')
            else:
                return response.HttpResponseBadRequest(response.JsonResponse({"error": {"code": "spotify_token_missing", "message": "spotify_token missing or refresh_token missing"}})) 
        except IntegrityError as error: 
            logger.error(error)
            return response.HttpResponseServerError(response.JsonResponse({"error": {"code": "user_already_exists"}}), content_type="application/json")
        except (HttpErrorSpotifyException, BadSpotifyFormatException): 
            return response.HttpResponseServerError(response.JsonResponse({"error": {"code": "spotify_error"}}), content_type="application/json")
        except Exception as error :
            logger.error(error)
            return response.HttpResponseServerError(response.JsonResponse({"error": {"code": "unknown_error"}}), content_type="application/json")
        
class SearchTrackAPIView(APIView): 

    def get(self, *args, **kwargs):
        try:
            query = self.request.query_params.get('q')
            access_code = self.request.META['HTTP_CODE']
            host = Host.objects.get(access_code=access_code)
            spotify_result = SpotifyHelper.search_track(spotify_token=host.spotify_token, query=query)
            if spotify_result.status_code == 401:
                host_new_token = SpotifyHelper.refresh_token(host=host)
                spotify_result = SpotifyHelper.search_track(spotify_token=host_new_token.spotify_token, query=query)
            if spotify_result.status_code == 200:
                context = {
                    'request': self.request,
                }
                list_track = SpotifyConverter.from_spotify_result_to_list_track_serialized(spotify_result=spotify_result.json(), context=context)
                return Response(list_track.data)
            else : 
                return response.HttpResponseServerError(response.JsonResponse({"message": "cannot get spotify search result"}))
        except Exception:
            return response.HttpResponseServerError(response.JsonResponse({"error": {"code": "unknown_error"}}), content_type="application/json")

class AddTrackToQueueAPIView(APIView): 

    def post(self, *args, **kwargs):
        try:
            if not "HTTP_CODE" in self.request.META:
                return response.BadHeaderError(response.JsonResponse({"error": {"code": "missing_auth_code"}}), content_type="application/json")
            elif not "uri" in self.request.data:
                return response.HttpResponseBadRequest(response.JsonResponse({"error": {"code": "missing_uri"}}), content_type="application/json")
            else:
                access_code = self.request.META['HTTP_CODE']
                uri = self.request.data["uri"]
                host = Host.objects.get(access_code=access_code)
                spotify_result = SpotifyHelper.add_track_to_queue(uri=uri, spotify_token=host.spotify_token)
                if spotify_result.status_code == 401:
                    host_new_token = SpotifyHelper.refresh_token(host=host)
                    spotify_result = SpotifyHelper.add_track_to_queue(spotify_token=host_new_token.spotify_token, uri=uri)
                if spotify_result.status_code == 204:
                    return Response({'message': 'added_to_queue'})
                else:
                    return response.HttpResponseServerError(response.JsonResponse({"error": {"code": "spotify_error"}}), content_type="application/json")
        except (HttpErrorSpotifyException, BadSpotifyFormatException): 
            return response.HttpResponseServerError(response.JsonResponse({"error": {"code": "spotify_error"}}), content_type="application/json")
        except: 
            return response.HttpResponseServerError(response.JsonResponse({"error": {"code": "unknown_error"}}), content_type="application/json")