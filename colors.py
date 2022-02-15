#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum

class Color(Enum):
    WHITE_PINK_FLOWERS = 1
    WHITE_GREEN_DOTS = 2
    GREEN_PINK_FLOWERS = 3
    PINK = 4
    LIGHT_PINK_PINK_DOTS = 5

    @staticmethod
    def values():
        return list(map(lambda c: c.value, Color))

    @staticmethod
    def fromValue(i):
        color = list(filter(lambda c: c.value == i, Color))
        if len(color) == 1:
            return color[0]
        else:
            return None
