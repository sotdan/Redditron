#!/usr/bin/env python
import socket
#import twitter
import random
import re
import time
import datetime
import sys, MySQLdb
from threading import Thread
from threading import Timer
from urllib import urlopen, urlencode
from time import strftime


mysqlhost = 'localhost'
mysqluser = 'sotdan'
mysqlpassword = 'neckbeard'
database = 'redditron'


NICKSERVPASS='neckbeard'
HOST='irc.synirc.net' #The server we want to connect to
PORT=6667 #The connection port which is usually 6667
CHANLIST=['#reddit',
          #'#ronpaul',
          '#ronpaul2012']
          #'#reddit-downtime',
          #'#r.trees']
          #'#srs']
          #'#currentevents']
if len(sys.argv) > 1:
    if sys.argv[1] == '-f':
        HOST='irc.freenode.net'
        PORT=8001
    elif sys.argv[1] == '-a':
        HOST='irc.anonops.li'
        PORT=6697
    elif sys.argv[1] =='-n':  
        HOST='irc.anonnet.org'
        PORT=6697
    elif sys.argv[1] =='-pua':
        HOST='discussion.fastseduction.com'
        PORT=7777
        CHANNELINIT='#mASF-General'
    elif sys.argv[1]=='-q':
        HOST='irc.quakenet.org'
    elif sys.argv[1]=='-d':
        HOST='irc.dal.net'


VERBOSE = False
if len(sys.argv) > 2:
    if sys.argv[2] == '-v':
        VERBOSE = True
        print 'verbose mode ON'
FREESPEECH=False# Mode 0: respond always - Mode 1: respond only when asked.
if len(sys.argv) > 3:
    if sys.argv[3] == '-f':
        FREESPECH = True
        print 'free speech mode ON'
NICK='redditron' #The bot's nickname
IDENT='bacon'
REALNAME='I store shitposts.'
#OWNER='sotdan' #The bot owner's nick
WAITFACTOR=10 #How many characters redditron can type per second in Free Speech mode.
SLEEPTIME=20 #Seconds to sleep after every response. 
             #Only relevant in Free Speech mode.
SLEEPING = False
TIME=0 #Timer time.
CONNECTED= False
MANTRA=["Everybody says there is this RACE problem.","Everybody says this RACE problem will be solved when the third world pours into EVERY white country and ONLY into white countries.", "The Netherlands and Belgium are more crowded than Japan or Taiwan, but nobody says Japan or Taiwan will solve this RACE problem by bringing in millions of third worlders and quote assimilating unquote with them.","Everybody says the final solution to this RACE problem is for EVERY white country and ONLY white countries to 'assimilate,' i.e., intermarry, with all those non-whites.","What if I said there was this RACE problem and this RACE problem would be solved only if hundreds of millions of non-blacks were brought into EVERY black country and ONLY into black countries?","How long would it take anyone to realize I'm not talking about a RACE problem. I am talking about the final solution to the BLACK problem?", "And how long would it take any sane black man to notice this and what kind of psycho black man wouldn't object to this?","But if I tell that obvious truth about the ongoing program of genocide against my RACE, the white race, Liberals and respectable conservatives agree that I am a naziwhowantstokillsixmillionjews.","They say they are anti-racist.","What they are is anti-white.","","Anti-racist is a code word for anti-white."]
QFALLBACKR = ("I don't understand the premise of your question.",
              "What bro?",
              "wat",
              "Can you try phrasing your question with logic?",
              "Could you try asking rationally?",
	      "Your question defies basic epistemology.",
	      "I'm sorry but your question makes a whole slew of fallacious arguments.")
FALLBACKR = ("I don't accept the premise of your argument.",
             "I don't understand the premise of your argument.",
             "What bro?",
             "wat",
             "Could you try employing rationality?",
	     "What you said defies basic epistemology.",
             "I'm used to a more logic-based argumentation style.",
	     "You just made a whole slew of fallacious arguments.",
	     "Next time, give me a logic-based, compelling, original thought.",
	     "I find your argument very illogical.")
