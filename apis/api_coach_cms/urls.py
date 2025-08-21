from django.conf import settings
from django.urls import path, include
from .views import views_users, views_browsable

app_name = "api_coach_cms"


endpoints_urlpatterns = [
    # Users
    path('current-coach', views_users.CurrentCoachInfoView.as_view(), name='current-coach'),
    path('login-coach', views_users.LoginCoachView.as_view(), name='login-coach'),
    path(
        'get-all-clients-based-on-coach',
        views_users.GetAllClientsBasedOnCoachView.as_view(),
        name='get-all-clients-based-on-coach'
    ),

]

urlpatterns = [path("", include(endpoints_urlpatterns))]

if settings.DEBUG:
    endpoints_urlpatterns_debug = [
        path("", views_browsable.APIRootView.as_view(), name="root"),
    ]
    urlpatterns += [path("", include(endpoints_urlpatterns_debug))]
