import json
from commandmap import CommandMap

"""
    MessageParser class.

    An instance of this class is passed to the SlackIRCController constructor.
    SlackIRCController will then use it to parse any incoming messages.

    Given a message, this class will strip everything out of it except for the
    message content. Then, it will:

        1) Check to see whether it was @mentioned in the channel,

        2) If so, parse the message and pull out the command/arguments within

        3) Compare the command sent against the list of available commands in
        config.json to see if there's anything for it to do,

        4) If the command is valid, call the appropriate method from CommandMap (which
        is defined in config.json) with the arguments recieved.

        5) Report back with the results (success/failure)

    When a message is recieved, the MessageParser class will check whether it contains any
    available command in config.json. If it does, then MessageParser calls the appropriate
    method within the CommandMap class to handle the message. Each method in this class should
    correspond with a method entry for a command in the config.json file.

    Example:
    	"commands": {
    	  "hello": {
    			"method": "sayHello",
    			"help": "says hello"
    		},
         }

    When the bot recieves the message @nickname hello, then MessageParser will call the sayHello
    method of the CommandMap class.
"""

class MessageParser(object):
    def __init__(self, **kwargs):
        if 'config' in kwargs:
            if isinstance(kwargs['config'], dict):
                self.config = kwargs['config']
            else:
                with open(kwargs['config'], 'r') as cfg:
                    self.config = json.load(cfg)

        self.command_map = CommandMap(self.config)

        if 'nickname' in kwargs:
            self.nickname = kwargs['nickname']
        else:
            self.nickname = self.config['irc']['username']

    """
        The parse method, which is called by the message read/eval loop
        in the SlackIRCController class.
    """
    def parse(self, message):
        # Strip metadata from the message
        message = self.stripMeta(message)

        # If we find our nickame in the message (e.g. we're being summoned)
        if self.checkForNick(message):
            # Strip our nickname from the message
            message = self.stripNick(message)
            # Strip any illegal characters from the message
            message = self.stripCharacters(message)

            # Compare the command sent against the configured list
            command = self.findCommand(message)
            if command is not None:
                # If we found it, then figure out what method to call
                method = self.findMethod(command)
                # Remove the command name from the message, leaving only the arguments
                args = self.stripCommand(command, message)
                # Call the appropriate method in the CommandMap class, and return
                # the response text it generates.
                return getattr(self.command_map, method)(args)

    """
        Checks for either @nickname or nickname in the current message text.
    """
    def checkForNick(self, message):
        message = message.split(' ')
        return '@'+self.nickname in message or self.nickname in message

    """
        Strips the metadata from the latest message.

        Converts this:
            :nickname!nickname@<server> PRIVMSG <channel> : <message>
        to this:
            <message>
    """
    def stripMeta(self, message):
        message = message[message.find(':')+1:] # Strip first colon
        return message[message.find(':')+1:] # Return everything from second colon onwards (message content)

    """
        Removes any blacklisted characters from the message.
    """
    def stripCharacters(self, message):
        for char in self.config['character_blacklist']:
            message = message.replace(char, '')
        return message

    """
        All commands are prefixed with the bot's nickname, so we need to remove that
        so that we're left with only the command itself and the arguments to pass.
    """
    def stripNick(self, message):
        nick = '@'+self.nickname if '@'+self.nickname in message else self.nickname
        message = message[message.find(nick)+len(nick):] # Strip first occurrence of nick
        return message

    """
        Strips the command name from the message, which leaves us with the arguments to pass.
    """
    def stripCommand(self, command, message):
        message = message[message.find(command)+len(command):] # Strip first occurrence of command name
        return message

    """
        The first string after our bot's nick in a message is the name of the command.
        So, we'll take that string and compare it against the configured list of valid
        commands.
    """
    def findCommand(self, message):
        message = message.split(' ')
        for word in message:
            if word in self.config['commands']:
                return word
        return None

    """
        If a command was found, then we'll need to know what method to call
        in the CommandMap class. Thankfully, this is defined in the config,
        so it's easy to look up.
    """
    def findMethod(self, message):
        message = message.split(' ')
        for word in message:
            if word in self.config['commands']:
                return self.config['commands'][word]['method']
        return None
