#!/usr/bin/env python


import twitter
import random, responses, socket, re, time, datetime, sys, irc
from threading import Thread
from threading import Timer
from urllib import urlopen, urlencode
from time import strftime

def posttopastebin(msg):
    url="http://pastebin.com/api/api_post.php"
    args={"api_dev_key":"fc4f3b4a851dc450d97932233d5bf546",
          "api_option":"paste",
          "api_paste_code":msg, 
          "api_paste_expire_date":"10M"}
    try:
        p = urlopen(url,urlencode(args)).read()
        rawlink = p.replace('m/','m/raw.php?i=')
    except:
        rawlink="couldn't connect to pastebin"
    return rawlink

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
        self.irc = ''
        self.responses = responses.Responses()

    def parsemsg(self, msg):
        complete=msg[1:].split(':',1) #Parse the message into useful data
        info=complete[0].split(' ')
        source = ""
        if len(info) > 2:
            source = info[2]
        msgpart=complete[1]
        sender=info[0].split('!')
        #if '#' in msgpart: #sometimes irrelevant data gets caught in msgpart
        #    msgpart = ""   #just ignore those lines until i find a better way
        #print "chan: "+ source+" sender: "+sender[0]+" msg: "+msgpart
        self.respondtomsg(source, sender[0],msgpart)

    
    def dispatch(self, line):
        self.parsemsg(line)
        #if args[1]=='PRIVMSG':
        #    print args[2], origin.sender, args[0]
        #    self.respondtomsg(args[2], origin.sender, args[0])


    def respondtomsg(self, source, sender, msg):
        responded = False
        if source == self.nick: #for PMs
            source = sender
            msg=self.nick+' '+msg
        if self.freespeech:
            if re.match(self.nick.lower()+'(:|,|\ )', msg.lower()):
                if 'self-destruct' in msg:
                    self.selfdestruct(source, sender)
                    responded = True
                elif 'sleeptime' in msg:
                    self.setsleeptime(source, msg)
                    responded = True
                elif 'waitfactor' in msg:
                    self.setwaitfactor(source, msg)
                    responded = True
                elif 'bot' in msg or 'help' in msg:
                    self.detected(source)
                    responded = True
                elif 'changemode' in msg:
                    self.changemode(source)
                    responded = True
                elif 'shut up' in msg or 'stfu' in msg:
                    self.stfu(source, msg)
                    responded = True
                if self.sleeping == False and responded == False:
                    responded = self.detecttrigger(msg.lower(), source)
                if responded == False:
                    self.fallback(source, sender, msg)
                    responded = True
            else:
                if self.sleeping == False:
                    responded = self.detecttrigger(msg.lower(), source)
        else:
            if re.match(self.nick.lower()+'(:|,|\ )', msg.lower()):
                if 'addadmin' in msg:
                    self.addadmin(source, msg, sender)
                    responded = True
                elif 'addquote' in msg:
                    self.addredditry(source, msg, sender)
                    responded = True
                elif 'joinchan' in msg:
                    self.joinchan(source, msg, sender)
                    responded = True
                elif 'partchan' in msg:
                    self.partchan(source, msg, sender)
                    responded = True
                elif 'changenick' in msg:
                    self.changenick(source, msg, sender)
                    responded = True
                elif 'randomquote' in msg:
                    self.randomresponse(source)
                    responded = True
                elif 'changemode' in msg:
                    self.changemode(source)
                    responded = True
                elif 'bot' in msg or 'help' in msg:
                    self.detected(source)
                    responded = True
                elif 'uptime' in msg:
                    self.getuptime(source)
                    responded = True
                elif 'getstats' in msg:
                    self.getdbstats(source)
                    responded = True
                elif 'getquotes' in msg:
                    self.getquotes(source,msg)
                    responded = True
                elif 'twitterpost' in msg:
                    self.posttwittertopastebin(source,msg)
                    responded = True
                elif 'twitter' in msg:
                    self.getrandomtwitterpost(source, msg)
                    responded = True
                elif 'gettags' in msg or 'triggers' in msg:
                    self.getkeys(source)
                    responded = True
                elif 'bobsmantra' in msg:
                    self.bobsmantra(source, sender, msg)
                    responded = True
                elif 'reloadconfig' in msg:
                    self.reloadconfig(source)
                    responded = True
                elif 'genmantra' in msg:
                    self.genmantra(source, sender, msg)
                    responded = True
                else:
                    if responded == False:
                        responded = self.detecttrigger(msg.lower(), source)
                    if responded == False:
                        self.fallback(source, sender, msg)
                        responded = True
        if responded == False:
            if re.match('(redditron(.*)a bot)|(a bot(.*)redditron)', msg.lower()):
                self.detected(source)
            elif 'shut up' in msg or 'stfu' in msg:
                if self.nick in msg:
                    self.stfu(source)
            elif re.match('h(ello|ey|i)\ '+ self.nick, msg):
                self.say(source,'Hello, friend.')


    def fallback(self, source, sender, msg):
        if source == sender: #check if it's a PM
            if msg.rstrip().endswith('?'):
                self.say(source, random.choice(self.config.qfallbackr))
            else:
                self.say(source, random.choice(self.config.fallbackr))
        else:
            if msg.rstrip().endswith('?'):
                self.say(source, sender+', '+random.choice(self.config.qfallbackr).lower())
            else:
                self.say(source, sender+', '+random.choice(self.config.fallbackr).lower())
        self.sleepafterresponse()

    def detected(self,source):
        self.logger("WARNING - i may have been detected in "+source)
        self.logger(strftime("%H:%M:%S")+' - responding')
        self.say(source,random.choice(self.config.botresponses))
        self.sleepafterresponse()

    def stfu(self,source):
        self.logger(strftime("%H:%M:%S")+" - stfu detected")
        self.logger('responding')
        self.say(source,random.choice(self.config.stfuresponses))
        self.sleepafterresponse()

    def changenick(self,source, msg, sender):
        msg = msg.split()
        if msg[1] == 'changenick':
            if sender in self.config.admins:
                if len(msg) ==3:
                    self.logger(strftime("%H:%M:%S"))
                    self.logger("changing nick to "+msg[2])
                    self.push('NICK '+msg[2]+'\r\n')
                    self.nick = msg[2] 		
                else:
                    self.say(source, 'yer doin it rong')
            else:
                self.say(source, 'Only botadmins can do that.')

    def partchan(self,source, msg, sender):
        msg = msg.split()
        if msg[1] == 'partchan':
            if sender in self.config.admins:
                if len(msg) ==3:
                    self.logger(strftime("%H:%M:%S"))
                    self.logger("parting "+msg[2])
                    self.push('PART '+msg[2]+'\r\n')
                else:
                    self.say(source, 'yer doin it rong')
            else:
                self.say(source, 'Only botadmins can do that.')

    def joinchan(self,source, msg, sender):
        msg = msg.split()
        if msg[1] == 'joinchan':
            if sender in self.config.admins:
                if len(msg) ==3:
                    self.logger(strftime("%H:%M:%S"))
                    self.logger("joining "+msg[2])
                    self.push('JOIN '+msg[2]+'\r\n')
                else:
                    self.say(source, 'yer doin it rong')
            else:
                self.say(source, 'Only botadmins can do that.')

    def selfdestruct(self, source, sender):
        if sender in self.config.admins:
            self.say(source, "____ ___  ____ ____ ___ _ _  _ ____ ")
            self.say(source, "|__| |__] |  | |__/  |  | |\ | | __ ")
            self.say(source, "|  | |__] |__| |  \  |  | | \| |__] ")
            self.logger(strftime("%H:%M:%S")+' - leaving '+source)
            self.push('PART '+source+' ABORTING\r\n')
        else:
    		self.say(source, 'Only botadmins can do that.')

    def genmantra(self, source, sender, msg):
        msg = msg.split()
        result = ''
        mantra = open(sys.path[0]+"/bobsmantra.txt", 'rb')
        if len(msg) == 4:
            self.logger(strftime("%H:%M:%S")+" - generating the mantra...")
            self.say(source, 'Generating the mantra...')
            x = msg[2]
            y = msg[3]
            for m in mantra:
                m=m.replace('RACE', x.upper())
                m=m.replace('race', x.lower())
                m=m.replace('racist', x.lower()+'ist')
                m=m.replace('WHITE', y.upper())
                m=m.replace('white', y.lower())
                m=m.replace('black', y.lower())
                m=m.replace('BLACK', y.upper())
                result+=m+'\r\n'
            link = posttopastebin(result)
            self.say(source, link)
        else:
            self.say(source, 'format: genmantra word1 word2')
            return

    def bobsmantra(self, source, sender, msg):
        if sender in self.config.admins:
            msg = msg.split()
            mantra = open(sys.path[0]+"/bobsmantra.txt", 'rb')
            if len(msg) == 4:
                replace = True
                x = msg[2]
                y = msg[3]
            elif len(msg) == 2:
                replace = False
            else:
                self.say(source, 'Format: bobsmantra word1 word2')
                return
            self.logger(strftime("%H:%M:%S")+" - starting to spam the mantra")
            for m in mantra:
                if replace == True:
                    m=m.replace('RACE', x.upper())
                    m=m.replace('race', x.lower())
                    m=m.replace('racist', x.lower()+'ist')
                    m=m.replace('WHITE', y.upper())
                    m=m.replace('white', y.lower())
                    m=m.replace('black', y.lower())
                    m=m.replace('BLACK', y.upper())
                waitfor=len(m)/(self.waitfactor)
                self.logger("waiting for "+str(waitfor))
                time.sleep(waitfor)
                self.say(source, m)
        else:
            self.say(source, 'Only botadmins can do that.')

    def sleepafterresponse(self):
        if self.freespeech:
            sleepfor = random.choice((self.sleeptime/2, self.sleeptime/4,
                                     self.sleeptime*3, self.sleeptime*2))
            self.logger('sleeping for '+str(sleepfor))
            t = Thread(target=self.sleeper, args=(sleepfor,))
            t.start()

    def setsleeptime(self, source, msgpart):
        sleeptimecmd = msgpart.split()
        if sleeptimecmd[2].isdigit():
            self.sleeptime = int(sleeptimecmd[2])
            a='Sleeptime is now '+sleeptimecmd[2]+' second(s).'
            self.logger(a)
            self.say(source,a)

    def setwaitfactor(self, source, msgpart):
        msg = msgpart.split()
        if msg[2].isdigit():
             self.waitfactor = int(msg[2])
             self.logger('waitfactor is now '+msg[2]+' second(s).')
             self.say(source,'Waitfactor is now '+msg[2]+' second(s).')

    def getquotes(self, source, msg):
        msg = msg.split()
        if len(msg) ==2:
            if msg[1]=='getquotes':
                self.say(source,'Working...')
                self.say(source,posttopastebin(self.responses.getstring()))
        elif len(msg) >= 3:
            msg = msg[2:]
            tag = ' '.join(msg)
            a,b = self.responses.getresponses(tag.rstrip())
            if a == True:
                self.say(source,posttopastebin(b))
            else: self.say(source,b)


    def posttwittertopastebin(self, source, msg):
        msg = msg.split()
        if msg[1] == 'twitterpost':
            msg = msg[2:]
            tag = ' '.join(msg)
            self.logger(strftime("%H:%M:%S")+' - gettin posts for '+tag)
            client = twitter.Api()
            print 'working'
            latest_posts=[]
            for x in range(1,10):
                print 'getting page '+str(x)
                latest_posts.append(client.GetSearch(tag, per_page= 100, page=x))
            print 'got '+str(len(latest_posts))+' posts'
            result=''
            for p in latest_posts:
                for l in p:
                    result+=l.text+'\n\n'
            self.say(source, posttopastebin(result))
        else:
            self.say(source, "something isn't right")

    def getrandomtwitterpost(self, source, msg):
        msg = msg.split()
        if msg[1] == 'twitter':
            msg = msg[2:]
            tag = ' '.join(msg)
            self.logger(strftime("%H:%M:%S")+' - gettin posts for '+tag)
            client = twitter.Api()
            try:
                latest_posts = client.GetSearch(tag)
                for l in latest_posts[:5]:
                    self.say(source, l.text)
                    time.sleep(7)
            except:
                self.say(source,"Twitter error.")
        else:
            self.say(source, "something isn't right")

    def changemode(self, source):
        if self.freespeech:
            self.freespeech = False
            self.logger('Entering PC Mode...')
            self.say(source,'Entering PC Mode...')
        else:
            self.freespeech = True
            self.logger('Entering FREE SPEECH mode...')
            self.say(source,'Entering FREE SPEECH mode...')

    def getkeys(self, source):
        link = posttopastebin(self.responses.getkeys())
        self.say(source, link)

    def getdbstats(self, source):
        self.say(source, self.responses.stats())

    def getuptime(self, source):
        global TIME
        self.say(source, 'Uptime: '+str(datetime.timedelta(seconds=TIME)))

    def addredditry(self, source, msgpart, sender):
        if '"' in msgpart:
            msg = msgpart.split('"')
            if len(msg) == 5:
                tag=msg[1]
                response=msg[3]
                self.logger(strftime("%H:%M:%S"))
                c=self.responses.add(tag,response)
                if c==0:
                    self.say(source,'Error.')
                    self.logger('error while adding quote')
                elif c==1: 
                    self.say(source, 'Added!')
                    self.responses.savetofile()
                    self.logger("added:\n"+response+'\nwith the tag:\n'+tag)
                elif c==2:
                    msg='The exact quote already exists.'
                    self.say(source,msg)
                    self.logger(msg)
            else:
                self.say(source, 'Format: '+self.nick+': addquote "tag" "quote"')
        else:
            self.say(source, 'Format: '+self.nick+': addquote "tag" "quote"')

    def randomresponse(self, source):
        response=self.responses.randomquote()
        self.logger(strftime("%H:%M:%S"))
        self.logger('posting random response: '+response)
        self.postresponse(source,response)

    def detecttrigger(self, msg, source):
        if not self.freespeech:
            msgm = msg.split()
            msg = ' '.join(msgm[1:])#this removes the nick from msg
        detected, response = self.responses.detect(msg.strip())
        if response == 'error':
            self.logger(response)
        else:
            if len(detected)>0:
                self.logger(strftime("%H:%M:%S"))
                self.logger('detected: '+str(detected))
                self.logger('response: '+response)
                self.postresponse(source, response)
                self.sleepafterresponse()
                return True
        return False

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

    def sleeper(self, i):
        self.sleeping = True
        time.sleep(i)
        self.sleeping = False
        self.logger("woke up")

    def say(self, source, msg):
        if self.waitfactor == 0:
            waitfor = 0
        else:
            if self.freespeech: waitfor = 2+len(msg)/(self.waitfactor)
            else: waitfor = len(msg)/(3*self.waitfactor)
        self.logger('waiting for '+str(waitfor))
        time.sleep(waitfor)
        def safe(input):
            input = input.replace('\n', '')
            input = input.replace('\r', '')
            return input.encode('utf-8')
        if self.connected:
            self.push('PRIVMSG '+source+' :'+safe(msg)+'\r\n')
        else: print msg

    def logger(self, msg):
        if self.connected:
            print msg

    
    # def nsidentify(self):
    #     password=self.config.nspassword
    #     print 'identifying with the password',password
    #     time.sleep(7)
    #     self.irc.send('PRIVMSG NickServ IDENTIFY '+password+'\r\n')
    #     time.sleep(3)        

    # def connect(self):
    #     self.irc=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create the socket
    #     host,port= self.config.host, self.config.port
    #     print 'attempting to connect to',host
    #     self.irc.connect((host,port)) #Connect to server
    #     self.irc.send('NICK '+self.nick+'\r\n') #Send the nick to server
        
    #     self.irc.send('USER '+self.config.ident+' '+host+' bacon :'+self.config.realname+'\r\n')
    #     while True:
    #         try:
    #             line = self.irc.recv( 4096 ) #recieve server messages
    #         except:
    #             sys.exit("connection error")
    #         if self.config.verbose == True:
    #             print line
    #         if line.find ( 'Nickname is already in use.' ) != -1:
    #             sys.exit("pick another nick")
    #         if line.find ( 'PING' ) != -1: #If server pings then pong
    #             self.irc.send('PONG '+line.split() [ 1 ]+'\r\n')
    #             print "pinged",strftime("%H:%M:%S"),"\r",
    #             sys.stdout.flush()        
    #             if self.connected == False:
    #                 self.connected=True
    #                 print 'bam - connected'
    #                 self.nsidentify()
    #                 for ch in self.config.chanlist:
    #                     self.irc.send('JOIN '+ch+' \r\n') #Join a channel
    #                     self.logger('joined '+ch) # TODO check if actuallyjoined
    #         elif line.find('PRIVMSG')!=-1: #Call a parsing function
    #             self.parsemsg(line)

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
