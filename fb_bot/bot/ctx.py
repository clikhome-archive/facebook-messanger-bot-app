# -*- coding: utf-8 -*-
from __future__ import absolute_import
from contextlib import contextmanager
from werkzeug.local import LocalStack


_session_ctx_stack = LocalStack()


def get_current_session():
    session = _session_ctx_stack.top
    if session is None:
        raise RuntimeError('Working outside of chat/session context.')
    return session


@contextmanager
def set_chat_context(session):
    _session_ctx_stack.push(session)
    try:
        yield
    finally:
        _session_ctx_stack.pop()
