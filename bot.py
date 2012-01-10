#!/usr/bin/env python


#import twitter
import random, cPickle, socket, re, time, datetime, sys, ConfigParser
from threading import Thread
from threading import Timer
from urllib import urlopen, urlencode
from time import strftime

RESPONSEFILE = sys.path[0]+"/responses.dat"
output = open(RESPONSEFILE, 'rb')
try: RESPONSES = cPickle.load(output)
except: RESPONSES = {}
CONNECTED= False
SLEEPING = False
NICK=""
WAITFACTOR=0
SLEEPTIME=0
FREESPEECH = False
IRC=''
FALLBACKR=[]
QFALLBACKR=[]
BOTRESPONSES=[]
STFURESPONSES=[]
ADMINS=[]



def parsemsg(msg):
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
    respondtomsg(source, sender[0],msgpart)

def respondtomsg(source, sender, msg):
    responded = False
    if source == NICK: #for PMs
        source = sender
        msg=NICK+' '+msg
    if FREESPEECH:
        if re.match(NICK.lower()+'(:|,|\ )', msg.lower()):
            if 'self-destruct' in msg:
                selfdestruct(source, sender)
                responded = True
            elif 'sleeptime' in msg:
                setsleeptime(source, msg)
                responded = True
            elif 'waitfactor' in msg:
                setwaitfactor(source, msg)
                responded = True
            elif 'bot' in msg or 'help' in msg:
                detected(source, msg)
                responded = True
            elif 'changemode' in msg:
                changemode(source)
                responded = True
            elif 'shut up' in msg or 'stfu' in msg:
                stfu(source, msg)
                responded = True
            if SLEEPING == False and responded == False:
                responded = pickresponse(msg.lower(), source)
            if responded == False:
                fallback(source, sender, msg)
                responded = True
        else:
            if SLEEPING == False:
                responded = pickresponse(msg.lower(), source)
    else:
        if re.match(NICK.lower()+'(:|,|\ )', msg.lower()):
            if 'addadmin' in msg:
                addadmin(source, msg, sender)
                responded = True
            elif 'joinchan' in msg:
                joinchan(source, msg, sender)
                responded = True
            elif 'partchan' in msg:
                partchan(source, msg, sender)
                responded = True
            elif 'changenick' in msg:
                changenick(source, msg, sender)
                responded = True
            elif 'randomquote' in msg:
                randomresponse(source)
                responded = True
            elif 'changemode' in msg:
                changemode(source)
                responded = True
            elif 'bot' in msg or 'help' in msg:
                detected(source)
                responded = True
            elif 'addquote' in msg:
                addredditry(source, msg, sender)
                responded = True
            elif 'uptime' in msg:
                getuptime(source)
                responded = True
            elif 'getstats' in msg:
                getdbstats(source)
                responded = True
            elif 'twitter' in msg:
                getrandomtwitterpost(source, msg)
                responded = True
            elif 'gettags' in msg or 'triggers' in msg:
                getkeys(source)
                responded = True
            elif 'bobsmantra' in msg:
                bobsmantra(source, sender, msg)
                responded = True
            elif 'reloadconfig' in msg:
                reloadconfig(source)
                responded = True
            elif 'genmantra' in msg:
                genmantra(source, sender, msg)
                responded = True
            else:
                if responded == False:
                    responded = pickresponse(msg.lower(), source)
                if responded == False:
                    fallback(source, sender, msg)
                    responded = True
    if responded == False:
        if re.match('(redditron(.*)a bot)|(a bot(.*)redditron)', msg.lower()):
            detected(source)
        elif 'shut up' in msg or 'stfu' in msg:
            if NICK in msg:
                stfu(source)
        elif re.match('h(ello|ey|i)\ '+ NICK, msg):
            say(source,'Hello, friend.')


def fallback(source, sender, msg):
    if source == sender: #ifpick it's a PM
        if msg.rstrip().endswith('?'):
            say(source, random.choice(QFALLBACKR))
        else:
            say(source, random.choice(FALLBACKR))
    else:
        if msg.rstrip().endswith('?'):
            say(source, sender+', '+random.choice(QFALLBACKR).lower())
        else:
            say(source, sender+', '+random.choice(FALLBACKR).lower())
    sleepafterresponse()

def detected(source):
    logger("WARNING - i may have been detected in "+source)
    logger(strftime("%H:%M:%S")+' - responding')
    say(source,random.choice(BOTRESPONSES))
    sleepafterresponse()

