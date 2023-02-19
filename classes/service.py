import subprocess
# try:
#     import dbus
# except ImportError:
#     dbus = None


class Service:
    """
    systemd service controller
    """

    _unit_name = 'sshd.service'
    # _status_time_format = '%a %Y-%m-%d %H:%M:%S %Z'

    def __init__(self, name: str, log=print, use_dbus=False):
        self.log = log

        self.use_dbus = use_dbus

        # if self.use_dbus and dbus is None:
        #     self.log("Cannot use dbus implementation: 'dbus' package is not present!")
        #     self.use_dbus = False

        # self.sysbus = None
        # self.systemd1 = None
        # self.manager = None

        name = name.strip()
        if len(name) == 0:
            raise Exception('Service name must be specified.')
        if any([c.isspace() for c in name]):
            raise Exception('Service name cannot contain spaces.')
        self.name = name

    # def get_dbus_manager(self):
    #     if self.manager is None:
    #         self.sysbus = dbus.SystemBus()
    #         self.systemd1 = self.sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
    #         self.manager = dbus.Interface(self.systemd1, 'org.freedesktop.systemd1.Manager')
    #     return self.manager
    #
    # def start(self):
    #     if self.use_dbus:
    #         self.get_dbus_manager().StartUnit(self.name, 'fail')
    #     else:
    #         try:
    #             subprocess.check_call(['sudo', 'systemctl', 'start', self.name])
    #         except subprocess.CalledProcessError as ex:
    #             self.log(ex)
    #
    # def stop(self):
    #     if self.use_dbus:
    #         self.get_dbus_manager().StopUnit(self.name, 'fail')
    #     else:
    #         subprocess.check_call(['sudo', 'systemctl', 'stop', self.name])
    #
    # def restart(self):
    #     if self.use_dbus:
    #         self.get_dbus_manager().RestartUnit(self.name, 'fail')
    #     else:
    #         subprocess.check_call(['sudo', 'systemctl', 'restart', self.name])

    def _status(self):
        """
        Returns dictionary of values returned by systemctl show call.
        :return: dict
        """
        # maybe dbus implementation
        p = subprocess.check_output(['systemctl', 'show', self.name, '--no-page'])
        stat = {}
        for line in p.decode('utf8').splitlines():
            key, value = line.split('=', 1)
            stat[key.strip()] = value.strip()

        return stat

    def status_string(self):
        try:
            x = subprocess.check_output(['systemctl', 'status', self.name]).decode('utf8').splitlines()[2].strip()
        except subprocess.CalledProcessError as ex:
            x = ex.output.decode('utf8')
        self.log(f'{self.name} status string:\n{x}')
        return x

    def is_running(self):
        status = self._status()['ActiveState']
        self.log(f'{self.name} ActiveState: {status}')
        return status == 'active'
