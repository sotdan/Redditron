#!/usr/bin/env python


import functions,re, responses, irc,sys,time,random,imp
from threading import Thread
from threading import Timer
from time import strftime

def decode(bytes):
    try: text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try: text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text

class Redditron(irc.Bot):
    def __init__(self, config):
        if not hasattr(config,'cli'):
            args = (config.nick, config.realname, config.chanlist, config.nspassword)
            irc.Bot.__init__(self, *args)
        self.config = config
        self.nick = self.config.nick
        self.waitfactor=self.config.waitfactor
        self.cooldowntime=self.config.cooldowntime
        self.freespeech=self.config.freespeech
        self.admins=self.config.admins
        self.connected= False
        self.cooldown = False
        self.responses = responses.Responses()
        self.setup()
    
    def startup(self):
        self.msg('NickServ', 'IDENTIFY %s' % self.config.nspassword)
        print >> sys.stderr, 'joining channels...',
        time.sleep(5)
        for ch in self.config.chanlist:
            self.joinch(ch)
        self.connected=True

    def setup(self):
        self.commands={}
        self.admincommands={}
        funcs=imp.load_source('functions',sys.path[0]+'/functions.py')
        for name, obj in vars(funcs).iteritems():
            if hasattr(obj,'commands'):
                if hasattr(obj,'admin'):
                    for c in obj.commands:
                        self.admincommands[c]=obj
                else:
                    for c in obj.commands:
                        self.commands[c]=obj
    
    def dispatch(self, origin, args):
        # origin.sender = nick when PM, else chan
        bytes, event, args = args[0], args[1], args[2:]
        msg = decode(bytes)
        if event=='251':
            self.startup()
        elif event=='366':
            self.logger('joined '+args[1])
            input = self.input(origin, msg, args)
            input.source=args[1]
            functions._greet(self, input)
        elif event=='PRIVMSG':
            responded = False
            if self.freespeech:
                input = self.input(origin, msg, args)
                if input.priv:
                    input.text=self.nick+' '+msg
                functions._freespeech(self,input)
            else:
                if not self.freespeech:
                    input = self.input(origin, msg, args)
                    nickmatch = re.match(self.nick.lower()+'(:|,|\ )', msg.lower())
                    if re.match('(redditron(.*)a bot)|(a bot(.*)redditron)', msg.lower()):
                        functions.detected(self,input)
                    elif self.nick.lower() in msg.lower() and 'a bot' in msg.lower():
                        functions.detected(self,input)
                    elif 'shut up' in msg or 'stfu' in msg:
                        if self.nick in msg:
                            functions.stfu(self,input)
                    elif re.match('h(ello|ey|i)\ '+ self.nick, msg):
                        functions._greet(self,input)
                    elif nickmatch or input.priv:
                        if not input.priv:
                            msg=msg[len(self.nick)+1:].lstrip()
                            input =self.input(origin,msg,args)
                        if msg:
                            cmd=msg.split()[0]
                            for c in self.commands:
                                if c == cmd:
                                    responded = self.commands[c](self,input)
                                    break
                            for c in self.admincommands:
                                if c in cmd:
                                    if input.admin:
                                        responded=self.admincommands[c](self,input)
                                    else:
                                        self.say(origin.sender,'Only botadmins can do that.')
                            if responded == False:
                                responded = functions.detecttrigger(self,input)
                            if responded == False:
                                functions.fallback(self,input)
                                responded = True

    def joinch(self,ch):
        self.write(('JOIN',ch))

    def partch(self,ch):
        self.write(('PART',ch))

    def nickch(self,ch):
        self.write(('NICK',ch))

    def input(self, origin, text, args):
        class CommandInput(unicode):
            def __new__(cls, text, origin, args):
                s = unicode.__new__(cls, text)
                s.text=text
                s.source = origin.sender
                s.nick = origin.nick
                s.args = args
                s.admin = origin.nick in self.config.admins
                s.priv = not origin.sender.startswith('#')
                return s

        return CommandInput(text, origin, args)

    def startcooldown(self):
        sleepfor = random.choice((self.cooldowntime/2, self.cooldowntime/4,
                                 self.cooldowntime*3, self.cooldowntime*2))
        self.logger('sleeping for '+str(sleepfor))
        t = Thread(target=self.sleeper, args=(sleepfor,))
        t.start()

    def postresponse(self,source,response):
        '''splits the string into several lines and then posts it
        '''
        def splitintwo(response,lit):
            r=response.split(lit)
            self.postresponse(source, lit.join(r[:len(r)/2])+lit.strip())
            self.postresponse(source, lit.join(r[len(r)/2:]))
        if len(response) > 100:
            if '\n' in response:
                splitintwo(response, '\n')
            elif '? ' in response:
                splitintwo(response, '? ')
            elif '; ' in response:
                splitintwo(response, '; ')
            elif '.. ' in response:
                splitintwo(response, '.. ')
            elif '. ' in response:
                splitintwo(response, '. ')
            else: self.say(source,response,cooldown=True)
        else: self.say(source,response,cooldown=True)

    def say(self, ch, msg, cooldown=False):
        if self.waitfactor == 0:
            waitfor = 0
        else:
            if self.freespeech: waitfor = 2+len(msg)/(self.waitfactor)
            else: waitfor = len(msg)/(4*self.waitfactor)
        self.logger('waiting for '+str(waitfor))
        time.sleep(waitfor)
        if self.connected:
            if isinstance(msg,str):
                self.msg(ch,msg)
            else: 
                print 'WARNING - notastring: ',msg
                self.msg(ch,str(msg))
        else: print msg
        if cooldown and self.freespeech:
            self.startcooldown()

    def sleeper(self, i):
        if self.cooldown: return
        self.cooldown = True
        time.sleep(i)
        self.cooldown = False
        self.logger("woke up")

    def logger(self, msg):
        if self.connected:
            print msg

def testallresponses(redditron):
    storewf, redditron.waitfactor = redditron.waitfactor, 0
    l = redditron.responses.getresponseslist()
    errors,errcounter='',0
    for r in l:
        try: redditron.postresponse("",r)
        except: 
            errors+= r+'\n'+str(sys.exc_info())+'\n\n'
            errcounter+=1
    redditron.waitfactor = storewf
    print errors
    print 'errors: '+str(errcounter)

def main():
    '''Starts a Redditron Command Line Session
    '''
    print 'Welcome to Redditron'
    class BotConfig(object):
        def __init__(self):
            self.nick='redditron'
            self.waitfactor=0
            self.cooldowntime=20
            self.admins=['a']
            self.freespeech=False
            self.exitfreespeechphrase = "You're a cracker"
            self.fallbackr = ["i don't understand you"]
            self.qfallbackr = ["i don't understand your question"]
            self.botresponses = ["not a bot."]
            self.stfuresponses = ["no."]
            self.greetings = ["hi."]
            self.cli=True
    class Origin(object):
        def __init__(self):
            self.sender=('a')
            self.nick=('a')
    config = BotConfig()
    bot=Redditron(config)
    origin=Origin()
    while True:
        msg= raw_input('>>')
        if msg == 'q':
            sys.exit("Bye")
        elif msg == 'r':
            input=bot.input(origin,msg,[''])
            input.priv=True
            functions.randomquote(bot,input)
        elif msg == 'test':
            testallresponses(bot)
        else:
            bot.dispatch(origin,[msg.encode(),'PRIVMSG'])

if __name__ == '__main__': 
   main()