def stfu(source):
    logger(strftime("%H:%M:%S")+" - stfu detected")
    logger('responding')
    say(source,random.choice(STFURESPONSES))
    sleepafterresponse()

def changenick(source, msg, sender):
    global NICK
    msg = msg.split()
    if msg[1] == 'changenick':
        if sender in ADMINS:
            if len(msg) ==3:
                logger(strftime("%H:%M:%S")+" changing nick to "+msg[2])
                IRC.send('NICK '+msg[2]+'\r\n')
                NICK = msg[2] 		
            else:
                say(source, 'yer doin it rong')
        else:
            say(source, 'Only botadmins can do that.')

def partchan(source, msg, sender):
    msg = msg.split()
    if msg[1] == 'partchan':
        if sender in ADMINS:
            if len(msg) ==3:
                logger(strftime("%H:%M:%S")+" - parting "+msg[2])
                IRC.send('PART '+msg[2]+'\r\n')
            else:
                say(source, 'yer doin it rong')
        else:
            say(source, 'Only botadmins can do that.')

def joinchan(source, msg, sender):
    msg = msg.split()
    if msg[1] == 'joinchan':
        if sender in ADMINS:
            if len(msg) ==3:
                logger(strftime("%H:%M:%S")+" - joining "+msg[2])
                IRC.send('JOIN '+msg[2]+'\r\n')
            else:
                say(source, 'yer doin it rong')
        else:
            say(source, 'Only botadmins can do that.')

def selfdestruct(source, sender):
    if sender in ADMINS:
        say(source, "____ ___  ____ ____ ___ _ _  _ ____ ")
        say(source, "|__| |__] |  | |__/  |  | |\ | | __ ")
        say(source, "|  | |__] |__| |  \  |  | | \| |__] ")
        logger(strftime("%H:%M:%S")+' - leaving '+source)
        IRC.send('PART '+source+' ABORTING\r\n')
    else:
		say(source, 'Only botadmins can do that.')

def genmantra(source, sender, msg):
    msg = msg.split()
    result = ''
    mantra = open(sys.path[0]+"/bobsmantra.txt", 'rb')
    if len(msg) == 4:
        print strftime("%H:%M:%S")+" - generating the mantra..."
        say(source, 'Generating the mantra...')
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
            result=result+'\r\n'+m+'\r\n'
        link = posttopastebin(result)
        say(source, link)
    else:
        say(source, 'format: genmantra word1 word2')
        return

def bobsmantra(source, sender, msg):
    if sender in ADMINS:
        msg = msg.split()
        mantra = open(sys.path[0]+"/bobsmantra.txt", 'rb')
        if len(msg) == 4:
            replace = True
            x = msg[2]
            y = msg[3]
        elif len(msg) == 2:
            replace = False
        else:
            say(source, 'Format: bobsmantra word1 word2')
            return
        logger(strftime("%H:%M:%S")+" - starting to spam the mantra")
        for m in mantra:
            if replace == True:
                m=m.replace('RACE', x.upper())
                m=m.replace('race', x.lower())
                m=m.replace('racist', x.lower()+'ist')
                m=m.replace('WHITE', y.upper())
                m=m.replace('white', y.lower())
                m=m.replace('black', y.lower())
                m=m.replace('BLACK', y.upper())
            waitfor=len(m)/(WAITFACTOR)
            logger("waiting for "+waitfor)
            time.sleep(waitfor)
            say(source, m)
    else:
        say(source, 'Only botadmins can do that.')

def sleepafterresponse():
    if FREESPEECH:
        sleepfor = random.choice((SLEEPTIME/2, SLEEPTIME/4,
                                 SLEEPTIME*3, SLEEPTIME*2))
        logger('sleeping for '+str(sleepfor))
        t = Thread(target=sleeper, args=(sleepfor,))
        t.start()

def setsleeptime(source, msgpart):
    sleeptimecmd = msgpart.split()
    if sleeptimecmd[2].isdigit():
        SLEEPTIME = int(sleeptimecmd[2])
        logger('sleeptime is now '+sleeptimecmd[2]+' second(s).')
        say(source,'Sleeptime is now '+sleeptimecmd[2]+' second(s).')

