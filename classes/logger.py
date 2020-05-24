import datetime
import os
import sys


class Logger:
    def __init__(self, file, use_stdout, log_file_writes, add_timestamps):
        self.file = file
        self.use_stdout = use_stdout
        self.log_file_writes = log_file_writes
        self.add_timestamps = add_timestamps

    def log(self, *args, **kwargs):
        if self.add_timestamps and len(args) > 0:
            args = (datetime.datetime.now(), ) + args

        if self.file is not None:
            if 'file' not in kwargs or self.log_file_writes or kwargs['file'] in [sys.stderr, sys.stdout]:
                fkwargs = kwargs.copy()
                fkwargs['file'] = self.file

                print(*args, **fkwargs)
                self.file.flush()

            pass
        if self.use_stdout:
            print(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.log(*args, **kwargs)

    @staticmethod
    def create_logger(path: str,
                      create_unique_file=False,
                      openmode='w',
                      encoding='utf8',
                      add_timestamps=False,
                      use_stdout=True):
        assert (isinstance(path, str))
        assert (isinstance(openmode, str))
        assert (isinstance(encoding, str))
        i = 0
        base_log_name = os.path.basename(path)
        log_dir = os.path.dirname(path)
        os.makedirs(log_dir, exist_ok=True)
        log_path = path
        while create_unique_file:
            log_path = os.path.join(log_dir, datetime.date.today().strftime('%Y-%m-%d') + f'-{i}_' + base_log_name)
            i += 1
            if not os.path.isfile(os.path.join(log_dir, log_path)):
                break

        return Logger(
                    file=open(log_path, openmode, encoding=encoding),
                    add_timestamps=add_timestamps,
                    use_stdout=use_stdout, log_file_writes=False)
