import subprocess

"""
    CommandMap class

    This class is used in conjunction with config.json to configure the bot's behavior.
"""

class CommandMap(object):
    def __init__(self, config):
        self.config = config

    def sayHello(self, args):
        return 'Hello, ' + args

    def getHelp(self, args):
        if not any(c.isalpha() for c in args):
            return '*help*: ' + self.config['commands']['help']['help']
        elif args.replace(' ', '') in self.config['commands']:
            return '*'+ args +':* '+ self.config['commands'][args.replace(' ', '')]['help']
        return 'No help information found for ' + args

    def domainLookup(self, args):
        if any(c.isalpha() for c in args):
            ip = str(subprocess.check_output(["dig", "+short", args.replace(' ', '')])).strip('\n')
            return ip if any(c.isdigit() for c in ip) else 'No DNS records found for ' + args
        else:
            return '*dig:* No domain specified.'

    def getHostname(self, args):
        return str(subprocess.check_output(["hostname"])).strip('\n')

    def diskStatus(self, args):
        stat = str(subprocess.check_output(["df","-h","/"])).split('\n')
        return 'Disk Usage _[fs size used avail % mounted]_:  ' + stat[1]

    def getUptime(self, args):
        return str(subprocess.check_output(["uptime"])).strip('\n')

    def doReboot(self, args):
        msg = str(subprocess.check_output(["shutdown","-r","+2"])).strip('\n')
        return 'Reboot scheduled in 2 minutes. ' + msg

    def undoReboot(self, args):
        msg = str(subprocess.check_output(["shutdown","-c"])).strip('\n')
        return 'Reboot cancelled! ' + msg

    def listCommands(self, args):
        commands = list()
        for key in self.config['commands']:
            commands.append(key)
        return 'Available commands are: ' + ', '.join(commands)

    def killClient(self, args):
        exit(0)
