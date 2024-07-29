#
# Copyright 2024 - Final Year Project for Bachelor of Science in Cyber Security and Digital Forensics Engineering
#
# SPDX-License-Identifier: Apache-2.0
r"""Utils module."""


def build_conf_dict(name, bid, cwe, qualnames, message, level="MEDIUM"):
    """Build and return a blacklist configuration dict."""
    return {
        "name": name,
        "id": bid,
        "cwe": cwe,
        "message": message,
        "qualnames": qualnames,
        "level": level,
    }
