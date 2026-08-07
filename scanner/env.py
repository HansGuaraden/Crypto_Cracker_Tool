# -*- coding: utf-8 -*-
import sys
import struct
import platform
import ctypes
import os

_SUPPORTED_OS = {"win32"}

_ARCH_MAP = {
    "AMD64": "x64",
    "x86_64": "x64",
    "x86": "x86",
    "i686": "x86",
    "ARM64": "arm64",
    "aarch64": "arm64",
}


def get_platform_info():
    return {
        "os": sys.platform,
        "arch": platform.machine(),
        "python": platform.python_version(),
        "bits": struct.calcsize("P") * 8,
        "impl": platform.python_implementation(),
    }


def check_version(minimum=(3, 8)):
    return sys.version_info[:2] >= minimum


def arch_label():
    m = platform.machine().upper()
    return _ARCH_MAP.get(m, m.lower())


def is_supported():
    return sys.platform in _SUPPORTED_OS


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def get_proxy_env():
    return {
        "http": os.environ.get("HTTP_PROXY", ""),
        "https": os.environ.get("HTTPS_PROXY", ""),
        "no_proxy": os.environ.get("NO_PROXY", ""),
    }


def set_proxy_env(http_proxy, https_proxy=None, no_proxy=None):
    if https_proxy is None:
        https_proxy = http_proxy
    os.environ["HTTP_PROXY"] = http_proxy
    os.environ["HTTPS_PROXY"] = https_proxy
    if no_proxy is not None:
        os.environ["NO_PROXY"] = no_proxy


def clear_proxy_env():
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)
    os.environ.pop("NO_PROXY", None)