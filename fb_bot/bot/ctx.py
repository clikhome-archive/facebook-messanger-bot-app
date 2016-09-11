# -*- coding: utf-8 -*-
from __future__ import absolute_import
from contextlib import contextmanager
from werkzeug.local import LocalStack, LocalProxy


def _get_current_session():
    _session = _session_ctx_stack.top
    if _session is None:
        raise RuntimeError('Working outside of chat/session context.')
    return _session


@contextmanager
def set_chat_context(session):
    _session_ctx_stack.push(session)
    try:
        yield
    finally:
        _session_ctx_stack.pop()


def _get_current_question_class():
    return session.search_request.current_question.__class__


_session_ctx_stack = LocalStack()
session = LocalProxy(_get_current_session)
search_request = LocalProxy(lambda: session.search_request)
# current_question_class = LocalProxy(_get_current_question_class)
