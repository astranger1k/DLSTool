"""General utility helpers used by the DLS tool application."""
from __future__ import annotations

import configparser


def read_ini_with_slash_comments(ini_path: str) -> configparser.ConfigParser:
    """Read an INI file while honoring // comment markers."""
    parser = configparser.ConfigParser(comment_prefixes=("#", ";", "//"), allow_no_value=True)
    parser.read(ini_path, encoding="utf-8")
    return parser


__all__ = ["read_ini_with_slash_comments"]