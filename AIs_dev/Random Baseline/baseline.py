from monopyly import *

import collections
import itertools
import platform
import random
import sys

import time

LOGGING       = False
AUCTIONS_INFO = False
ASSERTING     = False


def ASSERT(condition, msg):
    if ASSERTING and not condition:
        Log('ASSERT: %s' % str(msg))


def DEBUG(msg):
    if LOGGING and 'verbose' in sys.argv:
        print(msg)


prefix = '/tmp' if platform.system() == 'Linux' else 'c:/temp'
logFile = None
try:
    if LOGGING:
        mode = 'wb' if 'clean' in sys.argv else 'ab'
        logFile = open(r'%s/Monopoly_%s.log' % (prefix, platform.node()), mode)
except:
    pass


def Log(msg=''):
    if logFile:
        logFile.write(('%s\n' % msg).encode())
    print(msg)


logResults = None
try:
    if LOGGING:
        logResults = open(r'MonopolyResults_%s.log' % (platform.node()), 'ab')
        logResults.write('\n'.encode())
except:
    pass


def LogResults(msg=''):
    if LOGGING:
        if logResults:
            logResults.write(('%s\n' % msg).encode())
            logResults.flush()
        print(msg)


class LogHandler(object):
    def __init__(self, minimum_log_level=Logger.WARNING, message_processor=None):
        self.minimum_log_level = minimum_log_level
        self.message_processor = message_processor

    def handle_log_message(self, message, level, indent_level):
        self.message_processor(message)


class BaselineAI(PlayerAIBase):
    '''
    An AI that plays randomly with a few simple heuristics.
    '''

    def get_name(self):
        '''
        Returns the name shown for this AI.
        '''
        return "Baseline"
