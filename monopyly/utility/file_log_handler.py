from .logger import Logger


class FileLogHandler(object):
    '''
    A log handler that writes to a file.

    Messages at Warning level or greater are prefixed with the log level.
    '''
    def __init__(self, filename, minimum_log_level=Logger.WARNING):
        self.file = open(filename, "w")
        self.minimum_log_level = minimum_log_level

    def handle_log_message(self, message, level, indent_level):
        '''
        Write the message to the file if it is at or above the minimum log level.
        '''
        # Is the logged message at the minimum level to be logged?
        if level[0] < self.minimum_log_level[0]:
            return

        # We want to log the message.

        # We show indent as a sequence of dashes...
        if indent_level > 0:
            indent = "  " * (indent_level-1) + "- "
        else:
            indent = ""

        # We may show the log level as a prefix...
        if level[0] >= Logger.WARNING[0]:
            prefix = level[1] + ": "
        else:
            prefix = ""

        self.file.write(indent + prefix + message + "\n")
        self.file.flush()



