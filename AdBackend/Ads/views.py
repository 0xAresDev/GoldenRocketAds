from django.shortcuts import render
from .serializers import AdvertiserSerializer, AdSerializer, AdvertisersToServerSerializer, ServeAdsSerializer
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Ad, Advertiser
from django.shortcuts import get_object_or_404


# Create your views here.
class AdvertiserView(generics.ListAPIView):
    serializer_class = AdvertiserSerializer
    permissions = [permissions.IsAuthenticated]
    queryset = Advertiser.objects.all()


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def change_ads_on_server_view(request, format=None):
    seri = AdvertisersToServerSerializer()
    if request.data.get("ADD"):
        company_name = request.data.get("ADD")
        seri.add(request.data.get("guild"), company_name)
        return Response(status=status.HTTP_200_OK)
    elif request.data.get("REMOVE"):
        company_name = request.data.get("REMOVE")
        seri.remove(request.data.get("guild"), company_name)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def get_ads_for_server_view(request, format=None):
    seri = ServeAdsSerializer()
    ads = seri.get_ads(request.data.get("guild"))
    if not ads:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(ads, status=status.HTTP_200_OK)

"""
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
    return Response(status=status.HTTP_400_BAD_REQUEST)"""
