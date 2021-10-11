from django.http import response
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from api.permissions import PostOrIsOwner
from rest_framework.permissions import IsAuthenticated
from api.serializers import UserSerializer
from api.models import UserRoom
from rest_framework.authtoken.models import Token


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = UserRoom.objects.all().order_by('-date_joined')
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
        
