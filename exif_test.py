#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
from PIL.ExifTags import TAGS
import piexif

img = Image.open('generated/grid-001.jpg')
eb = img.info['exif']
print(eb)
edict=piexif.load(eb)
print(edict)

grid_string='FOO'
exif = {'0th': {270: grid_string }, 'Exif': {}, 'GPS': {}, 'Interop': {}, '1st': {}, 'thumbnail': None}
exif_bytes = piexif.dump(exif)
print(exif_bytes)