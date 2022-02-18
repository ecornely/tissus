#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import os.path
import io
import math
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from grid import generate_grid_whithout_collision
from colors import Color
from PIL import Image
import piexif

lock_image = QImage('img/lock.png')

class GridLabel(QLabel):
    def __init__(self, parent, grid):
        QLabel.__init__(self, parent)
        self.grid = grid
        self.clip = None
        self.lock = []
        for i in range(7):
            l = []
            for j in range(16):
                l.append(False)
            self.lock.append(l)
        self.images = {
            Color.GREEN_PINK_FLOWERS: QImage('img/large/GREEN_PINK_FLOWERS.jpg'),
            Color.WHITE_PINK_FLOWERS: QImage('img/large/WHITE_PINK_FLOWERS.jpg'),
            Color.WHITE_GREEN_DOTS: QImage('img/large/WHITE_GREEN_DOTS.jpg'),
            Color.PINK: QImage('img/large/PINK.jpg'),
            Color.LIGHT_PINK_PINK_DOTS: QImage('img/large/LIGHT_PINK_PINK_DOTS.jpg'),
        }
        self.resize(720, 315)

    def setGrid(self, grid):
        self.grid = grid
        self.clip = None
        self.repaint(0, 0, self.width(), self.height())

    def getGridString(self):
        s = ""
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                s += str(self.grid[i][j].value)
            s += "\n"
        return s

    def setLock(self, lock):
        self.lock = lock

    def getLockString(self):
        s = ""
        for i in range(len(self.lock)):
            for j in range(len(self.lock[i])):
                s += str('1' if self.lock[i][j] else '0')
            s += "\n"
        return s

    def getLock(self):
        lock = []
        for y in range(len(self.lock)):
            l = []
            for x in range(len(self.lock[y])):
                if self.lock[y][x]:
                    #print('Self.lock[{y}][{x}]')
                    l.append(self.grid[y][x])
                else:
                    l.append(None)
            lock.append(l)
        return lock

    def toImage(self):
        img = QImage(720, 315, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                cell = self.grid[y][x]
                painter.drawImage(QPoint(x*45, y*45), self.images[cell].scaled(45, 45, aspectRatioMode=Qt.AspectRatioMode.IgnoreAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation))
        return img

    def paintEvent(self, paintEvent):
        cell_size = math.floor(self.width() / 16)
        painter = QPainter(self)
        lock_size = math.floor(cell_size / 4)
        small_lock = lock_image.scaled(lock_size, lock_size, aspectRatioMode=Qt.AspectRatioMode.IgnoreAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation)            
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                cell = self.grid[y][x]
                painter.drawImage(QPoint(x*cell_size, y*cell_size), self.images[cell].scaled(cell_size, cell_size, aspectRatioMode=Qt.AspectRatioMode.IgnoreAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation))
                if self.lock[y][x]:
                    top_left = QPoint(x*cell_size, y*cell_size)
                    top_left += QPoint(math.floor(cell_size/2), math.floor(cell_size/2))
                    top_left -= QPoint(math.floor(lock_size/2), math.floor(lock_size/2))
                    painter.drawImage(top_left, small_lock)
                    #painter.fillRect(x*cell_size+10, y*cell_size+10, cell_size-20, cell_size-20, QColor.fromRgb(125,125,125,200))
        if self.clip != None:
            painter.fillRect(self.clip[1]*cell_size, self.clip[0]
                             * cell_size, cell_size, cell_size, QColor.fromRgb(255, 0, 0, 64))

    def mousePressEvent(self, event):
        cell_size = math.floor(self.width() / 16)
        if event.button() == Qt.LeftButton:
            x = int(event.x()/cell_size)
            y = int(event.y()/cell_size)
            locked = self.lock[y][x]
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.lock[y][x] = not locked
            elif not locked:
                if self.clip != None and self.clip[0] == y and self.clip[1] == x:
                    self.clip = None
                else:
                    if self.clip == None:
                        self.clip = [y, x]
                    else:
                        color = self.grid[self.clip[0]][self.clip[1]]
                        self.grid[self.clip[0]][self.clip[1]] = self.grid[y][x]
                        self.grid[y][x] = color
                        self.clip = None
            self.repaint(0, 0, self.width(), self.height())


class Swapper(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Tile swapper")
        self.resize(750, 365)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.gridLabel = GridLabel(self, self.generate(None))
        menuBar = QMenuBar(self)
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        openAction = QAction("&Open", fileMenu)
        openAction.triggered.connect(self.open)
        fileMenu.addAction(openAction)
        saveAction = QAction("&Save", fileMenu)
        saveAction.triggered.connect(self.save)
        fileMenu.addAction(saveAction)
        generateAction = QAction("&Generate", fileMenu)
        fileMenu.addAction(generateAction)
        generateAction.triggered.connect(self.regenerate)
        fileMenu.addSeparator()
        quitAction = QAction("&Quit", fileMenu)
        fileMenu.addAction(quitAction)
        quitAction.triggered.connect(self.quit)
        layout.addWidget(menuBar)
        layout.addWidget(self.gridLabel, 1)

    def save(self):
        folder = './generated/' if os.path.isdir('./generated/') else '.'
        fname = QFileDialog.getSaveFileName(
            self, 'Save file', folder, "Image files (*.jpg)")
        if fname[0] != '':
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            self.gridLabel.toImage().save(buffer, "JPG", 100)
            img = Image.open(io.BytesIO(buffer.data()))
            exif_dict = {
                '0th': {
                    270: self.gridLabel.getGridString(),
                    333: self.gridLabel.getLockString()
                }, 'Exif': {}, 'GPS': {
            }, 'Interop': {}, '1st': {}, 'thumbnail': None}
            exif_bytes = piexif.dump(exif_dict)
            img.save(fname[0], "JPEG", optimize=True,
                     quality=100, exif=exif_bytes)

    def open(self):
        folder = './generated/' if os.path.isdir('./generated/') else '.'
        fname = QFileDialog.getOpenFileName(
            self, 'Open file', folder, "Image files (*.jpg)")
        if fname[0] != '':
            exif = piexif.load(Image.open(fname[0]).info['exif'])
            if 333 in exif['0th'] and exif['0th'][333] != '':
                lock_numbers = exif['0th'][333].decode("UTF-8").rstrip('\n')
                lock = []
                for line in lock_numbers.split("\n"):
                    colors = list(map(lambda n: int(n) == 1, list(line)))
                    lock.append(colors)
                self.gridLabel.setLock(lock)
            grid_numbers = exif['0th'][270].decode("UTF-8").rstrip('\n')
            grid = []
            for line in grid_numbers.split("\n"):
                colors = list(map(lambda n: Color.fromValue(int(n)), list(line)))
                grid.append(colors)
            self.gridLabel.setGrid(grid)

    def quit(self):
        QCoreApplication.exit(0)

    def regenerate(self):
        grid = self.generate(self.gridLabel.getLock())
        self.gridLabel.setGrid(grid)

    def generate(self, lock):
        return generate_grid_whithout_collision(lock)


if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    w = Swapper()
    w.show()
    app.exec_()
