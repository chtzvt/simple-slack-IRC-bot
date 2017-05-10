import json, sys, socket, time
sys.path.insert(0, './lib')
from irccontroller import SlackIRCController
from messageparser import MessageParser

with open('config.json', 'r') as cfg:
    config = json.load(cfg)

slackbot = SlackIRCController(server=config['irc']['host'],
                           port=config['irc']['port'],
                           channel=config['irc']['channel'],
                           master=config['master'],
                           parser=MessageParser(config=config),
                           username=config['irc']['username'],
                           password=config['irc']['password'])

# Runs the bot and handles/retries on connection errors,
# implementing an exponential backoff up to 256 seconds.
def retryLoop(func, sec):
    try:
        func()
    except socket.error:
        sec = sec+1 if sec < 8 else 1
        print 'Connection error, retrying in '+ str(2**sec) +' seconds...'
        time.sleep(2**sec)
        retryLoop(func, sec)

retryLoop(slackbot.run, 0)
