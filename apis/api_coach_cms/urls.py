from django.conf import settings
from django.urls import path, include
from .views import (
    views_users,
    views_browsable,
    views_training_sessions,
    views_media
)

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
    path(
        'create-client',
        views_users.CreateClientView.as_view(),
        name='create-client'
    ),
    path(
        'client-detail/<int:id>',
        views_users.GetUpdateDeleteClientView.as_view(),
        name='client-detail'
    ),

    # Training sessions
    path(
        'active-training-sessions',
        views_training_sessions.GetActiveTrainingSessionsView.as_view(),
        name='active-training-sessions'
    ),
    path(
        'get-training-sessions-per-client/<int:id>',
        views_training_sessions.GetAllTrainingSessionsPerClientView.as_view(),
        name='get-training-sessions-per-client'
    ),
    path(
        'get-training-sessions-per-coach',
        views_training_sessions.GetAllTrainingSessionsPerCoachView.as_view(),
        name='get-training-sessions-per-coach'
    ),

    # Media
    path(
        'upload-profile-picture',
        views_media.UploadProfilePictureView.as_view(),
        name='upload-profile-picture'
    ),

]

urlpatterns = [path("", include(endpoints_urlpatterns))]

if settings.DEBUG:
    endpoints_urlpatterns_debug = [
        path("", views_browsable.APIRootView.as_view(), name="root"),
    ]
    urlpatterns += [path("", include(endpoints_urlpatterns_debug))]
