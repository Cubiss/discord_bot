import sys


class Logger:
    def __init__(self, log_file=None, print=True):
        self.log_file = log_file
        self.print=print

    def log(self, output, end='\n'):
        if self.print:
            print(output, end=end)
            sys.stdout.flush()
        if self.log_file is not None:
            f = open(self.log_file, 'a')
            f.write(str(output) + end)
            f.flush()
