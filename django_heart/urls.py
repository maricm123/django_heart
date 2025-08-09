from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api_heart/", include("api_heart_tv.urls", namespace="api_heart")),
    path("api_coach/", include("api_coach_cms.urls", namespace="api_coach_cms")),
]
