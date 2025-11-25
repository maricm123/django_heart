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
        views_users.GetUpdateClientView.as_view(),
        name='client-detail'
    ),
    path(
        'client-delete/<int:id>',
        views_users.DeleteClientView.as_view(),
        name='client-delete'
    )

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
    path(
        'get-training-session-detail/<int:id>',
        views_training_sessions.GetTrainingSessionView.as_view(),
        name='get-training-session-detail'
    ),
    path(
        'delete-training-session-detail/<int:id>',
        views_training_sessions.DeleteTrainingSessionView.as_view(),
        name='delete-training-session-detail'
    ),
    path(
        'update-training-session-detail/<int:id>',
        views_training_sessions.UpdateTrainingSessionView.as_view(),
        name='update-training-session-detail'
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
