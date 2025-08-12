import logging


class IgnoreStaticRequestsFilter(logging.Filter):
    def filter(self, record):
        # record.msg je npr. '"GET /static/xyz.css HTTP/1.1" 304 0'
        return not record.getMessage().startswith('"GET /static/')
