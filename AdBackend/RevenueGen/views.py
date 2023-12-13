from django.shortcuts import render
from .serializers import ChannelActivitySerializer, AdActivitySerializer, CalculateDailyIncomeSerializer, DailyIncomeSerializer
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import DailyIncome
from Ads.models import AdObject
from django.shortcuts import get_object_or_404



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_server_activity(request, format=None):
    seri = ChannelActivitySerializer()
    act = seri.create(request.data)
    if act:
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def daily_income_update_view(request, format=None):
    seri = CalculateDailyIncomeSerializer()
    act = seri.update_daily_income_of_servers()
    if act:
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def get_activity_points(request, format=None):
    seri = AdActivitySerializer()
    points = seri.get_activity(AdObject.objects.get(id=request.data.get("pk")))
    return Response({"points": points}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def get_all_engagement_points_in_time_period_view(request, format=None):
    seri = AdActivitySerializer()
    points = seri.get_activity_points_in_specific_time_period(request.data)
    return Response({"points": points}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def get_daily_incomes_view(request, format=None):
    seri = DailyIncomeSerializer()
    incomes = seri.get_daily_incomes(request.data.get("guild"), int(request.data.get("days")))
    return Response(incomes, status=status.HTTP_200_OK)
