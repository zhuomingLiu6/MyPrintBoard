# encoding:utf8

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import copy

class Main(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.resize(1000, 1000) 

        #插入按钮
        self.btn = QPushButton()
        self.btn.clicked.connect(self.loadFile)
        self.btn.setText("读入照片")
        layout.addWidget(self.btn)

        self.btn1 = QPushButton()
        self.btn1.clicked.connect(self.save_file)
        self.btn1.setText("保存照片")
        layout.addWidget(self.btn1)


        self.widget = ImageWithMouseControl(self)
        self.setWindowTitle('Image with mouse control')
        layout.addWidget(self.widget)

        self.btn2 = QPushButton()
        self.btn2.clicked.connect(self.widget.reopen)
        self.btn2.setText("还原图片")
        layout.addWidget(self.btn2)

        self.setLayout(layout)

    def loadFile(self):
        #加载文件
        fname, _ = QFileDialog.getOpenFileName(self, '选择图片', 'c:\\', 'Image files(*.jpg *.gif *.png)')
        self.widget.img = QPixmap(fname)
        self.widget.ori = QPixmap(fname)
        self.resize(self.widget.img.size())  

    def save_file(self):
        # 保存文件
        file_name,_ = QFileDialog.getSaveFileName(self,"文件保存","D:/imagetest/save","All Files (*);;Text Files (*.png)")
        self.widget.img.save(file_name)


class ImageWithMouseControl(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.img = QPixmap(1000,1000)
        self.img.fill(Qt.transparent)
        # 作为备用的用于还原
        self.ori = QPixmap(1000,1000)
        self.ori.fill(Qt.transparent)

        #self.scaled_img = self.img
        self.scaled_img = self.img.scaled(self.size())
        self.point = QPoint(0, 0)
        self.pen = QPen(Qt.black, 2, Qt.SolidLine)
        self.pos_xy = []

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.draw_img(painter)
        painter.end()
    
    def draw_img(self, painter):
        painter.drawPixmap(self.point, self.scaled_img)


    def reopen(self):
        self.img = self.ori
        self.scaled_img = self.img
        self.repaint()
    
    def mouseMoveEvent(self, event):
        #先在img画布上画
        pos_tmp = (event.pos().x(), event.pos().y())
        self.pos_xy.append(pos_tmp)
        painter = QPainter(self.img)
        painter.setPen(self.pen)
        if len(self.pos_xy) > 1:
            point_start = self.pos_xy[0] 
            for pos_tmp in self.pos_xy:
                painter.drawLine(point_start[0], point_start[1], pos_tmp[0], pos_tmp[1])
                point_start = pos_tmp
        #再更新img画布到scaled_img的尺寸
        self.scaled_img = self.img.scaled(self.scaled_img.size())
        #刷新画布
        self.repaint()

    def mouseReleaseEvent(self, event):
        self.pos_xy = []

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            # 放大图片
            self.scaled_img = self.img.scaled(self.scaled_img.width()-5, self.scaled_img.height()-5)
            new_w = event.x() - (self.scaled_img.width() * (event.x() - self.point.x())) / (self.scaled_img.width() + 5)
            new_h = event.y() - (self.scaled_img.height() * (event.y() - self.point.y())) / (self.scaled_img.height() + 5)
            self.point = QPoint(new_w, new_h)
            self.repaint()
        elif event.angleDelta().y() < 0:
            # 缩小图片
            self.scaled_img = self.img.scaled(self.scaled_img.width()+5, self.scaled_img.height()+5)
            new_w = event.x() - (self.scaled_img.width() * (event.x() - self.point.x())) / (self.scaled_img.width() - 5)
            new_h = event.y() - (self.scaled_img.height() * (event.y() - self.point.y())) / (self.scaled_img.height() - 5)
            self.point = QPoint(new_w, new_h)
            self.repaint()

    def resizeEvent(self, event):
        #窗口大小调整
        if self.parent is not None:
            self.scaled_img = self.img.scaled(self.size())
            self.point = QPoint(0, 0)
            self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    app.exec_()