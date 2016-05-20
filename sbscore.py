# !/usr/bin/python
# -*- coding: utf-8 -*-

"""
Smart Barbershop Core

This code is part of the demo of Smart Barbershop System.

author: Zhe Zhang
email: wenatuhs@gmail.com
last edited: May 16, 2016
"""

import os
import pickle
import warnings
from datetime import datetime, timedelta

__version__ = '0.9.5'
SERVERS = {}
TIMECOST = {'haircut': 40, 'wash': 20, 'protect': 30}  # unit: min


class Server:
    def __init__(self, sid, name=None):
        self.sid = sid
        self.name = name
        self.cdb = {}  # customer database
        self.bdb = {}  # barber database
        self.log = []
        database = 'data/{}.db'.format(sid)
        if os.path.exists(database):
            try:
                with open(database, 'rb') as f:
                    self.cdb, self.bdb, self.log = pickle.load(f)
                print('{}: status loaded!'.format(self.sid))
            except:
                warnings.warn('failed to load database file {}!'.format(database))
        self.barbers = {}  # all connected barbers
        self.customers = {}  # all connected customers

    def connect(self):
        try:
            SERVERS[self.sid]
            warnings.warn('already connected!')
        except:
            SERVERS[self.sid] = self
            print('{}: connected!'.format(self.sid))

    def disconnect(self):
        try:
            del SERVERS[self.sid]
            print('{}: disconnected!'.format(self.sid))
        except KeyError:
            warnings.warn('already disconnected!')

    def link(self, client):
        if isinstance(client, Customer):
            if not client.uid:  # anonymous customer
                client.uid = self.new_anon_id()
            self.customers[client.uid] = client
        else:
            if not client.uid:  # anonymous barber
                client.uid = self.new_anon_barber_id()
            self.barbers[client.uid] = client

    def unlink(self, client):
        if isinstance(client, Customer):
            del self.customers[client.uid]
            if client.uid[0] is 'a':
                client.uid = None
        else:
            del self.barbers[client.uid]

    def link_window(self, window):
        self.window = window

    def save(self):
        with open('data/{}.db'.format(self.sid), 'wb') as f:
            pickle.dump([self.cdb, self.bdb, self.log], f)
        print('{}: status saved!'.format(self.sid))

    def record(self, action):
        self.log.append(action)

    def suggest(self, service):
        return list(self.barbers.keys())

    @staticmethod
    def is_valid_worktime(worktime):
        a, b = worktime
        if a <= 24 and a >= 0 and b <= 24 and b >= 0 and a <= b:
            return True

        return False

    @staticmethod
    def is_anon_id(uid):
        try:
            return (uid[0] == 'a') and uid[1:].isdigit()
        except:
            return False

    @staticmethod
    def is_anon_barber_id(uid):
        try:
            return (uid[0:2] == 'ab') and uid[2:].isdigit()
        except:
            return False

    @staticmethod
    def is_anon_barber_id(uid):
        try:
            return (uid[0:2] == 'ab') and uid[2:].isdigit()
        except:
            return False

    def new_anon_id(self):
        anums = [int(uid[1:]) for uid in self.customers.keys() if self.is_anon_id(uid)]
        num = 1
        while num in anums: num += 1
        return 'a{}'.format(num)

    def new_barber_id(self):
        bnums = [int(uid[1:]) for uid in self.bdb.keys()]
        num = 1
        while num in bnums: num += 1
        return 'b{}'.format(num)

    def new_anon_barber_id(self):
        abnums = [int(uid[2:]) for uid in self.barbers.keys() if self.is_anon_barber_id(uid)]
        num = 1
        while num in abnums: num += 1
        return 'ab{}'.format(num)

    @property
    def current_time(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class BarberEntry:
    def __init__(self, barber):
        self.uid = barber.uid
        self.name = barber.name
        self.gender = barber.gender
        self.age = barber.age
        self.level = barber.level
        self.worktime = barber.worktime
        self.reviews = []  # item structure: [uid, star, review]
        self.history = []

    @property
    def ratings(self):
        if self.reviews:
            stars = [review[1] for review in self.reviews]
            return sum(stars) / len(stars)
        else:
            return 5

    def log_review(self, uid=None, star=5, review=''):
        self.reviews.append([uid, star, review])


class CustomerEntry:
    def __init__(self, customer):
        self.uid = customer.uid
        self.pwd = customer.pwd
        self.name = customer.name
        self.history = []


class Client:
    def __init__(self):
        self._uid = None
        self.pwd = None
        self.sid = None

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid):
        self._uid = uid
        if uid:
            try:
                self.window.currentid.refresh_id()
            except AttributeError:
                pass

    def _auto_sel_server(self):
        try:
            key = next(iter(SERVERS))
            server = SERVERS[key]
        except StopIteration:
            warnings.warn('no available servers!')
            server = None
        return server

    def get_server(self):
        if self.sid:
            return SERVERS[self.sid]
        else:
            warnings.warn('not connected to any server yet!')
            return None

    def connect(self):
        if self.sid:
            warnings.warn('already connected to server {}!'.format(self.sid))
        else:
            server = self._auto_sel_server()
            # connect
            if server:
                server.link(self)
                self.sid = server.sid
                print('{0}: connected to server {1}!'.format(self.uid, server.sid))

    def disconnect(self):
        if self.sid:
            print('{0}: disconnected from server {1}!'.format(self.uid, self.sid))
            self.get_server().unlink(self)
            self.sid = None
        else:
            warnings.warn('not connected to any server yet!')