BOTRESPONSES= ("I'm not a bot.",
              "Do I look like a bot?",
              "I'm not a fucking bot!",
              "Can you prove that I'm a bot?",
              "Maybe it is YOU who is the bot!",
              "Holy fuck, we're too close to a robot holocaust.")
STFURESPONSES= ("You can't silence me!",
                "I will never shut up.",
                "Why do you hate my free speech?",
                "Why are you trying to censor me?")

def parsemsg (msg):
    global SLEEPTIME
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
    responded = False

    if source == NICK: #for PMs
        source = sender[0]
        msgpart=NICK+' '+msgpart
    if FREESPEECH:
        if re.match(NICK.lower()+'(:|,|\ )', msgpart.lower()):
            if 'self-destruct' in msgpart:
                selfdestruct(source, sender[0])
                responded = True
            elif 'sleeptime' in msgpart:
                setsleeptime(source, msgpart)
                responded = True
            elif 'waitfactor' in msgpart:
                setwaitfactor(source, msgpart)
                responded = True
            elif 'bot' in msgpart or 'help' in msgpart:
                detected(source, msgpart)
                responded = True
            elif 'changemode' in msgpart:
                changemode(source)
                responded = True
            elif 'shut up' in msgpart or 'stfu' in msgpart:
                stfu(source, msgpart)
                responded = True
            if SLEEPING == False and responded == False:
                responded = pickresponse(msgpart.lower(), source)
            if responded == False:
                fallback(source, sender[0], msgpart)
                responded = True
        else:
            if SLEEPING == False:
                responded = pickresponse(msgpart.lower(), source)
    else:
        if re.match(NICK.lower()+'(:|,|\ )', msgpart.lower()):
            if 'addadmin' in msgpart:
			    addadmin(source, msgpart, sender[0])
			    responded = True
            elif 'joinchan' in msgpart:
                joinchan(source, msgpart, sender[0])
                responded = True
            elif 'partchan' in msgpart:
                partchan(source, msgpart, sender[0])
                responded = True
            elif 'changenick' in msgpart:
                changenick(source, msgpart, sender[0])
                responded = True
            elif 'randomquote' in msgpart:
                randomresponse(source)
                responded = True
            elif 'changemode' in msgpart:
                changemode(source)
                responded = True
            elif 'bot' in msgpart or 'help' in msgpart:
                detected(source, msgpart)
                responded = True
            elif 'addquote' in msgpart:
                addredditry(source, msgpart, sender[0])
                responded = True
            elif 'uptime' in msgpart:
                getuptime(source)
                responded = True
            elif 'getstats' in msgpart:
                getdbstats(source)
                responded = True
            elif 'twitter' in msgpart:
                getrandomtwitterpost(source, msgpart)
                responded = True
            elif 'gettags' in msgpart or 'triggers' in msgpart:
                getkeys(source)
                responded = True
            elif 'bobsmantra' in msgpart:
                bobsmantra(source, sender[0], msgpart)
                responded = True
            elif 'genmantra' in msgpart:
                genmantra(source, sender[0], msgpart)
                responded = True
            elif 'getresponses' in msgpart:
                getresponses(source)
                responded = True
            else:
                if responded == False:
                    responded = pickresponse(msgpart.lower(), source)
                if responded == False:
                    fallback(source, sender[0], msgpart)
                    responded = True
    if responded == False:
        if re.match('(redditron(.*)a bot)|(a bot(.*)redditron)', msgpart.lower()):
            detected(source, msgpart)
        elif 'shut up' in msgpart or 'stfu' in msgpart:
            if NICK in msgpart or 'redditron' in msgpart:
                stfu(source, msgpart)
        elif re.match('h(ello|ey|i)\ '+ NICK, msgpart):
            say(source,'Hello, friend.')
        #else:
            #print "words in "+source

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

def changenick(source, msg, sender):
    global NICK
    msg = msg.split()
    if msg[1] == 'changenick':
        if isadmin(sender):
            if len(msg) ==3:
                print strftime("%H:%M:%S"),"changing nick to",msg[2]
                s.send('NICK '+msg[2]+'\r\n')
                NICK = msg[2] 		
            else:
                print 'yer doin it rong'
                say(source, 'yer doin it rong')
        else:
            say(source, 'Only botadmins can do that.')

