import builtins
import sys


class Printer:
    def __init__(self, log_file=None):
        self.log_file = log_file

    def print(self, output, end='\n'):
        builtins.print(output, end=end)
        sys.stdout.flush()
        if self.log_file is not None:
            open(self.log_file, 'a').write(str(output) + end)
