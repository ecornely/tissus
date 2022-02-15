#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from colors import Color
from PIL import Image
from PIL.ExifTags import TAGS
import piexif
from grid import generate_grid_whithout_collision

def grid_to_string(grid):
  s=""
  for i in range(len(grid)):
    for j in range(len(grid[i])):
      s+=str(grid[i][j].value)
    s+="\n"
  return s

def generate_image(grid):
  images = {
      Color.GREEN_PINK_FLOWERS : Image.open('img/GREEN_PINK_FLOWERS.jpg'),
      Color.WHITE_PINK_FLOWERS : Image.open('img/WHITE_PINK_FLOWERS.jpg'),
      Color.WHITE_GREEN_DOTS : Image.open('img/WHITE_GREEN_DOTS.jpg'),
      Color.PINK : Image.open('img/PINK.jpg'),
      Color.LIGHT_PINK_PINK_DOTS : Image.open('img/LIGHT_PINK_PINK_DOTS.jpg'),
  }
  width = len(grid[0]) * images[Color.GREEN_PINK_FLOWERS].width
  height = len(grid) *  images[Color.GREEN_PINK_FLOWERS].height
  img = Image.new('RGB', [width, height])
  for y in range(len(grid)):
    for x in range(len(grid[y])):
      i = images[grid[y][x]]
      img.paste(i, (x*i.width, y*i.height))
  grid_string = grid_to_string(grid)

  return grid_string, img

if __name__ == "__main__":
  for z in range(100):
    image_name=f"generated/grid-{z:03}.jpg"
    grid= generate_grid_whithout_collision()
    
    grid_string, img = generate_image(grid)
    exif_dict = {'0th': {270: grid_string }, 'Exif': {}, 'GPS': {}, 'Interop': {}, '1st': {}, 'thumbnail': None}
    exif_bytes = piexif.dump(exif_dict)
  
    img.save(image_name,"JPEG", optimize=True, quality=95, exif=exif_bytes)
    