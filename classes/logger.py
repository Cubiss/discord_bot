import sys
import datetime


class Logger:
    def __init__(self, log_file=None, print=True, timestamps=False):
        self.log_file = log_file
        self.print = print
        self.timestamps = timestamps

    def log(self, message, end='\n'):
        if self.timestamps:
            message = f'[{datetime.datetime.now()}] {message}'

        if self.print:
            print(message, end=end)
            sys.stdout.flush()
        if self.log_file is not None:
            f = open(self.log_file, 'a')
            f.write(str(message) + end)
            f.flush()