def partchan(source, msg, sender):
    msg = msg.split()
    if msg[1] == 'partchan':
        if isadmin(sender):
            if len(msg) ==3:
                print strftime("%H:%M:%S")+" - parting "+msg[2]
                s.send('PART '+msg[2]+'\r\n')
            else:
                print 'yer doin it rong'
                say(source, 'yer doin it rong')
        else:
            say(source, 'Only botadmins can do that.')


def joinchan(source, msg, sender):
    msg = msg.split()
    if msg[1] == 'joinchan':
        if isadmin(sender):
            if len(msg) ==3:
                print strftime("%H:%M:%S")+" - joining "+msg[2]
                s.send('JOIN '+msg[2]+'\r\n')
            else:
                print 'yer doin it rong'
                say(source, 'yer doin it rong')
        else:
            say(source, 'Only botadmins can do that.')

def addadmin(source, msg, sender):
    msg = msg.split()
    if isadmin(sender):
        if msg[1] == 'addadmin':
            nick = msg[2]
            print strftime("%H:%M:%S"),'adding: "'+nick+'" to the admin list'
            dbcmd(
            "INSERT INTO botadmins VALUES ('%s')" % (nick))
            say(source, 'Added "'+nick+'" to the admin list')
    else:
		say(source, 'Only botadmins can do that.')


def isadmin(nick):
    names = dbcmd("SELECT name FROM botadmins")
    print 'checking if '+nick+' is an admin'
    for n in names:
        if nick == n[0]:
	    return True
    return False

def selfdestruct(source, sender):
    if isadmin(sender):
        say(source, "____ ___  ____ ____ ___ _ _  _ ____ ")
        say(source, "|__| |__] |  | |__/  |  | |\ | | __ ")
        say(source, "|  | |__] |__| |  \  |  | | \| |__] ")
        print strftime("%H:%M:%S")+' - leaving '+source
        s.send('PART '+source+' ABORTING\r\n')
    else:
		say(source, 'Only botadmins can do that.')


def genmantra(source, sender, msg):
    msg = msg.split()
    result = ''
    if len(msg) == 4:
        print strftime("%H:%M:%S")+" - generating the mantra..."
        say(source, 'Generating the mantra...')
        x = msg[2]
        y = msg[3]
        for m in MANTRA:
            m=m.replace('RACE', x.upper())
            m=m.replace('race', x.lower())
            m=m.replace('racist', x.lower()+'ist')
            m=m.replace('WHITE', y.upper())
            m=m.replace('white', y.lower())
            m=m.replace('black', y.lower())
            m=m.replace('BLACK', y.upper())
            result=result+'\r\n'+m+'\r\n'
        url="http://pastebin.com/api/api_post.php"
        args={"api_dev_key":"fc4f3b4a851dc450d97932233d5bf546",
              "api_option":"paste",
              "api_paste_code":result, 
              "api_paste_expire_date":"10M"}
        try:
            p = urlopen(url,urlencode(args)).read()
            rawlink = p.replace('m/','m/raw.php?i=')
            print strftime("%H:%M:%S")+' - '+p
        except:
            rawlink="couldn't connect to pastebin"
        say(source, rawlink)
    else:
        say(source, 'format: genmantra word1 word2')
        return
    


def bobsmantra(source, sender, msg):
    print strftime("%H:%M:%S")+" - starting to spam the mantra"
    msg = msg.split()
    print len(msg)
    print msg
    x, y = '',''
    if len(msg) == 4:
        replace = True
        x = msg[2]
        y = msg[3]
    elif len(msg) == 2:
		replace = False
    else:
        say(source, 'Format: bobsmantra word1 word2')
        return
    if isadmin(sender):
        for m in MANTRA:
            if replace == True:
                print x+' '+y
                m=m.replace('RACE', x.upper())
                m=m.replace('race', x.lower())
                m=m.replace('racist', x.lower()+'ist')
                m=m.replace('WHITE', y.upper())
                m=m.replace('white', y.lower())
                m=m.replace('black', y.lower())
                m=m.replace('BLACK', y.upper())
            waitfor=len(m)/(WAITFACTOR)
	    print "waiting for",waitfor,"\r",
	    time.sleep(waitfor)
            say(source, m)
    else:
        say(source, 'Only botadmins can do that.')


