#!/usr/bin/env python3

from contextlib import contextmanager


class InputValidationException(Exception):
    pass


class FatalRuntimeException(Exception):
    pass


@contextmanager
def ignore_exceptions(*exception_classes):
    try:
        yield
    except exception_classes:
        pass


@contextmanager
def ignore_exceptions_except(*exception_classes):
    try:
        yield
    except Exception as e:
        if isinstance(e, exception_classes):
            raise e
