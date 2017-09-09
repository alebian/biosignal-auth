import logging

import settings


def get_logger():
    handlers = [logging.FileHandler(settings.LOG_FILE)]
    if settings.LOG_CONSOLE:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        datefmt=settings.LOG_DATE_FORMAT,
        handlers=handlers
    )
    return logging
