import subprocess


class Service:
    """
    systemd service controller
    """
    # _status_time_format = '%a %Y-%m-%d %H:%M:%S %Z'

    def __init__(self, name: str, log=print):
        self.log = log
        name = name.strip()
        if len(name) == 0:
            raise Exception('Service name must be specified.')
        if any([c.isspace() for c in name]):
            raise Exception('Service name cannot contain spaces.')
        self.name = name

    def start(self):
        subprocess.check_call(['sudo', 'systemctl', 'start', self.name])

    def stop(self):
        subprocess.check_call(['sudo', 'systemctl', 'stop', self.name])

    def restart(self):
        subprocess.check_call(['sudo', 'systemctl', 'restart', self.name])

    def _status(self):
        """
        Returns dictionary of values returned by systemctl show call.
        :return: dict
        """
        p = subprocess.check_output(['systemctl', 'show', self.name, '--no-page'])
        stat = {}
        for line in p.decode('utf8').splitlines():
            key, value = line.split('=', 1)
            stat[key.strip()] = value.strip()

        return stat

    def status_string(self):
        x = subprocess.check_output(['systemctl', 'status', self.name]).decode('utf8')\
            .splitlines()[2].strip()
        self.log(f'{self.name} status string:\n{x}')
        return x

    def is_running(self):
        status = self._status()['ActiveState']
        self.log(f'{self.name} ActiveState: {status}')
        return status == 'active'
