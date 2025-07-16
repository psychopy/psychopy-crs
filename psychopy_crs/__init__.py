#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Originally part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2022 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

"""Extension package for PsychoPy which adds support for various hardware
devices by Cambridge Research Systems.
"""

__version__ = "0.0.2"


from . import bits, shaders
from .legacy import colorcal, optical


__all__ = [
    "experiment",
    "hardware",
    "legacy",
    "bits",
    "colorcal",
    "optical",
    "shaders"
]