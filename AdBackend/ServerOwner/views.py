from django.shortcuts import render
from .serializers import CreateServerSerializer, ChannelSerializer
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from .validity_checks import IsServerOwner
from rest_framework.response import Response
from rest_framework import status
from .models import Servers, Channel
from django.shortcuts import get_object_or_404


# Create your views here.
class CreateServerView(generics.CreateAPIView):
    serializer_class = CreateServerSerializer
    permissions = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def delete_server_view(request, format=None):
    if not IsServerOwner(request):
        return Response(status=status.HTTP_403_FORBIDDEN)
    server = Servers.objects.get(guild=request.data.get("guild"))
    server.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE', "POST", "PUT"])
@permission_classes([permissions.IsAuthenticated])
def channel_view(request, format=None):
    serializer = ChannelSerializer()
    if request.method == "POST":
        serializer.create(request.data)
        return Response(status=status.HTTP_201_CREATED)
    elif request.method == "PUT":
        serializer.update(request.data)
        return Response(status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        serializer.delete(request.data)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
