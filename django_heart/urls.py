from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf import settings


app_name = 'django_heart'

urlpatterns = [
    # OpenAPI schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc UI
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path("admin/", admin.site.urls),
    path("api_heart/", include("apis.api_heart_tv.urls", namespace="api_heart")),
    path("api_coach/", include("apis.api_coach_cms.urls", namespace="api_coach_cms")),
]


if settings.DEBUG:
    import debug_toolbar
    from rest_framework import urls as rest_urls

    # urlpatterns = [url(r'^__debug__/', include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += [path("__debug__", include(debug_toolbar.urls))]
    # Allow rest_framework login/logout views to test rest APIs
    urlpatterns += [path("", include(rest_urls, namespace="rest_framework"))]