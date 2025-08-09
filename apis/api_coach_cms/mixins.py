class ReqContextMixin:
    @property
    def _req_context(self):
        return self.context["request"]
