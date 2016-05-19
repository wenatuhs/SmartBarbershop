# !/usr/bin/python
# -*- coding: utf-8 -*-

"""
Smart Barbershop Barber Client GUI

This code is part of the demo of Smart Barbershop System.

author: Zhe Zhang
email: wenatuhs@gmail.com
last edited: May 17, 2016
"""

import sys
import warnings

from PyQt4 import QtGui, QtCore
from customer import normt, errort, notifyt, barbercard, StatusQLabel, SERVICES

__version__ = '0.8'


def customercard(title='Customer Info', customer=None):
    if customer is None:
        id = QtGui.QLabel('ID: {}'.format('wena'))
        name = QtGui.QLabel('Name: {}'.format('Zhe'))
        service = QtGui.QLabel('Services: {}'.format('Hair Cut'))
    else:
        id = QtGui.QLabel('ID: {}'.format(customer.uid))
        if customer.pwd:
            name = QtGui.QLabel('Name: {}'.format(customer.name))
        _service = ', '.join([SERVICES[sv] for sv in customer.service])
        service = QtGui.QLabel('Service: {}'.format(_service))

    customer_info = QtGui.QVBoxLayout()
    customer_info.addWidget(id)
    try:
        customer_info.addWidget(name)
    except:
        pass
    customer_info.addWidget(service)
    if title:
        pbox = QtGui.QGroupBox(title)
        pbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
    else:
        pbox = QtGui.QGroupBox()
    pbox.setLayout(customer_info)

    return pbox


def queuescroll(title=None, barber=None):
    server = barber.get_server()
    queue_vbox = QtGui.QVBoxLayout()
    for cus in barber.queue:
        queue_vbox.addWidget(customercard(title, server.customers[cus[0]]))
    queue_vbox.addStretch(1)
    queue_panel = QtGui.QGroupBox('Queue')
    queue_panel.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
    queue_panel.setLayout(queue_vbox)
    scroll = QtGui.QScrollArea()
    scroll.setWidget(queue_panel)
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet('QScrollArea  {border-radius: 10px;}')
    scroll.setFixedHeight(170)
    scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    return scroll


