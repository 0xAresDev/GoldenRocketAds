from django.urls import path
from .views import CreateServerView, delete_server_view, channel_view


app_name = "ServerOwner"

urlpatterns = [
    path('create-server/', CreateServerView.as_view(), name='server-creation'),
    path('delete-server/', delete_server_view, name='server-deletion'),
    path('channels/', channel_view, name="channel")
]
