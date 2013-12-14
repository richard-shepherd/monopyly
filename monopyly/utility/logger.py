
class Logger(object):
    '''
    A 'log-broker' that relays logged messages to handlers.
    '''

    # An 'enum' for log levels...
    DEBUG = (0, "Debug")
    INFO = (1, "Info")
    INFO_PLUS = (3, "InfoPlus")
    WARNING = (4, "Warning")
    ERROR = (5, "Error")
    FATAL = (6, "Fatal")

    # The collection of handlers...
    _handlers = set()

    # A hint to handlers about how to indent messages...
    _indent_level = 0

    @staticmethod
    def log(message, level=INFO):
        '''
        Logs the message (and level) to all registered handlers.
        '''
        for handler in Logger._handlers:
            handler.handle_log_message(message, level, Logger._indent_level)

    @staticmethod
    def add_handler(handler):
        '''
        Adds a log-handler. This is an object implementing:
        handle_log_message(message, level, indent_level)
        '''
        Logger._handlers.add(handler)

    @staticmethod
    def remove_handler(handler):
        '''
        Removes a log handler.
        '''
        Logger._handlers.remove(handler)

    @staticmethod
    def indent():
        '''
        Increases the indent level.
        '''
        Logger._indent_level += 1

    @staticmethod
    def dedent():
        '''
        Decreases the indent level.
        '''
        if Logger._indent_level > 0:
            Logger._indent_level -= 1



