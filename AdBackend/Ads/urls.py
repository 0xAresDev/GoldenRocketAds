from django.urls import path
from .views import AdvertiserView, change_ads_on_server_view, get_ads_for_server_view


app_name = "Ads"

urlpatterns = [
    path('get-advertisers/', AdvertiserView.as_view(), name='list-advertisers'),
    path('change-advertisers-on-server/', change_ads_on_server_view, name='change-advertisers-on-servers'),
    path('get-ads/', get_ads_for_server_view, name='get-ads'),
]
