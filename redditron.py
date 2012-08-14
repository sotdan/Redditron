#!/usr/bin/env python

import socket, bot, argparse, ConfigParser

#configfile = sys.path[0]+"/redditronrc"
configfile = "redditronrc.txt"

class BotConfig(object):
    def __init__(self, configfile):
        conf = ConfigParser.ConfigParser()
        conf.read(configfile)
        self.nick = self.pickanick(conf.get('botconfig', 'nick'))

        print 'nick: '+self.nick

        self.waitfactor = conf.getint('botconfig', 'waitfactor')
        print 'waitfactor: '+str(self.waitfactor)
        self.cooldowntime = conf.getint('botconfig','cooldowntime')
        print 'cooldowntime: '+str(self.cooldowntime)
        self.freespeech = conf.getboolean('botconfig','freespeech')
        self.admins=conf.get('botconfig','admins').split(',')
        print 'importing responses from conf file'
        def readlistfromconf(a):
            rlist = conf.items(a)
            result = []
            for r in rlist:
                r = r[1]
                result.append(r)
            return result
        self.fallbackr = readlistfromconf('fallbackresponses')
        self.qfallbackr = readlistfromconf('fallbackresponsesq')
        self.botresponses = readlistfromconf('botresponses')
        self.stfuresponses = readlistfromconf('stfuresponses')
        self.spamresponses = readlistfromconf('spamresponses')
        self.greetings = readlistfromconf('greetings')
        print 'done'

        servers = conf.get('botconfig','servers').split(',')
        defaultserver = conf.getint('botconfig','defaultserver')
        server = self.pickaserver(servers, defaultserver)
        server = server.strip().split('/')
        self.host=server[0]
        self.port = int(server[1])
        self.ident = conf.get('botconfig','ident')
        self.realname = conf.get('botconfig','realname')
        self.nspassword = conf.get('botconfig','password')
        chans = conf.get('botconfig','chans').split(',')
        self.chanlist = self.pickchans(chans)
        self.exitfreespeechphrase=conf.get('botconfig','exitfreespeechphrase')
        self.freespeech=self.pickfreespeech(self.freespeech)
        print 'freespeech: '+str(self.freespeech)

    def pickaserver(self, servers, defaultserver):
        defaultserver=servers[defaultserver-1]
        print 'Choose a server:\n'
        for s in range(len(servers)):
            if servers[s] == defaultserver:
                print str(s+1)+': '+servers[s]+' [default]'
            else: print str(s+1)+': '+servers[s]
        msg= raw_input('>> enter a number: ')
        try: return servers[int(msg)-1]
        except: return defaultserver

    def pickfreespeech(self,defaultfreespeech):
        msg=raw_input('>> enable free speech?(default: %s)'  % defaultfreespeech)
        if msg=='y':
            return True
        elif msg=='n':
            return False
        else:
            return defaultfreespeech

    def pickanick(self, defaultnick):
        msg= raw_input('>> enter a nick (default= %s): ' % defaultnick)
        if msg=="":
            return defaultnick
        else: return msg

    def pickchans(self, chanlist):
        result=[]
        for c in chanlist:
            msg= raw_input('>> join %s? (y/n) ' % c)
            if msg.lower()=="y":
                result.append(c)
        print 'joining: '+ str(result)
        return result

def main():
    parser = argparse.ArgumentParser(description='Redditron is an awesome IRC bot.')
    parser.add_argument('--verbose','-v',action='store_true')
    args = parser.parse_args()
    config= BotConfig(configfile)
    config.verbose = args.verbose
    redditron = bot.Redditron(config)
    redditron.run(config.host, config.port)

if __name__ == '__main__':
   main()
