# !/usr/bin/python
# -*- coding: utf-8 -*-

"""
Smart Barbershop Demo

This code is the demo of Smart Barbershop System.

author: Zhe Zhang
email: wenatuhs@gmail.com
last edited: May 16, 2016
"""

import sys
from PyQt4 import QtGui, QtCore
from sbscore import Server, CustomerEntry, BarberEntry, Customer, Barber
import customer, barber

__version__ = '0.9.5'


class DemoWindow(QtGui.QMainWindow):
    def __init__(self, server=None):
        super().__init__()
        self.server = server
        self.server.link_window(self)
        self.initUI()

    def initUI(self):
        # Set main widget
        self.stack = QtGui.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.demo = Demo(self)
        self.stack.addWidget(self.demo)
        self.stack.setCurrentWidget(self.demo)

        self.setWindowTitle('Smart Barbershop Demo {}'.format(__version__))
        self.setFixedSize(300, 300)
        self.show()
        self.setGeometry(1110, 50, 300, 300)
        # self.center()

    def closeEvent(self, e):
        super().closeEvent(e)

    def center(self):
        qr = self.frameGeometry()
        qr.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(qr.topLeft())


class Demo(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        newcus_btn = QtGui.QPushButton('New Customer')
        newbar_btn = QtGui.QPushButton('New Barber')
        save_btn = QtGui.QPushButton('Save')
        newcus_btn.clicked.connect(self.new_customer)
        newbar_btn.clicked.connect(self.new_barber)
        save_btn.clicked.connect(self.save_status)
        hbox = QtGui.QGridLayout()
        hbox.addWidget(newcus_btn, 0, 0)
        hbox.addWidget(newbar_btn, 0, 1)
        hbox.addWidget(save_btn, 1, 1)
        gbox = QtGui.QGroupBox('Control')
        gbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        gbox.setLayout(hbox)

        self.log = QtGui.QTextEdit()
        self.log.setReadOnly(True)
        lhbox = QtGui.QHBoxLayout()
        lhbox.addWidget(self.log)
        lbox = QtGui.QGroupBox('Log')
        lbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        lbox.setLayout(lhbox)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(gbox)
        layout.addWidget(lbox, 1)
        self.setLayout(layout)

    def new_customer(self):
        c = Customer()
        c.connect()
        customer.CustomerWindow(c, self)

    def new_barber(self):
        b = Barber()
        b.connect()
        barber.BarberWindow(b, self)

    def save_status(self):
        self.parent.server.save()


class OutLog:
    def __init__(self, edit, out=None, color=None):
        """(edit, out=None, color=None) -> can write stdout, stderr to a
        QTextEdit.
        edit = QTextEdit
        out = alternate stream ( can be the original sys.stdout )
        color = alternate color (i.e. color stderr a different color)
        """
        self.edit = edit
        self.out = out
        self.color = color
        self.flush = lambda: None  # eliminate the warning message by doing nothing

    def write(self, m):
        self.edit.moveCursor(QtGui.QTextCursor.End)
        if self.color:
            tc = self.edit.textColor()
            self.edit.setTextColor(self.color)
        self.edit.insertPlainText(m)

        if self.color:
            self.edit.setTextColor(tc)

        if self.out:
            self.out.write(m)


def main():
    SERVERS = {}
    server = Server('s0', 'Big Boss')

    # Open the demo window
    app = QtGui.QApplication(sys.argv)
    demo = DemoWindow(server)
    # Redirect the standard output and error
    sys.stdout = OutLog(demo.demo.log, sys.stdout, QtGui.QColor(0, 0, 0))
    # sys.stderr = OutLog(demo.demo.log, sys.stderr, QtGui.QColor(255, 0, 0))

    # Server online
    server.connect()

    # Barbers online
    # barbers = []
    # for i in range(5):
    #     b = Barber('b{}'.format(i + 1))
    #     b.connect()
    #     b.ready(init=True)
    #     barbers.append(b)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
