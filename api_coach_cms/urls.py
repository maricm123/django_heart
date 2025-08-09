from django.urls import path, include
from .views import views_users

app_name = "api_coach_cms"


endpoints_urlpatterns = [
    # Users
    path('current-coach', views_users.CurrentCoachInfoView.as_view(), name='current-coach'),

]

urlpatterns = [path("", include(endpoints_urlpatterns))]

# if settings.DEBUG:
#     endpoints_urlpatterns_debug = [
#         path("", view_browsable.APIRootView.as_view(), name="root"),
#     ]
#     urlpatterns += [path("", include(endpoints_urlpatterns_debug))]
