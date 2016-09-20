# -*- coding: utf-8 -*-
from __future__ import absolute_import
from blinker import Namespace

_signals = Namespace()

session_started = _signals.signal('session-started')
session_finished = _signals.signal('session-finished')
handler_before_call = _signals.signal('handler-before-call')