class BarberWindow(QtGui.QMainWindow):
    def __init__(self, barber=None, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.barber = barber
        self.barber.link_window(self)
        self.initUI()

    def initUI(self):
        # Set transparent background
        p = self.palette()
        color = p.color(QtGui.QPalette.Background)
        p.setColor(self.backgroundRole(),
                   QtGui.QColor(color.red(), color.green(), color.blue(), 0xff))
        self.setPalette(p)
        # Set main widget
        self.stack = QtGui.QStackedWidget()
        self.setCentralWidget(self.stack)
        self.login = Login(self)
        self.register = Register(self)
        self.workspace = WorkSpace(self)
        self.stack.addWidget(self.login)
        self.stack.addWidget(self.register)
        self.stack.addWidget(self.workspace)
        self.stack.setCurrentWidget(self.login)

        self.status = StatusQLabel(normt('Welcome!'))
        font = QtGui.QFont("Sans Serif", 9, QtGui.QFont.Light)
        self.status.setFont(font)
        bar = self.statusBar()
        bar.setStyleSheet("QStatusBar{background:lightgray;}")
        bar.setSizeGripEnabled(False)
        bar.addWidget(QtGui.QLabel(' '))
        bar.addWidget(self.status, 1)

        self.setWindowTitle('Smart Barbershop Barber Client {}'.format(__version__))
        self.setFixedSize(320, 480)
        self.show()
        self.setGeometry(1110, 50, 320, 480)
        # self.center()

    def closeEvent(self, e):
        try:
            self.barber.disconnect()
        except:
            warnings.warn('no barber attached!')
        super().closeEvent(e)

    def center(self):
        qr = self.frameGeometry()
        qr.moveCenter(QtGui.QDesktopWidget().availableGeometry().center())
        self.move(qr.topLeft())


class Login(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        welcome = QtGui.QLabel()
        pixmap = QtGui.QPixmap('images/welcome.png')
        welcome.setPixmap(pixmap)

        username = QtGui.QLabel('Nickname')
        self.usr = QtGui.QLineEdit()
        grid = QtGui.QGridLayout()
        grid.addWidget(username, 0, 0)
        grid.addWidget(self.usr, 0, 1)
        self.logbox = QtGui.QGroupBox('Login')
        self.logbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        self.logbox.setLayout(grid)

        login_btn = QtGui.QPushButton('Login')
        login_btn.resize(login_btn.sizeHint())
        login_btn.clicked.connect(self.login)
        reg_btn = QtGui.QPushButton('Register')
        reg_btn.setStyleSheet('QPushButton {color: gray; font-size: 9px;}')
        reg_btn.setFixedSize(40, 15)
        reg_btn.setFlat(True)
        reg_btn.resize(reg_btn.sizeHint())
        reg_btn.clicked.connect(self.go_register)
        btns = QtGui.QHBoxLayout()
        btns.addWidget(reg_btn)
        btns.addWidget(login_btn, 1)
        self.btns = QtGui.QFrame()
        self.btns.setLayout(btns)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(welcome)
        layout.addStretch(1)
        layout.addWidget(self.logbox)
        layout.addWidget(self.btns)
        self.setLayout(layout)

    def login(self):
        parent = self.parent
        barber = parent.barber
        nickname = self.usr.text()
        fail = barber.login(nickname)

        if not fail:
            parent.stack.setCurrentWidget(parent.workspace)
            parent.workspace.stack.removeWidget(parent.workspace.stack.currentWidget())
            card = barbercard('Profile', barber, False)
            parent.workspace.stack.addWidget(card)
            parent.workspace.stack.setCurrentWidget(card)
            parent.workspace.qstack.removeWidget(parent.workspace.qstack.currentWidget())
            scroll = queuescroll(None, barber)
            parent.workspace.qstack.addWidget(scroll)
            parent.workspace.qstack.setCurrentWidget(scroll)
            _msg = 'Hello {}!'.format(barber.name)
            parent.workspace.welcome.setText(_msg)
            _msg = 'Hello {}, are you ready for the customers?'.format(barber.name)
            parent.status.setText(notifyt(_msg))
            # Notify all connected customers
            self.notify_all_customers()
        else:
            parent.status.setText(errort('Incorrect nickname, please try again!'))

    def go_register(self):
        parent = self.parent
        parent.stack.setCurrentWidget(parent.register)
        parent.status.setText(notifyt('Please fill in your info!'))

    def notify_all_customers(self, kind='add'):
        parent = self.parent
        barber = parent.barber
        server = barber.get_server()
        for cus in server.customers.values():
            window = cus.window
            if kind == 'add':
                card = barbercard(barber=barber)
                window.appointment.stack.addWidget(card)
                window.appointment.barbercards[barber.name] = card
                window.appointment.bcombo.addItem(barber.name)
            elif kind == 'remove':
                idx = window.appointment.bcombo.findText(barber.name)
                window.appointment.bcombo.removeItem(idx)
                card = window.appointment.barbercards[barber.name]
                window.appointment.stack.removeWidget(card)
                del card
            elif kind == 'modify':
                card = barbercard(barber=barber)
                window.appointment.stack.addWidget(card)
                if window.appointment.bcombo.currentText() == barber.name:
                    window.appointment.stack.setCurrentWidget(card)
                _card = window.appointment.barbercards[barber.name]
                window.appointment.stack.removeWidget(_card)
                window.appointment.barbercards[barber.name] = card
                del _card


class Register(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        font = QtGui.QFont("Sans Serif", 21, QtGui.QFont.Bold)
        title = QtGui.QLabel('Please fill in your info!')
        title.setFont(font)
        details = QtGui.QLabel('And welcome to join us:)')
        details.setStyleSheet('QLabel  {color: gray; font-size: 12px; font-weight: regular;}')
        info = QtGui.QVBoxLayout()
        info.addWidget(title)
        info.addWidget(details)

        usrid = QtGui.QLabel('ID')
        nickname = QtGui.QLabel('Nickname')
        gender = QtGui.QLabel('Gender')
        age = QtGui.QLabel('Age')
        level = QtGui.QLabel('Level')
        worktime = QtGui.QLabel('Work Time')
        to = QtGui.QLabel('to')
        server = self.parent.barber.get_server()
        uid = server.new_barber_id()
        self.reg_usrid = QtGui.QLineEdit(uid)
        self.reg_usrid.setEnabled(False)
        self.reg_nickname = QtGui.QLineEdit()
        self.reg_gender = QtGui.QComboBox()
        self.reg_gender.addItems(['M', 'F'])
        self.reg_age = QtGui.QLineEdit()
        self.reg_level = QtGui.QComboBox()
        self.reg_level.addItems(['Senior', 'Director', 'Chief'])
        self.reg_worktime_a = QtGui.QLineEdit()
        self.reg_worktime_a.setText('8')
        self.reg_worktime_b = QtGui.QLineEdit()
        self.reg_worktime_b.setText('22')
        grid = QtGui.QGridLayout()
        grid.addWidget(usrid, 0, 0)
        grid.addWidget(self.reg_usrid, 0, 1, 1, 3)
        grid.addWidget(nickname, 1, 0)
        grid.addWidget(self.reg_nickname, 1, 1, 1, 3)
        grid.addWidget(gender, 2, 0)
        grid.addWidget(self.reg_gender, 2, 1, 1, 3)
        grid.addWidget(age, 3, 0)
        grid.addWidget(self.reg_age, 3, 1, 1, 3)
        grid.addWidget(level, 4, 0)
        grid.addWidget(self.reg_level, 4, 1, 1, 3)
        grid.addWidget(worktime, 5, 0)
        grid.addWidget(self.reg_worktime_a, 5, 1)
        grid.addWidget(to, 5, 2)
        grid.addWidget(self.reg_worktime_b, 5, 3)
        self.regbox = regbox = QtGui.QGroupBox('Register')
        regbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        regbox.setLayout(grid)

        login_btn = QtGui.QPushButton('Register')
        login_btn.resize(login_btn.sizeHint())
        login_btn.clicked.connect(self.register)
        guest_btn = QtGui.QPushButton('Cancel')
        guest_btn.resize(guest_btn.sizeHint())
        guest_btn.clicked.connect(self.cancel)
        btns = QtGui.QHBoxLayout()
        btns.addWidget(guest_btn, 1)
        btns.addWidget(login_btn, 2)
        self.btns = QtGui.QFrame()
        self.btns.setLayout(btns)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(info)
        layout.addWidget(self.regbox)
        layout.addStretch(1)
        layout.addWidget(self.btns)
        self.setLayout(layout)

    def register(self):
        parent = self.parent
        barber = parent.barber
        uid = self.reg_usrid.text()
        nickname = self.reg_nickname.text()
        gender = self.reg_gender.currentText()
        age = int(self.reg_age.text())
        level = self.reg_level.currentText()
        worktime_a = int(self.reg_worktime_a.text())
        worktime_b = int(self.reg_worktime_b.text())
        fail = barber.register(uid, nickname, gender, age, level, [worktime_a, worktime_b])

        if not fail:
            parent.stack.setCurrentWidget(parent.workspace)
            parent.workspace.stack.removeWidget(parent.workspace.stack.currentWidget())
            card = barbercard('Profile', barber, False)
            parent.workspace.stack.addWidget(card)
            parent.workspace.stack.setCurrentWidget(card)
            parent.workspace.qstack.removeWidget(parent.workspace.qstack.currentWidget())
            scroll = queuescroll(None, barber)
            parent.workspace.qstack.addWidget(scroll)
            parent.workspace.qstack.setCurrentWidget(scroll)
            _msg = 'Hello {}!'.format(barber.name)
            parent.workspace.welcome.setText(_msg)
            _msg = 'Hello {}, are you ready for the customers?'.format(barber.name)
            parent.status.setText(notifyt(_msg))
            parent.login.notify_all_customers()
        else:
            parent.status.setText(errort(
                'Nickname {} is already taken, please choose another one!'.format(nickname)))

    def cancel(self):
        parent = self.parent
        parent.stack.setCurrentWidget(parent.login)
        parent.status.setText(normt('Welcome!'))


class WorkSpace(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        parent = self.parent
        barber = parent.barber
        server = barber.get_server()

        font = QtGui.QFont("Sans Serif", 21, QtGui.QFont.Bold)
        _msg = 'Hello {}!'.format('Darling')
        self.welcome = QtGui.QLabel(_msg)
        self.welcome.setFont(font)
        self.clock = QtGui.QLabel(barber.get_server().current_time)
        self.clock.setStyleSheet('QLabel  {color: gray; font-size: 12px; font-weight: regular;}')
        info = QtGui.QVBoxLayout()
        info.addWidget(self.welcome)
        info.addWidget(self.clock)

        self.stack = QtGui.QStackedWidget()
        self.stack.addWidget(barbercard('Profile', barber, False))

        self.qstack = QtGui.QStackedWidget()
        self.qstack.addWidget(queuescroll(None, barber))

        self.next_btn = QtGui.QPushButton('Ready')
        self.next_btn.resize(self.next_btn.sizeHint())
        self.next_btn.clicked.connect(self.next)
        self.skip_btn = QtGui.QPushButton('Skip')
        self.skip_btn.resize(self.skip_btn.sizeHint())
        self.skip_btn.clicked.connect(self.skip)
        self.skip_btn.setEnabled(False)
        self.fin_btn = QtGui.QPushButton('Finish')
        self.fin_btn.resize(self.fin_btn.sizeHint())
        self.fin_btn.clicked.connect(self.finish)

        btns = QtGui.QHBoxLayout()
        btns.addWidget(self.next_btn)
        btns.addWidget(self.skip_btn)
        btns.addWidget(self.fin_btn)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(info)
        layout.addWidget(self.stack)
        layout.addWidget(self.qstack)
        layout.addStretch(1)
        layout.addLayout(btns)
        self.setLayout(layout)

    def update_queue(self, done=False):
        parent = self.parent
        barber = parent.barber
        self.qstack.removeWidget(self.qstack.currentWidget())
        scroll = queuescroll(None, barber)
        self.qstack.addWidget(scroll)
        self.qstack.setCurrentWidget(scroll)
        if not done:
            self.next_btn.setEnabled(True)
            self.fin_btn.setEnabled(False)
            _msg = 'Customer {} is in your queue now.'.format(barber.queue[-1][0])
            parent.status.setText(notifyt(_msg))
        else:
            try:
                _msg = 'Good job! Your next customer is {}.'.format(barber.queue[0][0])
            except IndexError:
                self.next_btn.setEnabled(False)
                self.fin_btn.setEnabled(True)
                _msg = "Nicely done! You don't have any customer for now, please take a break:)"
            parent.status.setText(notifyt(_msg))

    def update_review(self):
        parent = self.parent
        barber = parent.barber
        self.stack.removeWidget(self.stack.currentWidget())
        card = barbercard('Profile', barber, False)
        self.stack.addWidget(card)
        self.stack.setCurrentWidget(card)
        self.temp = parent.status.text()
        parent.status.setText(notifyt("You got a review from your customer!"))
        parent.login.notify_all_customers('modify')

    def next(self):
        if self.next_btn.text() == 'Ready':
            self.parent.barber.ready()
            self.next_btn.setText('Next')
            self.next_btn.setEnabled(False)
            self.parent.status.setText(normt("Alright let's rock!"))
        elif self.next_btn.text() == 'Next':
            self.parent.barber.ready()
            self.next_btn.setText('Begin')
            self.skip_btn.setEnabled(True)
        elif self.next_btn.text() == 'Begin':
            self.parent.barber.begin()
            self.next_btn.setText('Done')
        else:
            self.parent.barber.done()
            self.next_btn.setText('Next')
            self.skip_btn.setEnabled(False)

    def skip(self):
        pass

    def finish(self):
        parent = self.parent
        barber = parent.barber
        parent.login.notify_all_customers('remove')
        barber.logout()

        self.next_btn.setText('Ready')
        self.next_btn.setEnabled(True)
        parent.stack.setCurrentWidget(parent.login)
        parent.status.setText(normt('Welcome!'))


def main():
    app = QtGui.QApplication(sys.argv)
    ex = BarberWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
