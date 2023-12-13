from django.urls import path
from .views import add_server_activity, get_activity_points, get_all_engagement_points_in_time_period_view, daily_income_update_view, get_daily_incomes_view


app_name = "RevenueGen"

urlpatterns = [
    path('add-activity/', add_server_activity, name='add-activity'),
    path('get-ad-engagement/', get_activity_points, name='get-add-engagement'),
    path('get-engagement-points-in-time-period/', get_all_engagement_points_in_time_period_view,
         name='get-engagement-points-in-time-period'),
    path('update-incomes/', daily_income_update_view, name='update-income'),
    path('get-incomes/', get_daily_incomes_view, name='get-incomes'),
]
