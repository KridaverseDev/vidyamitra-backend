import functools
import traceback

from django.contrib.auth import get_user_model
from loguru import logger
from ninja.errors import HttpError, ValidationError

from silicon._sdk.error_handler import ErrorMessage

User = get_user_model()


def error_handler(func):
    """Error handler decorator to handle exceptions."""

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            logger.error(traceback.format_exc())
            raise e

        except User.DoesNotExist:
            logger.error(traceback.format_exc())
            raise HttpError(404, ErrorMessage.USER_ERR_01)

        except ValidationError as e:
            raise HttpError(400, ErrorMessage.ERR_DEFAULT)

        except Exception as ex:
            logger.error(traceback.format_exc())
            raise HttpError(400, ErrorMessage.ERR_DEFAULT)

    return decorator
