from django.urls.exceptions import NoReverseMatch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse


class APIRootViewMixin(APIView):
    """
    Return a dict endpoint_name: url for a rest api.
    Url needing an extra parameter (often a pk) are not displayed.
    """

    url_namespace = None

    def get_endpoints(self):
        raise NotImplementedError

    def get(self, request):
        self._check_url_namespace()
        list_endpoints = self.get_endpoints()

        dict_endpoints = dict(
            url_without_parameters=dict(), url_with_parameters=dict()
        )
        for endpoint_path in list_endpoints:
            name = endpoint_path.name
            try:
                uri = request.build_absolute_uri(
                    reverse(f"{self.url_namespace}:{name}")
                )
                key = "url_without_parameters"
            except NoReverseMatch:
                uri = request.build_absolute_uri(endpoint_path.pattern._route)
                key = "url_with_parameters"

            dict_endpoints[key][name] = uri

        return Response(dict_endpoints)

    def _check_url_namespace(self):
        if not self.url_namespace:
            raise AttributeError("Set url namespace")
