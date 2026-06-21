"""Logging setup. Each entry point calls setup_logging(level) once in main()."""
import logging
import sys


def setup_logging(level="INFO"):
    logging.basicConfig(
        level=getattr(logging, str(level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )


def get_logger(name):
    return logging.getLogger(name)
