from django.urls import path, include
from .views import view_users, view_heart_rate, views_training_session, views_browsable
from django.conf import settings

app_name = "api_heart"


endpoints_urlpatterns = [
    # Users
    path('get-all-users', view_users.GetAllUsersView.as_view(), name='get-all-users'),
    path('get-all-clients', view_users.GetAllClientsView.as_view(), name='get-all-clients'),

    # Heart rate
    path('heart-rate/latest', view_heart_rate.LatestHeartRateView.as_view(), name='heart-rate-latest'),

    path(
        'save-heartbeat',
        view_heart_rate.HeartRateCreateRecordFromFrontendView.as_view(),
        name='create-heart-rate'
    ),

    # Sessions
    path('create-session', views_training_session.CreateTrainingSessionView.as_view(), name='create-session'),
    path('finish-session/<int:id>', views_training_session.FinishTrainingSessionView.as_view(), name='finish-session'),

]

urlpatterns = [path("", include(endpoints_urlpatterns))]

if settings.DEBUG:
    endpoints_urlpatterns_debug = [
        path("", views_browsable.APIRootView.as_view(), name="root"),
    ]
    urlpatterns += [path("", include(endpoints_urlpatterns_debug))]
