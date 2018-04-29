# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import struct

class Demo(object):

    file_name = ''
    base_name = ''
    demo_prot = 0
    net_prot = 0
    host_name = ''
    client_name = ''
    map_name = ''
    gamedir = ''
    time = 0.0
    ticks = 0
    frames = 0
    tickrate = 0 # int(ticks / time)

    def __init__(self, demo_file):
        self.file_name = demo_file
        self.base_name = os.path.basename(demo_file)
        struct_fmt = 'ii260s260s260s260sfii'
        struct_len = struct.calcsize(struct_fmt)
        with open(demo_file, 'rb') as dem:
            head = struct.unpack('8s', dem.read(8))[0].decode('utf-8')
            if head != 'HL2DEMO\x00':
                raise NotDemoError('Input is not a hl2 demo file.')
            data = struct.unpack(struct_fmt, dem.read(struct_len))
            self.demo_prot = data[0]
            self.net_prot = data[1]
            self.host_name = data[2].decode('utf-8').rstrip('\x00')
            self.client_name = data[3].decode('utf-8').rstrip('\x00')
            self.map_name = data[4].decode('utf-8').rstrip('\x00')
            self.gamedir = data[5].decode('utf-8').rstrip('\x00')
            self.time = data[6]
            self.ticks = data[7]
            self.frames = data[8]
            self.tickrate = int(self.ticks / self.time)

    def __repr__(self):
        return 'Demo(host={}, map={}, ticks={})'.format(repr(self.host_name), repr(self.map_name), repr(self.ticks))

class NotDemoError(Exception):

    def __init__(self, message):
        super(NotDemoError, self).__init__()
        self.message = message

    def __repr__(self):
        classname = self.__class__.__name__
        return '{0}({1})'.format(classname, repr(self.message))

    def __str__(self):
        classname = self.__class__.__name__
        return '{0}: {1}'.format(classname, self.message)
