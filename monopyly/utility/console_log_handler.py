from .logger import Logger


class ConsoleLogHandler(object):
    '''
    A log handler that writes (prints) to the console.

    Messages at Warning level or greater are prefixed with the log level.
    '''
    def __init__(self, minimum_log_level=Logger.WARNING):
        self.minimum_log_level = minimum_log_level

    def handle_log_message(self, message, level, indent_level):
        '''
        Write the message to the console if it is at or above the minimum log level.
        '''
        # Is the logged message at the minimum level to be logged?
        if level[0] < self.minimum_log_level[0]:
            return

        # We want to log the message.

        # We show indent as a sequence of dashes...
        indent = "- " * indent_level

        # We may show the log level as a prefix...
        if level[0] >= Logger.WARNING[0]:
            prefix = level[1] + ": "
        else:
            prefix = ""

        print(indent + prefix + message)



