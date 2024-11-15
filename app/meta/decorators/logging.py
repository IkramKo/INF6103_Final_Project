import functools
import inspect
import logging

logger = logging.getLogger()

def log_method_calls(logger):
    """Decorator to log method entry and exit."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Entering method: {func.__name__} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Exiting method: {func.__name__} with result: {result}")
                return result
            except Exception as e:
                logger.exception(f"Exception in method {func.__name__}: {e}")
                raise  # Re-raise the exception after logging
        return wrapper
    return decorator

def log_with_attributes(message, level="info", **attributes):
    """Logs a message with Loki-compatible attributes, including the calling function."""

    attributes['function'] = inspect.currentframe().f_back.f_code.co_name # Get calling function's name
    log_method = getattr(logger, level)
    log_method(message, extra={**attributes}) # Correct usage