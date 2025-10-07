import logging


class DataLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        data = dict(extra)
        kwargs["extra"] = {"data": data}
        return msg, kwargs


def setup_logger():
    from src.config import config

    logger = logging.getLogger("app")

    if config.image_processing.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s -> %(data)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


_base_logger = setup_logger()


def get_logger() -> logging.LoggerAdapter:
    return DataLoggerAdapter(_base_logger, {})
