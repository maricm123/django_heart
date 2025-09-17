import json
import logging
import boto3
from logging import Logger
from typing import Dict, Sequence, Optional
from dataclasses import dataclass
from django.conf import settings


####################################################################################################
# Data structure utils
####################################################################################################


def merge_dicts(*dictionnaries: Dict) -> Dict:
    """
    Return a merged dict containing all key-values from provided dicts
    NOTE: base solution found here: https://stackoverflow.com/a/9416020/2255491
    """
    final_dict = dict()
    for d in dictionnaries:
        if not isinstance(d, Dict):
            raise TypeError("One of the provided parameter is not of type Dict")
        for k, v in d.items():
            # Doubles are forbidden, as it could lead to silence errors
            if k in final_dict.keys():
                raise ValueError(f'"{k}" key already exists in the source dict.')
            final_dict[k] = v

    return final_dict

####################################################################################################
# logging utils
####################################################################################################


def as_app_log(object) -> str:
    """
    wrapper to help displaying applicative logs without providing to much information when
    calling AppLog() instance
    """
    if object:  # could be None
        if hasattr(object, "as_app_log"):
            return object.as_app_log
        else:
            return object.__str__()
    else:
        return "NONE"  # we need to display something anyway in the log line


# class AppLogSource(Enum):
#     """Enum to help define source of the applicative log (ie. where it comes from)"""
#
#     BACK_OFFICE = auto()
#     CONVIVE_APP = auto()
#     CONVIVE_TILL = auto()
#     TEAM_MEMBER_TILL = auto()


@dataclass
class AppLogTemplate:
    slug: str
    message_template: str
    # extras attributes defined at template level
    extras: Optional[Dict] = None
    # extras attributes that will need to be defined at instance level
    required_extras: Optional[Sequence[str]] = None


def get_logger(module_name) -> Logger:
    return logging.getLogger(f"{settings.PROJECT_NAME}.{module_name}")


@dataclass
class AppLogException:
    slug: str

    def __init__(self, slug: str, logger: Logger):
        self.slug = slug
        logger.error(self.slug, exc_info=True)


@dataclass
class AppLog:
    slug: str
    message: str
    extras: dict = None

    def __init__(self, logger: Logger, template: AppLogTemplate, **kwargs):
        try:
            self.slug = template.slug
            self.message = template.message_template.format(
                # Apply as_app_log() fonction to all kwargs to display them as expected
                **{k: as_app_log(v) for k, v in kwargs.items()}
            )
            # First we check that template required extras are provided
            self.extras = kwargs.get("extras")
            self._check_required_extras(template)
            # Once it's checked, we add template extras
            self.extras = merge_dicts(self.extras or {}, template.extras or {})  # avoid None
            logger.info(self._full_message())
        except Exception as e:  # we don't want to break the program if app log does not work
            logger.error(f"ERROR when trying to log applicative stuff: {e}", exc_info=True)

    def _check_required_extras(self, template):
        if template.required_extras:
            if not self.extras:
                raise Exception('ERROR: "extras" parameter should be provided in AppLog')

            for extra_attr in template.required_extras:
                if extra_attr not in self.extras.keys():
                    raise Exception(f"ERROR: {extra_attr} attribute is not provided")

    def _full_message(self):
        """return a JSON string containing all AppLog attributes"""

        # https://stackoverflow.com/a/18337754/2255491
        return json.dumps(self.__dict__, ensure_ascii=False)


class IgnoreStaticRequestsFilter(logging.Filter):
    def filter(self, record):
        # record.msg je npr. '"GET /static/xyz.css HTTP/1.1" 304 0'
        return not record.getMessage().startswith('"GET /static/')


class IgnoreStaticUvicornRequestsFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # odbacuje sve logove za /static/ fajlove
        return not (msg.startswith("127.0.0.1") and "/static/" in msg)


# AWS S3 Utils
def generate_presigned_url(file_name, file_type):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    presigned_url = s3_client.generate_presigned_url(
        'put_object',  # operacija upload-a
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': file_name,
            'ContentType': file_type,
            'ACL': 'public-read'  # opcionalno, ako želiš da URL bude direktno dostupan
        },
        ExpiresIn=300  # važi 5 minuta
    )
    print(presigned_url, "PRESIGNED URL")
    return presigned_url
