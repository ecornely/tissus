#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from colors import Color
import random

def generate_grid():
  jars = {
    Color.WHITE_PINK_FLOWERS : 30,
    Color.WHITE_GREEN_DOTS : 26,
    Color.GREEN_PINK_FLOWERS : 18,
    Color.PINK : 30,
    Color.LIGHT_PINK_PINK_DOTS : 8,
  }
  grid_collision = False
  grid=[]
  for y in range(0,7):
    line=[]
    grid.append(line)
    for x in range(0,16):
      collision, color = random_color(jars, grid, x, y)
      grid_collision = grid_collision or collision
      line.append(color)
  return grid, grid_collision

def random_color(jars, grid, x, y):
  avoid=[]
  if(len(grid) > 1 and y > 0):
    avoid.append(grid[y-1][x])
  if(x>=1):
    avoid.append(grid[y][x-1])
  trial=0
  key = list(jars.keys())[random.randint(0,len(jars.keys())-1)]
  while trial<10 and key in avoid:
    key = list(jars.keys())[random.randint(0,len(jars.keys())-1)]
    trial+=1
  jars[key] = jars[key]-1
  if jars[key] == 0:
    del jars[key]
  return trial == 10, key

def generate_grid_whithout_collision():
    grid, collision = generate_grid()
    while collision:
      grid, collision = generate_grid()
    return grid
