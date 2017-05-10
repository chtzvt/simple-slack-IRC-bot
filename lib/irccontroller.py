import socket, ssl

class SlackIRCController(object):
    def __init__(self, **kwargs):
        self.server = kwargs['server']
        self.port = kwargs['port']
        if 'username' in kwargs and 'password' in kwargs:
            self.username = kwargs['username']
            self.password = kwargs['password']

        if 'channel' in kwargs:
            self.channel = kwargs['channel']

        if 'nickname' in kwargs:
            self.nickname = '@'+kwargs['nick']
        else:
            self.nickname = self.username

        if 'name' in kwargs:
            self.name = kwargs['name']
        else:
            self.name = self.username

        if 'hostname' in kwargs:
            self.hostname = kwargs['hostname']
        else:
            self.hostname = self.server

        if 'master' in kwargs:
            self.master = '@'+kwargs['master']
        else:
            self.master = '@channel'

        if 'parser' in kwargs and kwargs['parser'] is not None:
            self.commandParser = kwargs['parser']
        else:
            self.commandParser = self

        self.sentGreeting = False
        self.sendReady = False
        self.loop = True

    """
        Call this method to connect, authenticate, and start the read/eval loop
        As the name implies, this runs the bot.
    """
    def run(self):
        self.openSocket()
        self.login()
        self.joinChannel(self.channel)
        self.message_loop()

    """
        This will stop the loop from running.
    """
    def stop():
        self.loop = False

    """
        Opens a socket, and wraps it with SSL
    """
    def openSocket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server, self.port))
        self.irc_socket = ssl.wrap_socket(self.socket)

    """
        Authenticates the bot to the server
        For a handy protocol reference, check out http://stackoverflow.com/a/2969441
    """
    def login(self, **kwargs):
        self.irc_socket.send("USER "+ self.nickname + " " + self.hostname + " " + self.server + " : " + self.name + "\n") # user authentication
        self.irc_socket.send("PASS "+ self.password +"\n")
        self.irc_socket.send("NICK "+ self.nickname +"\n")

    """
        Sends the given message text to the current channel.
    """
    def sendMessage(self, message):
        self.irc_socket.send("PRIVMSG "+ self.channel +" :"+ message +"\n")

    """
        Send a message, but prefix it with the @username of the bot owner, so
        that they're notified.
    """
    def tellMaster(self, message):
        self.sendMessage(self.master +' '+ message)

    """
        Joins the specified channel.
    """
    def joinChannel(self, channel):
        self.irc_socket.send("JOIN "+ channel +"\n")

    """
        As per the RFC, we need to respond with a PONG every time
        the server PINGs us.
    """
    def sendPong(self):
        self.irc_socket.send("PONG :pingis \n")

    """
        The main loop, which retrieves any new messages and passes them to the parser.
        We only pass messages if they're not a PING or authentication error message.
        If no parser is supplied, then we print all messages recieved to stdout.
    """
    def message_loop(self):
        while self.loop is True:
          message = self.irc_socket.recv(2048)
          message = message.strip('\n\r')

          # Every time the server sends a PING, respond with a PONG (per the RFC)
          if message.find("PING :") > 0:
            self.sendPong()

          # We'll get this message if our credentials are invalid.
          # If we do get it, we should stop looping.
          if message.find(':slackbot PRIVMSG '+ self.username +' :Invalid user name or password') > 0:
             self.loop = False

          # After the MOTD has been sent, it's safe to begin sending messages.
          if message.find('End of MOTD command') > 0:
              self.sendReady = True

          # If we haven't sent the greeting yet, but we're ready to begin sending messages
          # Then we'll announce our presence to the current channel.
          if self.sentGreeting is False and self.sendReady is True:
              self.tellMaster(self.nickname +' has connected.')
              self.sentGreeting = True

          # Attempt to evaluate input, and catch any errors
          # If there's an error, we'll notify the channel instead of crashing.
          try:
              output = self.commandParser.parse(message)
              if output is not None:
                  self.tellMaster(output)
          except Exception,e:
              self.tellMaster('Encountered an error while processing: `'+ message +'` _(got `'+ repr(e) +'`)_.')

    """
        If no parser is supplied, the controller will simply print every message it recieves.
    """
    def parse(self, message):
        print message