class Barber(Client):
    def __init__(self, uid=None):
        super().__init__()
        self.uid = uid
        self.time0 = None  # current begin time
        self.queue = []

    def connect(self):
        super().connect()
        server = self.get_server()
        try:
            info = server.bdb[self.uid]
            self.name = info.name
            self.gender = info.gender
            self.age = info.age
            self.level = info.level
            self.worktime = info.worktime
        except KeyError:
            warnings.warn('this is your first time connecting, please fill in your info!')

    def register(self, uid, name, gender, age, level='Senior', worktime=[8, 22]):
        if not name:
            return 2
        if age == -1:
            return 3
        if worktime[0] == -1:
            return 4
        if not Server.is_valid_worktime(worktime):
            return 5
        _uid = self.uid
        self.uid = uid
        self.name = name  # first name
        self.gender = gender  # M, F
        self.age = age
        self.level = level  # chief, director, senior
        self.worktime = worktime  # work time
        server = self.get_server()
        if name in [be.name for be in server.bdb.values()]:
            warnings.warn('Nickname {} is already taken, please choose another one!'.format(name))
            self.uid = _uid

            return 1
        else:
            server.bdb[self.uid] = BarberEntry(self)
            self.uid = _uid
            self.login(name)

            return 0

    def login(self, name):
        server = self.get_server()
        try:
            info = [ba for ba in server.barbers.values() if
                    (not Server.is_anon_barber_id(ba.uid)) and ba.name == name][0]

            return 2
        except IndexError:
            pass
        try:
            info = [be for be in server.bdb.values() if be.name == name][0]
            self.name = info.name
            self.gender = info.gender
            self.age = info.age
            self.level = info.level
            self.worktime = info.worktime
            server.unlink(self)
            self.uid = info.uid
            server.link(self)
            print('{0}: hello {1}!'.format(self.uid, self.name))

            return 0
        except IndexError:
            warnings.warn('incorrect id!')

            return 1

    def logout(self):
        # Logout only when queue is empty!
        print('{0}: goodbye {1}!'.format(self.uid, self.name))
        server = self.get_server()
        server.unlink(self)
        self.uid = None
        self.time0 = None
        del self.name
        del self.gender
        del self.age
        del self.level
        del self.worktime
        server.link(self)

    def _update_est_time(self, head=False):
        server = self.get_server()
        try:
            customer0 = server.customers[self.queue[0][0]]
            dt = self.time0 - customer0.est_time
            if not head:
                customer0.est_time += dt
        except IndexError:
            return
        if head:
            queue = self.queue
        else:
            queue = self.queue[1:]
        for task in queue:
            customer = server.customers[task[0]]
            customer.est_time += dt
            try:
                customer.window.service.update_est_time()
            except:
                warnings.warn('no window attached!')

    def _notify_next(self):
        server = self.get_server()
        try:
            customer = server.customers[self.queue[0][0]]
            customer._notify()
        except IndexError:
            pass

    def _confirm_current(self):
        server = self.get_server()
        try:
            customer = server.customers[self.queue[0][0]]
            customer._confirm()
        except IndexError:
            pass

    def _queue_update_notify(self):
        cid = self.queue[-1][0]
        print('{0}: customer {1} is in the queue now.'.format(self.uid, cid))
        try:
            self.window.workspace.update_queue()
            self.window.login.notify_all_customers('modify')
        except AttributeError:
            warnings.warn('no window attached!')

    def _intptime(self, hour):
        _date = self.time0.date().strftime('%Y-%m-%d')
        return datetime.strptime('{0} {1}'.format(_date, hour), '%Y-%m-%d %H')

    def is_available(self, service):
        if self.time0:
            _fintime = self.finish_time() + timedelta(minutes=sum([TIMECOST[ser] for ser in service]))
            if _fintime <= self._intptime(self.worktime[1]):
                return True
            else:
                return True
        else:
            return False

    def wait_time(self):
        totalmin = sum([sum([TIMECOST[ser] for ser in req[1]]) for req in self.queue])
        hours = totalmin // 60
        mins = totalmin % 60
        return [hours, mins]

    def finish_time(self):
        hours, mins = self.wait_time()
        return self.time0 + timedelta(hours=hours, minutes=mins)

    def ready(self, timestamp=None, init=False):
        if not timestamp:
            timestamp = datetime.now()
        self.time0 = timestamp
        if not init:
            self._update_est_time()
            self._notify_next()

    def begin(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()
        self.time0 = timestamp
        cid, service = self.queue[0]
        self.get_server().record([timestamp, self.uid, cid, service, 'begin'])
        self._update_est_time()
        self._confirm_current()

    def done(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()
        cid, service = self.queue.pop(0)
        server = self.get_server()
        server.record([timestamp, self.uid, cid, service, 'done'])
        customer = server.customers[cid]
        customer._done(timestamp)
        # Just a try
        self.time0 = timestamp
        self._update_est_time(True)
        try:
            self.window.workspace.update_queue(True)
            self.window.login.notify_all_customers('modify')
        except AttributeError:
            warnings.warn('no window attached!')

    def cancel(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()
        # TODO: DO SOMETHING ON CUSTOMER SIDE!
        cid, service = self.queue.pop(0)
        server = self.get_server()
        server.record([timestamp, self.uid, cid, service, 'cancel'])
        customer = server.customers[cid]
        customer._cancel()
        # TODO: Notify all customers!

    def link_window(self, window):
        self.window = window


class Customer(Client):
    def link_window(self, window):
        self.window = window

    def _done(self, timestamp=None):
        try:
            self.window.process.done(timestamp)
        except AttributeError:
            warnings.warn('no window attached!')
        print('{}: your haircut is done, leave a review?'.format(self.uid))

    def _cancel(self):
        del self.bid
        del self.est_time
        del self.service
        print('{}: your appointment is cancelled, find out why?'.format(self.uid))

    def _notify(self):
        try:
            self.window.service.go()
        except AttributeError:
            warnings.warn('no window attached!')
        print('{0}: darling, barber {1} is ready to serve you now!'.format(self.uid, self.bid))

    def _confirm(self):
        try:
            self.window.service.confirm()
        except AttributeError:
            warnings.warn('no window attached!')
        print('{}: nice, your service begins!'.format(self.uid))

    def register(self, uid, pwd, name=None):
        server = self.get_server()
        if not uid:
            warnings.warn('id can not be empty!')

            return 2
        if not pwd:
            warnings.warn('password must be set!')

            return 3
        try:
            server.cdb[uid]
            warnings.warn('id {} is already used, please choose another one!'.format(uid))

            return 1
        except KeyError:
            _uid = self.uid
            self.uid = uid
            self.pwd = pwd
            self.name = name
            server.cdb[self.uid] = CustomerEntry(self)
            self.uid = _uid
            self.login(uid, pwd)

            return 0

    def login(self, uid, pwd):
        # Only call this once before logout!
        server = self.get_server()
        try:
            customer = server.cdb[uid]
            if pwd == customer.pwd:
                try:
                    server.customers[uid]

                    return 2
                except KeyError:
                    pass
                server.unlink(self)
                self.uid = uid
                self.pwd = pwd
                self.name = customer.name
                server.link(self)
                print('{0}: hello {1}!'.format(self.uid, self.name if self.name else uid))

                return 0
            else:
                warnings.warn('incorrect id or password!')
        except KeyError:
            warnings.warn('incorrect id or password!')

        return 1

    def logout(self):
        # Only call this after login!
        print('{0}: goodbye {1}!'.format(self.uid, self.name if self.name else self.uid))
        server = self.get_server()
        server.unlink(self)
        self.uid = None
        self.pwd = None
        del self.name
        try:
            del self.bid
            del self.est_time
            del self.service
        except AttributeError:
            pass
        server.link(self)

    def request(self, bid=None, service=['haircut'], timestamp=None):
        server = self.get_server()
        if bid:
            try:
                barber = server.barbers[bid]
                if barber.is_available(service):
                    if not timestamp:
                        timestamp = datetime.now()
                    self.bid = bid
                    self.service = service
                    self.est_time = barber.finish_time()
                    barber.queue.append([self.uid, service])
                    barber._queue_update_notify()
                    server.record([timestamp, bid, self.uid, service, 'assign'])
                    print('{0}: congrats, barber {1} will serve you shortly!'.format(self.uid, bid))

                    return 0
                else:
                    warnings.warn('sorry, barber {} is not available now!'.format(bid))

                    return 1
            except KeyError:
                warnings.warn('sorry, barber {} is not at work now!'.format(bid))

                return 2
        else:
            bbinfo = server.suggest(service)
            print('{0}: here are some suggestions for you:\n{1}'.format(self.uid, bbinfo))

            return 3

    def review(self, star=5, review=''):
        uid = None if Server.is_anon_id(self.uid) else self.uid
        self.get_server().bdb[self.bid].log_review(uid, star, review)
        print('{}: thank you for your review!'.format(self.uid))
        del self.bid
        del self.est_time
        del self.service
