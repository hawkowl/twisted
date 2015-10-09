# -*- test-case-name: twisted.test.test_paths -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Python 3 and Windows-specific wrappers for L{os.path}/L{os} that use Unicode only.
"""

import os
import os.path

from os import listdir, utime, stat


def _ensureText(path):

    if isinstance(path, bytes):
        return path.decode("mbcs")
    return path


def isabs(path):
    return os.path.isabs(_ensureText(path))

def exists(path):
    return os.path.exists(_ensureText(path))

def normpath(path):
    return os.path.normpath(_ensureText(path))

def abspath(path):
    return os.path.abspath(_ensureText(path))

def splitext(path):
    return os.path.splitext(_ensureText(path))

def basename(path):
    return os.path.basename(_ensureText(path))

def dirname(path):
    return os.path.dirname(_ensureText(path))

def join(*paths):
    return os.path.join([_ensureText(path) for path in paths])