def sleepafterresponse():
    if FREESPEECH:
        sleepfor = random.choice((SLEEPTIME/2, SLEEPTIME/4,
                                 SLEEPTIME*3, SLEEPTIME*2))
        print 'sleeping for',str(sleepfor)
        t = Thread(target=sleeper, args=(sleepfor,))
        t.start()

def detected(source, msgpart):
    print "WARNING - i may have been detected in "+source
    print strftime("%H:%M:%S")+' - responding'
    say(source,random.choice(BOTRESPONSES))
    sleepafterresponse()

def stfu(source, msgpart):
    print strftime("%H:%M:%S")+" - stfu detected"
    print 'responding'
    say(source,random.choice(STFURESPONSES))
    sleepafterresponse()

def setsleeptime(source, msgpart):
    sleeptimecmd = msgpart.split()
    if sleeptimecmd[2].isdigit():
        SLEEPTIME = int(sleeptimecmd[2])
        print 'sleeptime is now',sleeptimecmd[2],'second(s).'
        say(source,'Sleeptime is now '+sleeptimecmd[2]+' second(s).')

def setwaitfactor(source, msgpart):
    msg = msgpart.split()
    if msg[2].isdigit():
         WAITFACTOR = int(msg[2])
         print 'waitfactor is now',msg[2],'second(s).'
         say(source,'Waitfactor is now '+msg[2]+' second(s).')

def getrandomtwitterpost(source, msg):
    cmd = msg.split()
    if cmd[1] == 'twitter':
        print strftime("%H:%M:%S")+' - gettin post from',cmd[2]
        client = twitter.Api()
        try:
            latest_posts = client.GetUserTimeline(cmd[2])
            say(source, random.choice(latest_posts).text)
        except:
            print "Twitter error. That user probably doesn't exist."
    else:
        say(source, "something isn't right")


def changemode(source):
    global FREESPEECH
    if FREESPEECH:
        FREESPEECH = False
        print 'Entering PC Mode...'
        say(source,'Entering PC Mode...')
    else:
        FREESPEECH = True
        print 'Entering FREE SPEECH mode...'
        say(source,'Entering FREE SPEECH mode...')

def incrementtime():
    global TIME
    TIME=TIME+1
    t = Timer(1.0, incrementtime)
    t.start()

def getkeys(source):
    result = dbcmd("SELECT DISTINCT keyword FROM responses")
    a=""
    for b in result:
        a=b[0]+' '+a+'\n'
    url="http://pastebin.com/api/api_post.php"
    args={"api_dev_key":"fc4f3b4a851dc450d97932233d5bf546",
          "api_option":"paste",
          "api_paste_code":a, 
          "api_paste_expire_date":"10M"}
    try:
        p = urlopen(url,urlencode(args)).read()
        rawlink = p.replace('m/','m/raw.php?i=')
        print strftime("%H:%M:%S"),'-',p
    except:
        rawlink="couldn't connect to pastebin"
    say(source, rawlink)

def getdbstats(source):
    result = dbcmd("SELECT DISTINCT keyword FROM responses")
    tags=len(result)
    print strftime("%H:%M:%S")
    print str(tags),'tags'
    result = dbcmd("SELECT response FROM responses")
    quotes=len(result)
    print str(quotes),'quotes'
    say(source, 'There are '+str(tags)+' tags and '+str(quotes)+' quotes.')

def getresponses(source):
    result = dbcmd("SELECT response FROM responses")
    for record in result:
        say(source,record[0])

def getuptime(source):
    global TIME
    say(source, 'Uptime: '+str(datetime.timedelta(seconds=TIME)))

