from apis.mixins import APIRootViewMixin


class APIRootView(APIRootViewMixin):
    url_namespace = "apis.api_heart_tv"

    def get_endpoints(self):
        from ..urls import endpoints_urlpatterns

        return endpoints_urlpatterns
