#!/usr/bin/env/python

from __future__ import division

import random
from noise import pnoise2
from PyQt4 import QtGui, QtCore
import sys

hex_colour = ['#006600', '#197519', '#338533', '#4D944D', '#66A366', '#80B280', '#99C299', '#B2D1B2', '#CCE0CC', '#E6F0E6', '#FFFFFF']
#hex_colour = ['#0033CC', '#0033CC', '#0033CC', '#0033CC', '#4D70DB', '#80B280', '#99C299', '#B2D1B2', '#CCE0CC', '#E6F0E6', '#FFFFFF']
  
def isOdd(integer):                                     # move to World
  return bool(integer & 1)

class World(list):
  def __init__(self, width, height, continuous_width = False, continuous_height = False, seed = None, sea_level = 5):
    object.__init__(self)
    self.height = height
    self.width = width
    self.continuous_width = False
    self.continuous_height = False
    self.sea_level = sea_level
    self.seed = seed

    self.generateMap()
    self.setContinuous(continuous_width, continuous_height)
    self.drawLand()
    
  def generateMap(self):
    for r in range(0, self.height):
      row = []
      self.append(row)
      for c in range(0, self.width):
        self[r].append(Tile(r, c))

  def getTiles(self):
    container = []
    for row in range(self.height):
      for col in range(self.width):
        container.append(self[row][col])
    return container

  def getRandomTiles(self):
    container = self.getTiles()
    random.shuffle(container)
    return container

  def setContinuous(self, continuous_width = False, continuous_height = False):
      self.continuous_width = continuous_width
      self.continuous_height = continuous_height

  def cor(self, integer, limit, continuous = False):
    if continuous == False:
      if integer > limit -1:
        return limit -1
      elif integer < 0:
        return 0
      else:
        return integer
    else:
      if integer > limit -1:
        return limit - 1 - integer
      else:
        return integer

  def corX(self, col):
    return self.cor(col, self.width, self.continuous_width)

  def corY(self, row):
    return self.cor(row, self.height, self.continuous_height)

  def getTile(self, col, row):
    return self[self.corY(row)][self.corX(col)]

  def getNeighbouringTiles(self, tile):
    # TODO: modify with if clause for hex vs square tiles
    diffs = [(-1, 0), (-1, -1), (0, -1), (1, 0), (1, 1), (0, 1), (1, -1), (-1, 1)]
    return [self.getTile(tile.col + diff[0], tile.row + diff[1]) for diff in diffs]

  def getNeighbouringElevation(self, tile):
    return [neighbour.elevation for neighbour in getNeighbouringTiles()]  

  def drawLand(self):
    if self.seed == None:
      seed = random.randint(1, 1000)
      self.seed = seed
    else:
      seed = self.seed
    noise = []
    for tile in self.getTiles():
      relX = float(tile.col / self.width)
      relY = float(tile.row / self.height)
      tile.noise = pnoise2(relX, relY, 13, 0.6, base = seed)
      noise.append(tile.noise)
    min_noise = min(noise)
    max_noise = max(noise)
    noise_range = float(max_noise - min_noise)
    for tile in self.getTiles():
      tile.elevation = (tile.noise + abs(min_noise)) / noise_range

class Tile(object):
  def __init__(self, row, col):
    object.__init__(self)
    self.row = row
    self.col = col
    self.noise = None
    self.elevation = 0

class Application(QtGui.QApplication):
  def __init__(self, width = 500, height = 300, continuous_width = False, continuous_height = False, pixel = 1, seed = None, sea_level = 5):
    QtGui.QApplication.__init__(self, sys.argv)
    self.pixel = pixel
    self.world = World(width, height, continuous_width, continuous_height, seed, sea_level)
    self.main = Preview()
    self.main.show()
    self.main.setWindowTitle(str(self.world.seed))
    
class Preview(QtGui.QWidget):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.app = QtCore.QCoreApplication.instance()
    self.setFixedSize(self.app.world.width * self.app.pixel, self.app.world.height * self.app.pixel)

  def paintEvent(self, e):
    qp = QtGui.QPainter()
    qp.begin(self)
    self.drawTiles(qp)
    qp.end()
    
  def drawTiles(self, painter):
    width = self.app.pixel
    for row in range(len(self.app.world)):
      if isOdd(row):
        margin = int(width/2)
      else:
        margin = 0    
      for col in range(len(self.app.world[row])):
      	tile = self.app.world[row][col]
      	color = QtGui.QColor(0 ,0, 0)
        if int(tile.elevation * 10) < self.app.world.sea_level - 1:
          color.setNamedColor('#0033CC')
        elif int(tile.elevation  * 10) == self.app.world.sea_level - 1:
          color.setNamedColor('#4D70DB')
        else:
          color.setNamedColor(hex_colour[int(tile.elevation * 10)])
        painter.setPen(color)
        painter.setBrush(color)
        painter.drawRect(col * width + margin, row * width, width, width)
        
if __name__ == "__main__":

  tileSize = 1 # pixel width
  seedNumber = None # if None random seed from 0 to 999
  seaLevel = 5 # n deep waters + 1 shallow waters (max 10)
  application = Application(pixel = tileSize, seed = seedNumber, sea_level = seaLevel)
  sys.exit(application.exec_())