def setwaitfactor(source, msgpart):
    msg = msgpart.split()
    if msg[2].isdigit():
         WAITFACTOR = int(msg[2])
         logger('waitfactor is now '+msg[2]+' second(s).')
         say(source,'Waitfactor is now '+msg[2]+' second(s).')

def getrandomtwitterpost(source, msg):
    cmd = msg.split()
    if cmd[1] == 'twitter':
        logger(strftime("%H:%M:%S")+' - gettin post from',cmd[2])
        client = twitter.Api()
        try:
            latest_posts = client.GetUserTimeline(cmd[2])
            say(source, random.choice(latest_posts).text)
        except:
            say(source,"Twitter error. That user probably doesn't exist.")
    else:
        say(source, "something isn't right")

def changemode(source):
    global FREESPEECH
    if FREESPEECH:
        FREESPEECH = False
        logger('Entering PC Mode...')
        say(source,'Entering PC Mode...')
    else:
        FREESPEECH = True
        logger('Entering FREE SPEECH mode...')
        say(source,'Entering FREE SPEECH mode...')

def posttopastebin(msg):
    url="http://pastebin.com/api/api_post.php"
    args={"api_dev_key":"fc4f3b4a851dc450d97932233d5bf546",
          "api_option":"paste",
          "api_paste_code":msg, 
          "api_paste_expire_date":"10M"}
    try:
        p = urlopen(url,urlencode(args)).read()
        rawlink = p.replace('m/','m/raw.php?i=')
        logger(strftime("%H:%M:%S")+' - '+p)
    except:
        rawlink="couldn't connect to pastebin"
    return rawlink

def getkeys(source):
    a=RESPONSES.keys()
    link = posttopastebin(a)
    say(source, link)

def getdbstats(source):
    tags=len(RESPONSES.keys())
    quotes = 0
    for x in RESPONSES.values():
        quotes=quotes+len(x)
    say(source, 'There are '+str(tags)+' tags and '+str(quotes)+' quotes.')

def getuptime(source):
    global TIME
    say(source, 'Uptime: '+str(datetime.timedelta(seconds=TIME)))

def addredditry(source, msgpart, sender):
    global RESPONSES
    if '"' in msgpart:
        msg = msgpart.split('"')
        if len(msg) == 5:
            tag=msg[1]
            response=msg[3]
            logger(strftime("%H:%M:%S"))
            logger('adding: "'+response+'" with the tag '+tag)
            if tag in RESPONSES:
                RESPONSES[tag] = RESPONSES[tag].append(response)
            else:
                RESPONSES[tag] = ([response])
            output = open(RESPONSEFILE, 'wb')
            cPickle.dump(RESPONSES, output)
            say(source, 'Added!')
        else:
            say(source, 'Format: '+NICK+': add "tag" "quote"')
    else:
        say(source, 'Format: '+NICK+': add "tag" "quote"')

def randomresponse(source):
    result=RESPONSES.items()
    response = random.choice(result)
    response = random.choice(response[1])
    logger(strftime("%H:%M:%S"))
    logger('posting random response: '+response)
    postresponse(source,response)

def pickresponse(msg, source):
    global RESPONSES
    keys = RESPONSES.keys()
    responded = False
    for k in keys:
        if k in msg:
            responselist = RESPONSES[k]
            response = random.choice(responselist)
            logger(strftime("%H:%M:%S"))
            logger(k+' detected in '+source+' responding with: '+response)
            responded = True
            postresponse(source, response)
            sleepafterresponse()
            break
    return responded
            
def postresponse(source, response): 
    if len(response) > 150 and response.count('.')>1:
        l = response.split('. ',)
        while '' in l:
            l.remove('')
        if len(l) == 1:
            say(source,l[0]+'.')
        elif len(l) == 2:
            postresponse(source, l[0].lstrip(' ')+'.')
            postresponse(source, l[1].lstrip(' '))
        elif len(l) == 3:
            postresponse(source, l[0].lstrip(' ')+'. '+l[1].lstrip(' ')+'.')
            postresponse(source, l[2].lstrip(' '))
        elif len(l) == 4:
            postresponse(source, l[0].lstrip(' ')+'. '+l[1].lstrip(' ')+'.')
            postresponse(source, l[2].lstrip(' ')+'. '+l[3].lstrip(' '))
        elif len(l) == 5:
            postresponse(source, 
            l[0].lstrip(' ')+'. '+l[1].lstrip(' ')+'. '+l[2].lstrip(' ')+'.')
            postresponse(source, l[3].lstrip(' ')+'. '+l[4].lstrip(' '))
        else:
            logger(strftime("%H:%M:%S"))
            logger("WARNING - FOUND A QUOTE WITH MORE THAN 5 SENTENCES")
            logger(l)
    else:
        say(source,response)