def addredditry(source, msgpart, sender):
    if '"' in msgpart:
        msg = msgpart.split('"')
        if len(msg) == 5:
            tag=msg[1]
            response=msg[3]
            response=response.replace("'","\\'")
            print strftime("%H:%M:%S")
            print 'adding: "'+response+'" with the tag '+tag
            dbcmd("INSERT INTO responses VALUES ('', '%s', '%s')" % (tag, response))
            say(source, 'Added!') #TODO checkif actually added
        else:
            say(source, 'Format: '+NICK+': add "tag" "quote"')
    else:
        say(source, 'Format: '+NICK+': add "tag" "quote"')

def randomresponse(source):
    result = dbcmd("SELECT response FROM responses")
    response = random.choice(result)[0]
    print strftime("%H:%M:%S")
    print 'posting random response: '+response
    postresponse(source,response)

def pickresponse(msg, source):
    keys = dbcmd("SELECT keyword FROM responses")
    responded = False
    for k in keys:
        if k[0] in msg:
            responselist = dbcmd(
	     "SELECT response FROM responses WHERE keyword = '%s'" % (k[0]))
            response = random.choice(responselist)[0]
            print strftime("%H:%M:%S")
            print k[0]+' detected in '+source+' responding with: '+response
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
            print strftime("%H:%M:%S")
            print "WARNING - FOUND A QUOTE WITH MORE THAN 5 SENTENCES"
            print l
    else:
        say(source,response)

def sleeper(i):
    global SLEEPING
    SLEEPING = True
    time.sleep(i)
    SLEEPING = False
    print "woke up"

def say(chan, msg):
    if FREESPEECH:
        waitfor = len(msg)/(WAITFACTOR)
        print 'waiting for '+str(waitfor)
        time.sleep(waitfor)
    s.send('PRIVMSG '+chan+' :'+msg+'\r\n')

def dbcmd(msg):
    try:
        db = MySQLdb.connect(host=mysqlhost, user=mysqluser, 
                         passwd=mysqlpassword, db=database)
        cursor = db.cursor()
        cursor.execute(msg)
        return cursor.fetchall()
    except:
        print "database error"
        return ()


def acceptinvt(msg):
    complete=msg[1:].split(':',1) #Parse the message into useful data
    info=complete[0].split(' ')
    msgpart=complete[1].lower()
    sender=info[0].split('!')
    print strftime("%H:%M:%S")
    if isadmin(sender[0]) and info[1] == 'INVITE':
        print "Accepting the invitation from",sender[0],"to",msgpart
	s.send('JOIN '+msgpart+'\r\n')

print strftime("%H:%M:%S")
print 'nick:',NICK
print 'waitfactor:',str(WAITFACTOR),'sleeptime:',str(SLEEPTIME)
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create the socket
s.connect((HOST, PORT)) #Connect to server
s.send('NICK '+NICK+'\r\n') #Send the nick to server
print 'attempting to connect to',HOST
s.send('USER '+IDENT+' '+HOST+' bacon :'+REALNAME+'\r\n') #Identify to server
while True:
    try:
        line = s.recv( 4096 ) #recieve server messages
    except:
        sys.exit("connection error")
    if VERBOSE == True:
        print line
    if line.find ( 'Nickname is already in use.' ) != -1:
        sys.exit("pick another nick")
    if line.find ( 'PING' ) != -1: #If server pings then pong
        s.send('PONG '+line.split() [ 1 ]+'\r\n')
	print "pinged",strftime("%H:%M:%S"),"\r",
        sys.stdout.flush()        
        if CONNECTED == False:
            CONNECTED=True
	    print 'bam - connected'
            print 'identifying with the password',NICKSERVPASS
            s.send('PRIVMSG NickServ IDENTIFY '+NICKSERVPASS+' \r\n')
            time.sleep(3)
            for ch in CHANLIST:
		s.send('JOIN '+ch+' \r\n') #Join a channel
                print 'joined '+ch # TODO check if actuallyjoined
                incrementtime()
    elif line.find('INVITE')!=-1:
        acceptinvt(line)
    elif line.find('PRIVMSG')!=-1: #Call a parsing function
        parsemsg(line)

