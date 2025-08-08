from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api_heart/", include("api_heart_tv.urls", namespace="api_heart")),
]
