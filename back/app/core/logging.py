import inspect
import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Allow to intercept "external" logs to write them with loguru instead
    https://github.com/Delgan/loguru?tab=readme-ov-file#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def intercept_logs_toward_loguru_sinks() -> None:
    """Execute this function whenever logs should be configured"""
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
