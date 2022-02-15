#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import os.path
import io
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from grid import generate_grid_whithout_collision
from colors import Color
from PIL import Image
import piexif


class GridLabel(QLabel):
    def __init__(self, parent, grid):
        QLabel.__init__(self, parent)
        self.grid = grid
        self.clip = None
        self.images = {
            Color.GREEN_PINK_FLOWERS: QImage('img/GREEN_PINK_FLOWERS.jpg'),
            Color.WHITE_PINK_FLOWERS: QImage('img/WHITE_PINK_FLOWERS.jpg'),
            Color.WHITE_GREEN_DOTS: QImage('img/WHITE_GREEN_DOTS.jpg'),
            Color.PINK: QImage('img/PINK.jpg'),
            Color.LIGHT_PINK_PINK_DOTS: QImage('img/LIGHT_PINK_PINK_DOTS.jpg'),
        }
        self.resize(720, 315)

    def setGrid(self, grid):
        self.grid = grid
        self.clip = None
        self.repaint(0, 0, 720, 315)

    def getGridString(self):
        s = ""
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                s += str(self.grid[i][j].value)
            s += "\n"
        return s

    def toImage(self):
        img = QImage(720, 315, QImage.Format.Format_RGB32)
        painter = QPainter(img)
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                cell = self.grid[y][x]
                painter.drawImage(QPoint(x*45, y*45), self.images[cell])
        return img

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                cell = self.grid[y][x]
                painter.drawImage(QPoint(x*45, y*45), self.images[cell])
        if self.clip != None:
            painter.fillRect(self.clip[1]*45, self.clip[0]
                             * 45, 45, 45, QColor.fromRgb(255, 0, 0, 64))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = int(event.x()/45)
            y = int(event.y()/45)
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
            self.repaint(0, 0, 720, 315)


class Swapper(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Tile swapper")
        self.resize(750, 365)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.gridLabel = GridLabel(self, self.generate())
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
            exif_dict = {'0th': {270: self.gridLabel.getGridString()}, 'Exif': {}, 'GPS': {
            }, 'Interop': {}, '1st': {}, 'thumbnail': None}
            exif_bytes = piexif.dump(exif_dict)
            img.save(fname[0], "JPEG", optimize=True,
                     quality=100, exif=exif_bytes)

    def open(self):
        folder = './generated/' if os.path.isdir('./generated/') else '.'
        fname = QFileDialog.getOpenFileName(
            self, 'Open file', folder, "Image files (*.jpg)")
        if fname[0] != '':
            grid_numbers = piexif.load(Image.open(fname[0]).info['exif'])[
                '0th'][270].decode("UTF-8").rstrip('\n')
            grid = []
            for line in grid_numbers.split("\n"):
                colors = list(map(lambda n: Color.fromValue(int(n)), list(line)))
                grid.append(colors)
            self.gridLabel.setGrid(grid)

    def quit(self):
        QCoreApplication.exit(0)

    def regenerate(self):
        grid = self.generate()
        self.gridLabel.setGrid(grid)

    def generate(self):
        return generate_grid_whithout_collision()


if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    w = Swapper()
    w.show()
    app.exec_()
