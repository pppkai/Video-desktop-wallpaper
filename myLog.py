import logging

def log(handler="my_log", log_file="test.log"):
    logger = logging.getLogger(handler)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        ch = logging.StreamHandler()
        formatter = logging.Formatter(fmt="%(asctime)s %(name)s %(filename)s %(message)s", datefmt="%Y/%m/%d %X")

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger