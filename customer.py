# !/usr/bin/python
# -*- coding: utf-8 -*-

"""
Smart Barbershop Customer Client GUI

This code is part of the demo of Smart Barbershop System.

author: Zhe Zhang
email: wenatuhs@gmail.com
last edited: May 16, 2016
"""

import os
import sys
from datetime import datetime
import warnings

from PyQt4 import QtGui, QtCore

__version__ = '0.8'
SERVICES = {'haircut': 'Hair Cut', 'wash': 'Wash', 'protect': 'Protect'}


class StatusQLabel(QtGui.QLabel):
    def __init__(self, p_str, parent=None, duration=3000, kind='barber'):
        super().__init__(p_str, parent)
        self.duration = duration
        self.hold = 0
        self.timer = QtCore.QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.update_time)

    def setText(self, p_str):
        super().setText(p_str)
        self.hold += 1
        QtCore.QTimer.singleShot(self.duration, self.release)

    def release(self):
        self.hold -= 1
        if not self.hold:
            self.update_time()

    def update_time(self):
        if not self.hold:
            super().setText(normt(datetime.now().strftime('%Y-%m-%d %H:%M')))


class ExtendedQLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mouseReleaseEvent(self, ev):
        print('clicked')
        # self.emit(QtCore.SIGNAL('clicked()'))


def barbercard(title='Barber Info', barber=None, showtime=True):
    try:
        server = barber.get_server()
        name = QtGui.QLabel('Name: {}'.format(barber.name))
        gender = QtGui.QLabel('Gender: {}'.format(barber.gender))
        age = QtGui.QLabel('Age: {}'.format(barber.age))
        level = QtGui.QLabel('Level: {}'.format(barber.level))
        ratings = QtGui.QLabel('Ratings: {:.1f} Stars'.format(server.bdb[barber.uid].ratings))
        ratings.setStyleSheet('QLabel  {color: darkgreen; font-size: 12px; font-weight: bold;}')
        if showtime:
            hours, mins = barber.wait_time()
            if hours:
                if mins:
                    time = QtGui.QLabel('Waiting Time: {0}h {1} min'.format(hours, mins))
                else:
                    time = QtGui.QLabel('Waiting Time: {}h'.format(hours))
            else:
                time = QtGui.QLabel('Waiting Time: {} min'.format(mins))
            time.setStyleSheet('QLabel  {color: darkred; font-size: 12px; font-weight: bold;}')
        pic = ExtendedQLabel()
        try:
            fname = [f for f in os.listdir('avatars') if f.startswith(barber.name)][0]
            pixmap = QtGui.QPixmap('avatars/{}'.format(fname))
        except IndexError:
            fname = 'male.png' if barber.gender == 'M' else 'female.png'
            pixmap = QtGui.QPixmap('avatars/{}'.format(fname))
        pic.setPixmap(pixmap)
    except:
        name = QtGui.QLabel('Name: {}'.format('John'))
        gender = QtGui.QLabel('Gender: {}'.format('M'))
        age = QtGui.QLabel('Age: {}'.format(22))
        level = QtGui.QLabel('Level: {}'.format('senior'))
        ratings = QtGui.QLabel('Ratings: {:.1f} Stars'.format(5))
        ratings.setStyleSheet('QLabel  {color: darkgreen; font-size: 12px; font-weight: bold;}')
        time = QtGui.QLabel('Waiting Time: 1h')
        time.setStyleSheet('QLabel  {color: darkred; font-size: 12px; font-weight: bold;}')
        pic = ExtendedQLabel()
        pixmap = QtGui.QPixmap('avatars/{}.jpg'.format('John'))
        pic.setPixmap(pixmap)

    barber_info = QtGui.QVBoxLayout()
    barber_info.addWidget(name)
    barber_info.addWidget(gender)
    barber_info.addWidget(age)
    barber_info.addWidget(level)
    barber_info.addWidget(ratings)
    if showtime:
        barber_info.addWidget(time)
    barber_info.addStretch(1)
    image = QtGui.QVBoxLayout()
    image.addWidget(pic)
    person = QtGui.QHBoxLayout()
    person.addLayout(barber_info)
    person.addStretch(1)
    person.addLayout(image)
    if title:
        pbox = QtGui.QGroupBox(title)
        pbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
    else:
        pbox = QtGui.QGroupBox()
    pbox.setLayout(person)

    return pbox


def sumcard(title='Summary', bname='', serstr='', startstr='', endstr='', durstr=''):
    service = QtGui.QLabel('Service: {}'.format(serstr))
    barber = QtGui.QLabel('Barber: {}'.format(bname))
    start = QtGui.QLabel('Start Time: {}'.format(startstr))
    end = QtGui.QLabel('End Time: {}'.format(endstr))
    time = QtGui.QLabel('Duration: {}'.format(durstr))

    service_info = QtGui.QGridLayout()
    service_info.addWidget(service, 0, 0)
    service_info.addWidget(barber, 1, 0)
    service_info.addWidget(start, 0, 1)
    service_info.addWidget(end, 1, 1)
    service_info.addWidget(time, 2, 1)

    sbox = QtGui.QGroupBox(title)
    sbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
    sbox.setLayout(service_info)

    return sbox


def normt(m):
    return '<font color=\"dimgray\">{}</font>'.format(m)


def errort(m):
    return '<font color=\"darkred\">{}</font>'.format(m)


def notifyt(m):
    return '<font color=\"darkgreen\">{}</font>'.format(m)


class CustomerWindow(QtGui.QMainWindow):
    def __init__(self, customer=None, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.customer = customer
        self.customer.link_window(self)
        self.initUI()

    def initUI(self):
        # Set main widget
        self.stack = QtGui.QStackedWidget(self)
        self.setCentralWidget(self.stack)
        self.login = Login(self)
        self.appointment = Appointment(self)
        self.suggestion = Suggestion(self)
        self.service = Service(self)
        self.process = Process(self)
        self.finish = Finish(self)
        self.stack.addWidget(self.login)
        self.stack.addWidget(self.appointment)
        self.stack.addWidget(self.suggestion)
        self.stack.addWidget(self.service)
        self.stack.addWidget(self.process)
        self.stack.addWidget(self.finish)
        self.stack.setCurrentWidget(self.login)

        self.status = StatusQLabel(normt('Welcome!'))
        font = QtGui.QFont("Sans Serif", 9, QtGui.QFont.Light)
        self.status.setFont(font)
        bar = self.statusBar()
        bar.setStyleSheet("QStatusBar{background:lightgray;}")
        bar.setSizeGripEnabled(False)
        bar.addWidget(QtGui.QLabel(' '))
        bar.addWidget(self.status, 1)

        self.setWindowTitle('Smart Barbershop Customer Client {}'.format(__version__))
        self.setFixedSize(320, 480)
        self.show()
        self.setGeometry(1110, 50, 320, 480)
        # self.center()

    def closeEvent(self, e):
        try:
            self.customer.disconnect()
        except:
            warnings.warn('no customer attached!')
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

        username = QtGui.QLabel('Username')
        password = QtGui.QLabel('Password')
        self.usr = QtGui.QLineEdit()
        self.pwd = QtGui.QLineEdit()
        self.pwd.setEchoMode(QtGui.QLineEdit.Password)
        grid = QtGui.QGridLayout()
        grid.addWidget(username, 0, 0)
        grid.addWidget(self.usr, 0, 1)
        grid.addWidget(password, 1, 0)
        grid.addWidget(self.pwd, 1, 1)
        self.logbox = logbox = QtGui.QGroupBox('Login')
        logbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        logbox.setLayout(grid)

        username = QtGui.QLabel('Username')
        password = QtGui.QLabel('Password')
        nickname = QtGui.QLabel('Nickname')
        self.reg_usr = QtGui.QLineEdit()
        self.reg_pwd = QtGui.QLineEdit()
        self.reg_nic = QtGui.QLineEdit()
        self.reg_pwd.setEchoMode(QtGui.QLineEdit.Password)
        grid = QtGui.QGridLayout()
        grid.addWidget(username, 0, 0)
        grid.addWidget(self.reg_usr, 0, 1)
        grid.addWidget(password, 1, 0)
        grid.addWidget(self.reg_pwd, 1, 1, 1, 3)
        grid.addWidget(nickname, 0, 2)
        grid.addWidget(self.reg_nic, 0, 3)
        self.regbox = regbox = QtGui.QGroupBox('Register')
        regbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        regbox.setLayout(grid)

        self.stack = QtGui.QStackedWidget()
        self.stack.addWidget(self.logbox)
        self.stack.addWidget(self.regbox)
        self.stack.setCurrentWidget(self.logbox)

        login_btn = QtGui.QPushButton('Login')
        login_btn.resize(login_btn.sizeHint())
        login_btn.clicked.connect(self.login)
        guest_btn = QtGui.QPushButton('Guest')
        guest_btn.resize(guest_btn.sizeHint())
        guest_btn.clicked.connect(self.guest_login)
        reg_btn = QtGui.QPushButton('Register')
        reg_btn.setStyleSheet('QPushButton {color: gray; font-size: 9px;}')
        reg_btn.setFixedSize(40, 15)
        reg_btn.setFlat(True)
        reg_btn.resize(reg_btn.sizeHint())
        reg_btn.clicked.connect(self.go_register)
        btns = QtGui.QHBoxLayout()
        btns.addWidget(reg_btn)
        btns.addWidget(login_btn, 1)
        btns.addWidget(guest_btn, 1)
        self.btns1 = QtGui.QFrame()
        self.btns1.setLayout(btns)

        login_btn = QtGui.QPushButton('Register')
        login_btn.resize(login_btn.sizeHint())
        login_btn.clicked.connect(self.register)
        guest_btn = QtGui.QPushButton('Cancel')
        guest_btn.resize(guest_btn.sizeHint())
        guest_btn.clicked.connect(self.cancel)
        btns = QtGui.QHBoxLayout()
        btns.addWidget(guest_btn, 1)
        btns.addWidget(login_btn, 2)
        self.btns2 = QtGui.QFrame()
        self.btns2.setLayout(btns)

        self.bstack = QtGui.QStackedWidget()
        self.bstack.addWidget(self.btns1)
        self.bstack.addWidget(self.btns2)
        self.bstack.setCurrentWidget(self.btns1)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(welcome, 1)
        layout.addWidget(self.stack)
        layout.addWidget(self.bstack)
        self.setLayout(layout)

    def login(self):
        customer = self.parent.customer
        username = self.usr.text()
        password = self.pwd.text()
        fail = customer.login(username, password)

        parent = self.parent
        if not fail:
            parent.appointment.reset()
            parent.stack.setCurrentWidget(parent.appointment)
            parent.appointment.out_btn.setText('Logout')
            parent.appointment.out_btn.clicked.disconnect()
            parent.appointment.out_btn.clicked.connect(parent.appointment.logout)
            _msg = 'Hello, {}!'.format(customer.name if customer.name else customer.uid)
            parent.appointment.welcome.setText(_msg)
            if parent.appointment.bcombo.currentText():
                _msg = 'Good day {}, please choose your barber and services!'.format(
                    customer.name if customer.name else customer.uid)
                parent.status.setText(notifyt(_msg))
            else:
                _msg = 'Good day {}, but it seems that no barber is at work now...'.format(
                    customer.name if customer.name else customer.uid)
                parent.status.setText(errort(_msg))
        else:
            parent.status.setText(errort('Incorrect username or password, please try again!'))

    def go_register(self):
        self.stack.setCurrentWidget(self.regbox)
        self.bstack.setCurrentWidget(self.btns2)
        self.parent.status.setText(notifyt('Please fill in your info!'))

    def register(self):
        customer = self.parent.customer
        username = self.reg_usr.text()
        password = self.reg_pwd.text()
        nickname = self.reg_nic.text() if self.reg_nic.text() else None
        fail = customer.register(username, password, nickname)

        parent = self.parent
        if not fail:
            self.reset_login()
            parent.appointment.reset()
            parent.stack.setCurrentWidget(parent.appointment)
            parent.appointment.out_btn.setText('Logout')
            parent.appointment.out_btn.clicked.disconnect()
            parent.appointment.out_btn.clicked.connect(parent.appointment.logout)
            _msg = 'Hello, {}!'.format(customer.name if customer.name else customer.uid)
            parent.appointment.welcome.setText(_msg)
            if parent.appointment.bcombo.currentText():
                _msg = 'Welcome {}, please choose your barber and services!'.format(
                    customer.name if customer.name else customer.uid)
                parent.status.setText(notifyt(_msg))
            else:
                _msg = 'Welcome {}, but it seems that no barber is at work now...'.format(
                    customer.name if customer.name else customer.uid)
                parent.status.setText(errort(_msg))
        elif fail == 2:
            parent.status.setText(errort('Please choose a username!'))
        elif fail == 3:
            parent.status.setText(errort('Password must not be empty!'))
        else:
            parent.status.setText(errort(
                'Username {} is already taken, please choose another one!'.format(username)))

    def reset_login(self):
        self.stack.setCurrentWidget(self.logbox)
        self.bstack.setCurrentWidget(self.btns1)

    def cancel(self):
        self.reset_login()
        self.parent.status.setText(normt('Welcome!'))

    def guest_login(self):
        parent = self.parent
        customer = parent.customer
        parent.appointment.out_btn.setText('Back')
        parent.appointment.out_btn.clicked.disconnect()
        parent.appointment.out_btn.clicked.connect(parent.appointment.goback)
        parent.stack.setCurrentWidget(parent.appointment)
        _msg = 'Hello, {}!'.format('Darling')
        parent.appointment.welcome.setText(_msg)
        if parent.appointment.bcombo.currentText():
            if parent.appointment.do_btn.isEnabled():
                _msg = 'Good day {}, please choose your barber and services!'.format(customer.uid)
                parent.status.setText(notifyt(_msg))
            else:
                _msg = 'Please at least choose one service!'
                parent.status.setText(errort(_msg))
        else:
            _msg = 'Good day {}, but it seems that no barber is at work now...'.format(customer.uid)
            parent.status.setText(errort(_msg))


class Appointment(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        font = QtGui.QFont("Sans Serif", 21, QtGui.QFont.Bold)
        _msg = 'Hello {}!'.format('Darling')
        self.welcome = QtGui.QLabel(_msg)
        self.welcome.setFont(font)
        self.clock = QtGui.QLabel(self.parent.customer.get_server().current_time)
        self.clock.setStyleSheet('QLabel  {color: gray; font-size: 12px; font-weight: regular;}')
        info = QtGui.QVBoxLayout()
        info.addWidget(self.welcome)
        info.addWidget(self.clock)

        service = QtGui.QLabel('Service')
        barber = QtGui.QLabel('Barber')

        self.haircut = QtGui.QCheckBox('Hair Cut')
        self.wash = QtGui.QCheckBox('Wash')
        self.protect = QtGui.QCheckBox('Protect')
        self.haircut.setChecked(True)

        service_cb = QtGui.QGridLayout()
        service_cb.addWidget(self.haircut, 0, 0)
        service_cb.addWidget(self.wash, 0, 1)
        service_cb.addWidget(self.protect, 1, 0)
        serbox = QtGui.QGroupBox()
        serbox.setLayout(service_cb)

        self.stack = QtGui.QStackedWidget()
        self.bcombo = bcombo = QtGui.QComboBox()
        self.barbercards = {}
        customer = self.parent.customer
        server = customer.get_server()
        for bb in server.barbers.values():
            if not server.is_anon_barber_id(bb.uid):
                bcombo.addItem(bb.name)
                card = barbercard(barber=bb)
                self.stack.addWidget(card)
                self.barbercards[bb.name] = card
        bcombo.currentIndexChanged.connect(self.update_barberinfo)

        sug_btn = QtGui.QPushButton('Suggest')
        sug_btn.resize(sug_btn.sizeHint())
        sug_btn.clicked.connect(self.suggest)

        grid = QtGui.QGridLayout()
        grid.addWidget(service, 0, 0)
        grid.addWidget(serbox, 0, 1, 2, 3)
        grid.addWidget(barber, 2, 0)
        grid.addWidget(bcombo, 2, 1, 1, 2)
        grid.addWidget(sug_btn, 2, 3)
        gbox = QtGui.QGroupBox('Service')
        gbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        gbox.setLayout(grid)

        self.do_btn = QtGui.QPushButton('Put an Order')
        self.do_btn.resize(self.do_btn.sizeHint())
        self.out_btn = QtGui.QPushButton('Logout')
        self.out_btn.resize(self.out_btn.sizeHint())

        self.do_btn.clicked.connect(self.order)
        self.out_btn.clicked.connect(self.logout)
        self.haircut.stateChanged.connect(self.check_service)
        self.wash.stateChanged.connect(self.check_service)
        self.protect.stateChanged.connect(self.check_service)

        btns = QtGui.QHBoxLayout()
        btns.addWidget(self.out_btn, 1)
        btns.addWidget(self.do_btn, 2)

        self.update_barberinfo()

        layout = QtGui.QVBoxLayout()
        layout.addLayout(info)
        layout.addWidget(gbox)
        layout.addWidget(self.stack)
        layout.addStretch(1)
        layout.addLayout(btns)
        self.setLayout(layout)

    def reset(self):
        self.haircut.setChecked(True)
        self.wash.setChecked(False)
        self.protect.setChecked(False)
        self.bcombo.setCurrentIndex(0)

    def check_service(self):
        parent = self.parent
        if not (self.haircut.isChecked() or self.wash.isChecked() or self.protect.isChecked()):
            self.do_btn.setEnabled(False)
            parent.status.setText(errort('Please at least choose one service!'))
        else:
            if not self.do_btn.isEnabled():
                if self.bcombo.currentText():
                    self.do_btn.setEnabled(True)
                    parent.status.setText(
                        notifyt('Great! Now choose more services and/or pick up your barber:)'))
                else:
                    _msg = 'Sorry, it seems that no barber is at work now...'
                    parent.status.setText(errort(_msg))

    def update_barberinfo(self):
        name = self.bcombo.currentText()
        try:
            self.stack.setCurrentWidget(self.barbercards[name])
            if not self.do_btn.isEnabled():
                self.do_btn.setEnabled(True)
                _msg = 'Alright, you could choose your barber and services now!'
                self.parent.status.setText(notifyt(_msg))
        except KeyError:
            self.do_btn.setEnabled(False)
            try:
                _msg = 'Sorry, it seems that no barber is at work now...'
                self.parent.status.setText(errort(_msg))
            except AttributeError:
                pass

    def logout(self):
        customer = self.parent.customer
        customer.logout()

        parent = self.parent
        parent.stack.setCurrentWidget(parent.login)
        parent.status.setText(normt('Welcome!'))
        self.reset()

    def goback(self):
        parent = self.parent
        parent.stack.setCurrentWidget(parent.login)
        parent.status.setText(normt('Welcome!'))

    def order(self):
        parent = self.parent
        customer = parent.customer
        server = customer.get_server()
        # Get barber
        bname = self.bcombo.currentText()
        barber = [bb for bb in server.barbers.values() if
                  (not server.is_anon_barber_id(bb.uid)) and bb.name == bname][0]
        # Get services
        services = []
        if self.haircut.isChecked():
            services.append('haircut')
        if self.wash.isChecked():
            services.append('wash')
        if self.protect.isChecked():
            services.append('protect')
        # Make request
        fail = customer.request(barber.uid, services)
        # Update service panel
        if not fail:
            # parent.service.details.setText('{} will serve you shortly:)'.format(barber.name))
            parent.service.stack.removeWidget(parent.service.stack.currentWidget())
            card = barbercard('Your Barber', barber, False)
            parent.service.stack.addWidget(card)
            parent.service.stack.setCurrentWidget(card)
            _services = ', '.join([SERVICES[sv] for sv in services])
            parent.service.service.setText('Service: {}'.format(_services))
            parent.service.barber.setText('Barber: {}'.format(barber.name))
            _time = customer.est_time.strftime('%H:%M')
            parent.service.time.setText('Estimated Start Time: {}'.format(_time))
            parent.stack.setCurrentWidget(parent.service)
            parent.status.setText(notifyt('Please wait until your barber calling for you!'))
        elif fail == 1:
            parent.status.setText(
                errort('Sorry, barber {} is too busy to accept your order!'.format(barber.name)))
        else:
            parent.status.setText(errort('Sorry, barber {} is not at work now!'.format(barber.name)))

    def suggest(self):
        parent = self.parent
        parent.stack.setCurrentWidget(parent.suggestion)


class Suggestion(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        font = QtGui.QFont("Sans Serif", 21, QtGui.QFont.Bold)
        title = QtGui.QLabel('Here are some suggestions!')
        title.setFont(font)
        details = QtGui.QLabel('We picked them up just for you:)')
        details.setStyleSheet('QLabel  {color: gray; font-size: 12px; font-weight: regular;}')
        info = QtGui.QVBoxLayout()
        info.addWidget(title)
        info.addWidget(details)

        sug_lbl = QtGui.QLabel('Suggest by')
        scombo = QtGui.QComboBox()
        scombo.addItem("Ratings")
        scombo.addItem("Waiting Time")
        scombo.addItem("Level")
        shbox = QtGui.QHBoxLayout()
        shbox.addWidget(sug_lbl)
        shbox.addWidget(scombo, 1)
        sbox = QtGui.QGroupBox('Suggestion')
        sbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        sbox.setLayout(shbox)

        ratings_vbox = QtGui.QVBoxLayout()
        ratings_vbox.addWidget(barbercard(None))
        ratings_vbox.addWidget(barbercard(None))
        ratings_vbox.addWidget(barbercard(None))
        ratings_vbox.addWidget(barbercard(None))
        ratings_panel = QtGui.QGroupBox('Barber Info')
        ratings_panel.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        ratings_panel.setLayout(ratings_vbox)
        scroll = QtGui.QScrollArea()
        scroll.setWidget(ratings_panel)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea  {border-radius: 10px;}')
        # scroll.setBackgroundRole(QtGui.QPalette.)
        scroll.setFixedHeight(280)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        cancel_btn = QtGui.QPushButton('Back')
        cancel_btn.resize(cancel_btn.sizeHint())
        cancel_btn.clicked.connect(self.goback)
        go_btn = QtGui.QPushButton('More')
        go_btn.resize(go_btn.sizeHint())
        go_btn.clicked.connect(self.loadmore)

        btns = QtGui.QHBoxLayout()
        btns.addStretch(1)
        btns.addWidget(go_btn, 1)
        btns.addWidget(cancel_btn, 1)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(info)
        layout.addStretch(1)
        layout.addWidget(sbox)
        layout.addWidget(scroll)
        layout.addStretch(1)
        layout.addLayout(btns)

        self.setLayout(layout)

    def goback(self):
        parent = self.parent
        self.hide()
        parent.stack.setCurrentWidget(parent.appointment)
        parent.appointment.show()

    def loadmore(self):
        parent = self.parent
        self.hide()
        parent.stack.setCurrentWidget(parent.process)
        parent.process.show()


class Service(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        font = QtGui.QFont("Sans Serif", 21, QtGui.QFont.Bold)
        thanks = QtGui.QLabel('Thank you for your order!')
        thanks.setFont(font)
        # self.details = QtGui.QLabel('John will serve you shortly:)')
        self.details = QtGui.QLabel(self.parent.customer.get_server().current_time)
        self.details.setStyleSheet('QLabel  {color: gray; font-size: 12px; font-weight: regular;}')
        info = QtGui.QVBoxLayout()
        info.addWidget(thanks)
        info.addWidget(self.details)

        self.stack = QtGui.QStackedWidget()
        self.stack.addWidget(barbercard('Your Barber'))

        self.service = QtGui.QLabel('Service: Hair Cut')
        self.barber = QtGui.QLabel('Barber: John')
        self.time = QtGui.QLabel('Estimated Start Time: 18:30')
        self.time.setStyleSheet('QLabel  {color: darkblue; font-size: 16px; font-weight: bold;}')

        service_info = QtGui.QVBoxLayout()
        service_info.addWidget(self.service)
        service_info.addWidget(self.barber)
        service_info.addWidget(self.time)

        sbox = QtGui.QGroupBox('Service Info')
        sbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        sbox.setLayout(service_info)

        cancel_btn = QtGui.QPushButton('Cancel')
        cancel_btn.resize(cancel_btn.sizeHint())
        cancel_btn.clicked.connect(self.cancel)
        # TODO: Add customer side cancel feather
        cancel_btn.setEnabled(False)

        btns = QtGui.QHBoxLayout()
        btns.addStretch(2)
        btns.addWidget(cancel_btn, 1)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(info)
        layout.addWidget(self.stack)
        layout.addWidget(sbox)
        layout.addStretch(1)
        layout.addLayout(btns)
        self.setLayout(layout)

    def go(self):
        parent = self.parent
        customer = parent.customer
        server = customer.get_server()
        barber = server.barbers[customer.bid]

        # parent.process.details.setText('{} is ready to serve you now:)'.format(barber.name))
        parent.process.thanks.setText("It's your turn!")
        parent.process.stack.removeWidget(parent.process.stack.currentWidget())
        card = barbercard('Your Barber', barber, False)
        parent.process.stack.addWidget(card)
        parent.process.stack.setCurrentWidget(card)

        parent.stack.setCurrentWidget(parent.process)
        parent.status.setText(notifyt('Please come to barber {} to begin your service!'.format(barber.name)))

    def confirm(self):
        parent = self.parent
        parent.process.thanks.setText('Have a good time!')
        # parent.process.details.setText('Hohoho:)')
        parent.status.setText(notifyt('Cool! Your service begins!'))

    def cancel(self):
        parent = self.parent
        parent.stack.setCurrentWidget(parent.appointment)

    def update_est_time(self):
        parent = self.parent
        customer = parent.customer
        self.time.setText('Estimated Start Time: {}'.format(customer.est_time.strftime('%H:%M')))
        parent.status.setText(notifyt('The estimated start time has been updated!'))


class Process(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        font = QtGui.QFont("Sans Serif", 21, QtGui.QFont.Bold)
        self.thanks = QtGui.QLabel("It's your turn!")
        self.thanks.setFont(font)
        # self.details = QtGui.QLabel('John is ready to serve you:)')
        self.details = QtGui.QLabel(self.parent.customer.get_server().current_time)
        self.details.setStyleSheet('QLabel  {color: gray; font-size: 12px; font-weight: regular;}')
        info = QtGui.QVBoxLayout()
        info.addWidget(self.thanks)
        info.addWidget(self.details)

        self.stack = QtGui.QStackedWidget()
        self.stack.addWidget(barbercard('Your Barber'))

        progress = QtGui.QLabel('Progress')
        pbar = QtGui.QProgressBar()
        pbar.setValue(50)

        phbox = QtGui.QHBoxLayout()
        phbox.addWidget(progress)
        phbox.addWidget(pbar)

        cancel_btn = QtGui.QPushButton('Cancel')
        cancel_btn.resize(cancel_btn.sizeHint())
        cancel_btn.clicked.connect(self.cancel)
        # TODO: Add this cancel feature
        cancel_btn.setEnabled(False)

        btns = QtGui.QHBoxLayout()
        btns.addStretch(2)
        btns.addWidget(cancel_btn, 1)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(info)
        layout.addWidget(self.stack)
        layout.addLayout(phbox)
        layout.addStretch(1)
        layout.addLayout(btns)
        self.setLayout(layout)

    def cancel(self):
        parent = self.parent
        parent.stack.setCurrentWidget(parent.appointment)

    def done(self, timestamp=None):
        parent = self.parent
        customer = parent.customer
        server = customer.get_server()
        barber = server.barbers[customer.bid]

        parent.finish.stack.removeWidget(parent.finish.stack.currentWidget())
        card = barbercard('Your Barber', barber, False)
        parent.finish.stack.addWidget(card)
        parent.finish.stack.setCurrentWidget(card)

        serstr = ', '.join([SERVICES[sv] for sv in customer.service])
        starttime = barber.time0
        endtime = timestamp
        dt = endtime - starttime
        totmin = round(dt.seconds / 60)
        startstr = starttime.strftime('%H:%M')
        endstr = endtime.strftime('%H:%M')
        hr = totmin // 60
        mins = totmin % 60
        hrstr = '{}h'.format(hr) if hr else ''
        minsstr = '{} min'.format(mins) if (mins or (not hr)) else ''
        durstr = hrstr + ' ' + minsstr

        parent.finish.sstack.removeWidget(parent.finish.sstack.currentWidget())
        scard = sumcard('Summary', barber.name, serstr, startstr, endstr, durstr)
        parent.finish.sstack.addWidget(scard)
        parent.finish.sstack.setCurrentWidget(scard)

        parent.stack.setCurrentWidget(parent.finish)
        parent.status.setText(notifyt('Please consider rating your barber {}!'.format(barber.name)))


class Finish(QtGui.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        font = QtGui.QFont("Sans Serif", 21, QtGui.QFont.Bold)
        thanks = QtGui.QLabel('Your service is done!')
        thanks.setFont(font)
        # self.details = QtGui.QLabel('See you next time:)')
        self.details = QtGui.QLabel(self.parent.customer.get_server().current_time)
        self.details.setStyleSheet('QLabel  {color: gray; font-size: 12px; font-weight: regular;}')
        info = QtGui.QVBoxLayout()
        info.addWidget(thanks)
        info.addWidget(self.details)

        self.stack = QtGui.QStackedWidget()
        self.stack.addWidget(barbercard('Your Barber'))

        self.sstack = QtGui.QStackedWidget()
        self.sstack.addWidget(sumcard())

        rate = QtGui.QLabel('Rating')
        self.ratings_sld = ratings_sld = QtGui.QSlider(QtCore.Qt.Horizontal)
        ratings_sld.setMinimum(2)
        ratings_sld.setMaximum(10)
        ratings_sld.setTickPosition(QtGui.QSlider.TicksBelow)
        ratings_sld.setTickInterval(2)
        ratings_sld.setValue(10)
        ratings_sld.valueChanged.connect(self.update_rate_value)
        self.rate_value = rate_value = QtGui.QLabel('5.0 Stars')
        ratings_hbox = QtGui.QHBoxLayout()
        ratings_hbox.addWidget(rate)
        ratings_hbox.addWidget(ratings_sld)
        ratings_hbox.addWidget(rate_value)
        rbox = QtGui.QGroupBox('Ratings')
        rbox.setStyleSheet('QGroupBox  {color: gray; font-size: 9px; font-weight: bold;}')
        rbox.setLayout(ratings_hbox)

        cancel_btn = QtGui.QPushButton('Skip')
        cancel_btn.resize(cancel_btn.sizeHint())
        cancel_btn.clicked.connect(self.skip)
        go_btn = QtGui.QPushButton('Submit')
        go_btn.resize(go_btn.sizeHint())
        go_btn.clicked.connect(self.submit)

        btns = QtGui.QHBoxLayout()
        btns.addStretch(1)
        btns.addWidget(cancel_btn, 1)
        btns.addWidget(go_btn, 1)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(info)
        layout.addWidget(self.stack)
        layout.addWidget(self.sstack)
        layout.addWidget(rbox)
        layout.addStretch(1)
        layout.addLayout(btns)

        self.setLayout(layout)

    def update_rate_value(self):
        v = self.ratings_sld.value()
        self.rate_value.setText('{:.1f} Stars'.format(v / 2))

    def reset_ratings(self):
        self.ratings_sld.setValue(10)

    def skip(self):
        parent = self.parent
        parent.stack.setCurrentWidget(parent.appointment)
        _msg = 'Thank you! Order another service?'
        parent.status.setText(notifyt(_msg))
        self.reset_ratings()

    def submit(self):
        parent = self.parent
        customer = parent.customer
        server = customer.get_server()

        star = float(self.rate_value.text().split()[0])
        review = ''
        bid = customer.bid
        customer.review(star, review)
        try:
            barber = server.barbers[bid]
            barber.window.workspace.update_review()
        except KeyError:
            pass
        except AttributeError:
            warnings.warn('no window attached!')
        parent.stack.setCurrentWidget(parent.appointment)
        _msg = 'Thank you for your review! Order another service?'
        parent.status.setText(notifyt(_msg))
        self.reset_ratings()


def main():
    app = QtGui.QApplication(sys.argv)
    ex = CustomerWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
