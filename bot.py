#!/usr/bin/env python


import functions,re, responses, irc,sys,time,random
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
        args = (config.nick, config.realname, config.chanlist, config.nspassword)
        irc.Bot.__init__(self, *args)
        self.config = config
        self.nick = self.config.nick
        self.waitfactor=self.config.waitfactor
        self.sleeptime=self.config.sleeptime
        self.freespeech=self.config.freespeech
        self.admins=self.config.admins
        self.connected= False
        self.sleeping = False
        self.responses = responses.Responses()
    
    def startup(self):
        self.msg('NickServ', 'IDENTIFY %s' % self.config.nspassword)
        print >> sys.stderr, 'joining channels...',
        time.sleep(5)
        for ch in self.config.chanlist:
            self.joinch(ch)
        self.connected=True
    
    def dispatch(self, origin, args):
        # origin.sender = nick when PM, else chan
        bytes, event, args = args[0], args[1], args[2:]
        text = decode(bytes)
        if event=='251':
            self.startup()
        elif event=='366':
            self.logger('joined '+args[1])
        elif event=='PRIVMSG':
            self.respondtomsg(origin,text)

    def respondtomsg_new(self,origin,text):
        if not self.freespeech:
            if text.startwith(self.nick):
                pass
 
    def joinch(self,ch):
        self.write(('JOIN',ch))

    def partch(self,ch):
        self.write(('PART',ch))

    def respondtomsg(self, origin, msg):
        source,sender=origin.sender, origin.nick
        responded = False
        if source == self.nick: #for PMs
            source = sender
            msg=self.nick+' '+msg
        if self.freespeech:
            if re.match(self.nick.lower()+'(:|,|\ )', msg.lower()):
                if 'self-destruct' in msg:
                    functions.selfdestruct(self,source, sender)
                    responded = True
                elif 'sleeptime' in msg:
                    functions.setsleeptime(self,source, msg)
                    responded = True
                elif 'waitfactor' in msg:
                    functions.setwaitfactor(self,source, msg)
                    responded = True
                elif 'bot' in msg or 'help' in msg:
                    functions.detected(self,source)
                    responded = True
                elif 'changemode' in msg:
                    functions.changemode(self,source)
                    responded = True
                elif 'shut up' in msg or 'stfu' in msg:
                    functions.stfu(self,source,msg)
                    responded = True
                if self.sleeping == False and responded == False:
                    responded = functions.detecttrigger(self,msg.lower(), source)
                if responded == False:
                    functions.fallback(self, source, sender, msg)
                    responded = True
            else:
                if self.sleeping == False:
                    responded = functions.detecttrigger(self,msg.lower(), source)
        else:
            if re.match(self.nick.lower()+'(:|,|\ )', msg.lower()):
                if 'addadmin' in msg:
                    functions.addadmin(self,source, msg, sender)
                    responded = True
                elif 'addquote' in msg:
                    functions.addredditry(self,source, msg, sender)
                    responded = True
                elif 'joinchan' in msg:
                    functions.joinchan(self,source, msg, sender)
                    responded = True
                elif 'partchan' in msg:
                    functions.partchan(self,source, msg, sender)
                    responded = True
                elif 'changenick' in msg:
                    functions.changenick(self,source, msg, sender)
                    responded = True
                elif 'randomquote' in msg:
                    functions.randomresponse(self,source)
                    responded = True
                elif 'changemode' in msg:
                    functions.changemode(self,source)
                    responded = True
                elif 'bot' in msg or 'help' in msg:
                    functions.detected(self,source)
                    responded = True
                elif 'uptime' in msg:
                    functions.getuptime(self,source)
                    responded = True
                elif 'getstats' in msg:
                    functions.getdbstats(self,source)
                    responded = True
                elif 'getquotes' in msg:
                    functions.getquotes(self,source,msg)
                    responded = True
                elif 'twitterpost' in msg:
                    functions.posttwittertopastebin(self,source,msg)
                    responded = True
                elif 'twitter' in msg:
                    functions.getrandomtwitterpost(self,source, msg)
                    responded = True
                elif 'gettags' in msg or 'triggers' in msg:
                    functions.getkeys(self,source)
                    responded = True
                elif 'bobsmantra' in msg:
                    functions.bobsmantra(self,source, sender, msg)
                    responded = True
                elif 'reloadconfig' in msg:
                    functions.reloadconfig(self,source)
                    responded = True
                elif 'genmantra' in msg:
                    functions.genmantra(self,source, sender, msg)
                    responded = True
                else:
                    if responded == False:
                        responded = functions.detecttrigger(self,msg.lower(), source)
                    if responded == False:
                        functions.fallback(self,source, sender, msg)
                        responded = True
        if responded == False:
            if re.match('(redditron(.*)a bot)|(a bot(.*)redditron)', msg.lower()):
                functions.detected(self,source)
            elif 'shut up' in msg or 'stfu' in msg:
                if self.nick in msg:
                    functions.stfu(self,source)
            elif re.match('h(ello|ey|i)\ '+ self.nick, msg):
                self.say(source,'Hello, friend.')

    def sleepafterresponse(self):
        if self.freespeech:
            sleepfor = random.choice((self.sleeptime/2, self.sleeptime/4,
                                     self.sleeptime*3, self.sleeptime*2))
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
        if len(response) > 120:
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
            else: self.say(source,response)
        else: self.say(source,response)

    def say(self, source, msg):
        if self.waitfactor == 0:
            waitfor = 0
        else:
            if self.freespeech: waitfor = 2+len(msg)/(self.waitfactor)
            else: waitfor = len(msg)/(3*self.waitfactor)
        self.logger('waiting for '+str(waitfor))
        time.sleep(waitfor)
        if self.connected:
            self.msg(source,msg)
        else: print msg

    def sleeper(redditron, i):
        redditron.sleeping = True
        time.sleep(i)
        redditron.sleeping = False
        redditron.logger("woke up")

    def logger(self, msg):
        if self.connected:
            print msg

def testallresponses(self):
    storewf, self.waitfactor = self.waitfactor, 0
    l = self.responses.getresponseslist()
    errors,errcounter='',0
    for r in l:
        try: postresponse("",r)
        except: 
            errors+= r+'\n'+str(sys.exc_info())+'\n\n'
            errcounter+=1
    self.waitfactor = storewf
    print errors
    print 'errors: '+str(errcounter)

def main():
    '''Starts a Redditron Command Line Session
    '''
    print 'Welcome to CLI Redditron'
    loadconfig()
    while True:
        msg= raw_input('>>')
        if msg == u'q':
            sys.exit("Bye")
        elif msg == u'r':
            randomresponse('')
        elif msg == u'test':
            testallresponses()
        else:respondtomsg(self.nick,"",msg)

if __name__ == '__main__': 
   main()