def sleeper(i):
    global SLEEPING
    SLEEPING = True
    time.sleep(i)
    SLEEPING = False
    logger("woke up")

def say(chan, msg):
    if FREESPEECH:
        waitfor = 2+len(msg)/(WAITFACTOR)
        logger('waiting for '+str(waitfor))
        time.sleep(waitfor)
    if CONNECTED:
        IRC.send('PRIVMSG '+chan+' :'+msg+'\r\n')
    else: print msg

def reloadconfig(source):

def loadconfig(config):
    config = ConfigParser.ConfigParser()
    config.read(CONFIGFILE)
    global NICK, WAITFACTOR, SLEEPTIME, FREESPEECH, ADMINS
    global FALLBACKR, QFALLBACKR, BOTRESPONSES, STFURESPONSES
    logger(strftime("%H:%M:%S"))
    NICK = config.get('botconfig', 'nick')
    logger('nick: '+NICK)
    WAITFACTOR = config.getint('botconfig', 'waitfactor')
    logger('waitfactor: '+str(WAITFACTOR))
    SLEEPTIME = config.getint('botconfig','sleeptime')
    logger('sleeptime: '+str(SLEEPTIME))
    FREESPEECH = config.getboolean('botconfig','freespeech')
    logger('freespeech: '+str(FREESPEECH))
    ADMINS=config.get('botconfig','admins').split(',')
    logger('importing responses from conf file')
    def readlistfromconf(a):
        rlist = config.items(a)
        result = []
        for r in rlist:
            r = r[1]
            result.append(r)
        return result
    FALLBACKR = readlistfromconf('fallbackresponses')
    QFALLBACKR = readlistfromconf('fallbackresponsesq')
    BOTRESPONSES = readlistfromconf('botresponses')
    STFURESPONSES = readlistfromconf('stfuresponses')
    logger('done')

    servers = config.get('botconfig','servers').split(',')
    server = servers[0]
    host = server.split('/')[0]
    port = int(server.split('/')[1])
    ident = config.get('botconfig','ident')
    realname = config.get('botconfig','realname')
    nspassword = config.get('botconfig','password')
    chanlist = config.get('botconfig','chans').split(',')
    return port,host,ident,realname,nspassword,chanlist

def logger(msg):
    if CONNECTED:
        print msg

def connect(verbose):
    global CONNECTED, IRC

    port,host,ident,realname,nspassword,chanlist = loadconfig(source)

    IRC=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create the socket

    IRC.connect((host, port)) #Connect to server
    IRC.send('NICK '+NICK+'\r\n') #Send the nick to server
    print 'attempting to connect to',host
    IRC.send('USER '+ident+' '+host+' bacon :'+realname+'\r\n') #Identify to server
    while True:
        try:
            line = IRC.recv( 4096 ) #recieve server messages
        except:
            sys.exit("connection error")
        if verbose == True:
            print line
        if line.find ( 'Nickname is already in use.' ) != -1:
            sys.exit("pick another nick")
        if line.find ( 'PING' ) != -1: #If server pings then pong
            IRC.send('PONG '+line.split() [ 1 ]+'\r\n')
            print "pinged",strftime("%H:%M:%S"),"\r",
            sys.stdout.flush()        
            if CONNECTED == False:
                CONNECTED=True
                print 'bam - connected'
                print 'identifying with the password',nspassword
                IRC.send('PRIVMSG NickServ IDENTIFY '+nspassword+' \r\n')
                time.sleep(3)
                for ch in chanlist:
                    IRC.send('JOIN '+ch+' \r\n') #Join a channel
                    logger('joined '+ch) # TODO check if actuallyjoined
        elif line.find('PRIVMSG')!=-1: #Call a parsing function
            parsemsg(line)

def main():
    '''Starts a Redditron Command Line Session
    '''
    print 'Welcome to CLI Redditron'
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read(sys.path[0]+"/redditronrc")
    loadconfig(config)
    while True:
        msg= raw_input('>>')
        respondtomsg(NICK,"",msg)

if __name__ == '__main__': 
   main()
