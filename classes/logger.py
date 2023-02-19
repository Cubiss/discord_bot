import datetime
import os
import sys
import shutil


class Logger:
    def __init__(self, files, use_stdout, log_file_writes, add_timestamps):
        self.files = files
        self.use_stdout = use_stdout
        self.log_file_writes = log_file_writes
        self.add_timestamps = add_timestamps

    def log(self, *args, **kwargs):
        if self.add_timestamps and len(args) > 0:
            args = (datetime.datetime.now(), ) + args
        if self.files is not None:
            for f in self.files:
                if 'file' not in kwargs or self.log_file_writes or kwargs['file'] in [sys.stderr, sys.stdout]:
                    fkwargs = kwargs.copy()
                    fkwargs['file'] = f

                    print(*args, **fkwargs)
                    f.flush()
            pass
        if self.use_stdout:
            print(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.log(*args, **kwargs)

    @staticmethod
    def create_logger(log_dir: str,
                      create_latest=True,
                      openmode='w',
                      encoding='utf8',
                      add_timestamps=True,
                      use_stdout=True):

        assert (isinstance(log_dir, str))
        assert (isinstance(openmode, str))
        assert (isinstance(encoding, str))

        os.makedirs(log_dir, exist_ok=True)

        i = 0
        files = []

        while 1:
            current_log_path = os.path.join(
                log_dir, datetime.date.today().strftime('%Y-%m-%d') + f'-{i}.log'
            )

            if os.path.isfile(current_log_path) and openmode != 'a':
                i += 1
                continue

            files.append(open(current_log_path, openmode, encoding=encoding))
            break

        if create_latest:
            files.append(open(os.path.join(log_dir, 'latest.log'), 'w', encoding=encoding))

        return Logger(
                    files=files,
                    add_timestamps=add_timestamps,
                    use_stdout=use_stdout,
                    log_file_writes=False
        )

    @staticmethod
    def get_unique_filename(directory, filename):
        i = 0

        fn, ext = os.path.splitext(filename)

        newname = f"{fn}-{datetime.date.today().strftime('%Y-%m-%d')}.{ext}"

        while os.path.isfile(os.path.join(directory, newname)):
            i += 1
            newname = f"{fn}-{datetime.date.today().strftime('%Y-%m-%d')}.{ext}"

        return newname
        pass
