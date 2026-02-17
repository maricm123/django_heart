from django.conf import settings
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    views_users,
    views_browsable,
    views_training_sessions,
    views_media,
    views_dashboard,
    views_tenant,
    views_contact
)

app_name = "api_coach_cms"


endpoints_urlpatterns = [
    # Tenants
    path('current-tenant', views_tenant.GetCurrentTenant.as_view(), name='current-tenant'),
    # Users
    path('current-coach', views_users.GetCurrentCoachDetailsView.as_view(), name='current-coach'),
    path(
        'update-current-coach',
        views_users.UpdateCurrentCoachView.as_view(),
        name='update-current-coach'
    ),
    path('login-coach', views_users.LoginCoachView.as_view(), name='login-coach'),
    path('logout-coach', views_users.LogoutCoachView.as_view(), name='logout-coach'),
    path('refresh-token', TokenRefreshView.as_view(), name='refresh-token'),
    path(
        'get-all-clients-from-coach',
        views_users.GetAllClientsFromCoach.as_view(),
        name='get-all-clients-from-coach'
    ),
    path(
        'get-all-clients-from-coach-not-active-session',
        views_users.GetAllClientsFromCoachNotActiveSessionView.as_view(),
        name='get-all-clients-from-coach-not-active-session'
    ),
    path(
        'create-client',
        views_users.CreateClientView.as_view(),
        name='create-client'
    ),
    path(
        'update-client/<int:id>',
        views_users.UpdateClientView.as_view(),
        name='update-client'
    ),
    path(
        'get-client-detail/<int:id>',
        views_users.GetClientDetailsView.as_view(),
        name='get-client-detail'
    ),
    path(
        'client-delete/<int:id>',
        views_users.DeleteClientView.as_view(),
        name='client-delete'
    ),

    # Training sessions
    path(
        'get-active-training-sessions',
        views_training_sessions.GetActiveTrainingSessionsView.as_view(),
        name='get-active-training-sessions'
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
    path(
        'force-delete-training-session/<int:id>',
        views_training_sessions.ForceDeleteActiveTrainingSessionView.as_view(),
        name='force-delete-training-session'
    ),
    path(
        "training-session/<int:id>/pause",
        views_training_sessions.PauseActiveTrainingSessionView.as_view(),
        name='pause-training-session'
    ),
    path(
        "training-session/<int:id>/resume",
        views_training_sessions.ResumeActiveTrainingSessionView.as_view(),
        name='resume-training-session'
    ),

    # Media
    path(
        'upload-profile-picture',
        views_media.UploadProfilePictureView.as_view(),
        name='upload-profile-picture'
    ),

    # Dashboard
    path(
        'dashboard-informations',
        views_dashboard.DashboardInformationsView.as_view(),
        name='dashboard-informations'
    ),

    # Contact form
    path(
        'contact-form',
        views_contact.SendMailContactFormView.as_view(),
        name='contact-form'
    ),

]

urlpatterns = [path("", include(endpoints_urlpatterns))]

if settings.DEBUG:
    endpoints_urlpatterns_debug = [
        path("", views_browsable.APIRootView.as_view(), name="root"),
    ]
    urlpatterns += [path("", include(endpoints_urlpatterns_debug))]
