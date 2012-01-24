import random, re, time, datetime, sys
from time import strftime
from urllib import urlopen, urlencode

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

def fallback(redditron, source, sender, msg):
    if source == sender: #check if it's a PM
        if msg.rstrip().endswith('?'):
            redditron.say(source, random.choice(redditron.config.qfallbackr))
        else:
            redditron.say(source, random.choice(redditron.config.fallbackr))
    else:
        if msg.rstrip().endswith('?'):
            redditron.say(source, sender+', '+random.choice(redditron.config.qfallbackr).lower())
        else:
            redditron.say(source, sender+', '+random.choice(redditron.config.fallbackr).lower())
    redditron.sleepafterresponse()

def detected(redditron,source):
    redditron.logger("WARNING - i may have been detected in "+source)
    redditron.logger(strftime("%H:%M:%S")+' - responding')
    redditron.say(source,random.choice(redditron.config.botresponses))
    redditron.sleepafterresponse()

def stfu(redditron,source):
    redditron.logger(strftime("%H:%M:%S")+" - stfu detected")
    redditron.logger('responding')
    redditron.say(source,random.choice(redditron.config.stfuresponses))
    redditron.sleepafterresponse()

def changenick(redditron,source, msg, sender):
    msg = msg.split()
    if msg[1] == 'changenick':
        if sender in redditron.config.admins:
            if len(msg) ==3:
                redditron.logger(strftime("%H:%M:%S"))
                redditron.logger("changing nick to "+msg[2])
                redditron.push('NICK '+msg[2]+'\r\n')
                redditron.nick = msg[2] 		
            else:
                redditron.say(source, 'yer doin it rong')
        else:
            redditron.say(source, 'Only botadmins can do that.')

def partchan(redditron,source, msg, sender):
    msg = msg.split()
    if msg[1] == 'partchan':
        if sender in redditron.config.admins:
            if len(msg) ==3:
                redditron.logger(strftime("%H:%M:%S"))
                redditron.logger("parting "+msg[2])
                redditron.push('PART '+msg[2]+'\r\n')
            else:
                redditron.say(source, 'yer doin it rong')
        else:
            redditron.say(source, 'Only botadmins can do that.')

def joinchan(redditron,source, msg, sender):
    msg = msg.split()
    if msg[1] == 'joinchan':
        if sender in redditron.config.admins:
            if len(msg) ==3:
                redditron.joinch(msg[2])
            else:
                redditron.say(source, 'yer doin it rong')
        else:
            redditron.say(source, 'Only botadmins can do that.')

def selfdestruct(redditron, source, sender):
    if sender in self.config.admins:
        redditron.say(source, "____ ___  ____ ____ ___ _ _  _ ____ ")
        redditron.say(source, "|__| |__] |  | |__/  |  | |\ | | __ ")
        redditron.say(source, "|  | |__] |__| |  \  |  | | \| |__] ")
        redditron.logger(strftime("%H:%M:%S")+' - leaving '+source)
        redditron.push('PART '+source+' ABORTING\r\n')
    else:
		redditron.say(source, 'Only botadmins can do that.')

def genmantra(redditron, source, sender, msg):
    msg = msg.split()
    result = ''
    mantra = open(sys.path[0]+"/bobsmantra.txt", 'rb')
    if len(msg) == 4:
        redditron.logger(strftime("%H:%M:%S")+" - generating the mantra...")
        redditron.say(source, 'Generating the mantra...')
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
        redditron.say(source, link)
    else:
        redditron.say(source, 'format: genmantra word1 word2')
        return

def bobsmantra(redditron, source, sender, msg):
    if sender in redditron.config.admins:
        msg = msg.split()
        mantra = open(sys.path[0]+"/bobsmantra.txt", 'rb')
        if len(msg) == 4:
            replace = True
            x = msg[2]
            y = msg[3]
        elif len(msg) == 2:
            replace = False
        else:
            redditron.say(source, 'Format: bobsmantra word1 word2')
            return
        redditron.logger(strftime("%H:%M:%S")+" - starting to spam the mantra")
        for m in mantra:
            if replace == True:
                m=m.replace('RACE', x.upper())
                m=m.replace('race', x.lower())
                m=m.replace('racist', x.lower()+'ist')
                m=m.replace('WHITE', y.upper())
                m=m.replace('white', y.lower())
                m=m.replace('black', y.lower())
                m=m.replace('BLACK', y.upper())
            waitfor=len(m)/(redditron.waitfactor)
            redditron.logger("waiting for "+str(waitfor))
            time.sleep(waitfor)
            redditron.say(source, m)
    else:
        redditron.say(source, 'Only botadmins can do that.')

def setsleeptime(redditron, source, msgpart):
    sleeptimecmd = msgpart.split()
    if sleeptimecmd[2].isdigit():
        redditron.sleeptime = int(sleeptimecmd[2])
        a='Sleeptime is now '+sleeptimecmd[2]+' second(s).'
        redditron.logger(a)
        redditron.say(source,a)

def setwaitfactor(redditron, source, msgpart):
    msg = msgpart.split()
    if msg[2].isdigit():
         redditron.waitfactor = int(msg[2])
         redditron.logger('waitfactor is now '+msg[2]+' second(s).')
         redditron.say(source,'Waitfactor is now '+msg[2]+' second(s).')

def getquotes(redditron, source, msg):
    msg = msg.split()
    if len(msg) ==2:
        if msg[1]=='getquotes':
            redditron.say(source,'Working...')
            redditron.say(source,posttopastebin(redditron.responses.getstring()))
    elif len(msg) >= 3:
        msg = msg[2:]
        tag = ' '.join(msg)
        a,b = redditron.responses.getresponses(tag.rstrip())
        if a == True:
            redditron.say(source,posttopastebin(b))
        else: redditron.say(source,b)


def posttwittertopastebin(redditron, source, msg):
    msg = msg.split()
    if msg[1] == 'twitterpost':
        msg = msg[2:]
        tag = ' '.join(msg)
        redditron.logger(strftime("%H:%M:%S")+' - gettin posts for '+tag)
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
        redditron.say(source, posttopastebin(result))
    else:
        redditron.say(source, "something isn't right")

def getrandomtwitterpost2(redditron,source,msg):
    '''trying to remove the python-twitter dependency'''
    url  = 'http://search.twitter.com/search.json'
    json = redditron._FetchUrl(url, parameters=parameters)
    url = redditron._BuildUrl(url, extra_params=extra_params)
    encoded_post_data = redditron._EncodePostData(post_data)
    http_handler  = redditron._urllib.HTTPHandler(debuglevel=_debug)
    https_handler = redditron._urllib.HTTPSHandler(debuglevel=_debug)

    opener = redditron._urllib.OpenerDirector()
    opener.add_handler(http_handler)
    opener.add_handler(https_handler)
    response = opener.open(url, encoded_post_data)
    url_data = redditron._DecompressGzippedResponse(response)
    opener.close()
    data = redditron._ParseAndCheckTwitter(json)


def getrandomtwitterpost(redditron, source, msg):
    msg = msg.split()
    if msg[1] == 'twitter':
        msg = msg[2:]
        tag = ' '.join(msg)
        redditron.logger(strftime("%H:%M:%S")+' - gettin posts for '+tag)
        client = twitter.Api()
        try:
            latest_posts = client.GetSearch(tag)
            for l in latest_posts[:5]:
                redditron.say(source, l.text)
                time.sleep(7)
        except:
            redditron.say(source,"Twitter error.")
    else:
        redditron.say(source, "something isn't right")

def changemode(redditron, source):
    if redditron.freespeech:
        redditron.freespeech = False
        redditron.logger('Entering PC Mode...')
        redditron.say(source,'Entering PC Mode...')
    else:
        redditron.freespeech = True
        redditron.logger('Entering FREE SPEECH mode...')
        redditron.say(source,'Entering FREE SPEECH mode...')

def getkeys(redditron, source):
    link = posttopastebin(redditron.responses.getkeys())
    redditron.say(source, link)

def getdbstats(redditron, source):
    redditron.say(source, redditron.responses.stats())

def getuptime(redditron, source):
    redditron.say(source, 'Uptime: '+str(datetime.timedelta(seconds=TIME)))

def addredditry(redditron, source, msgpart, sender):
    responses=redditron.responses
    if '"' in msgpart:
        msg = msgpart.split('"')
        if len(msg) == 5:
            tag=msg[1]
            response=msg[3]
            redditron.logger(strftime("%H:%M:%S"))
            c=responses.add(tag,response)
            if c==0:
                redditron.say(source,'Error.')
                redditron.logger('error while adding quote')
            elif c==1: 
                responses.savetofile()
                redditron.say(source, 'Added!')
                redditron.logger("added:\n"+response+'\nwith the tag:\n'+tag)
            elif c==2:
                msg='The exact quote already exists.'
                redditron.say(source,msg)
                redditron.logger(msg)
        else:
            redditron.say(source, 'Format: '+redditron.nick+': addquote "tag" "quote"')
    else:
        redditron.say(source, 'Format: '+redditron.nick+': addquote "tag" "quote"')

def randomresponse(redditron, source):
    response=redditron.responses.randomquote()
    redditron.logger(strftime("%H:%M:%S"))
    redditron.logger('posting random response: '+response)
    redditron.postresponse(source,response)

def detecttrigger(redditron, msg, source):
    if not redditron.freespeech:
        msgm = msg.split()
        msg = ' '.join(msgm[1:])#this removes the nick from msg
    detected, response = redditron.responses.detect(msg.strip())
    if response == 'error':
        redditron.logger(response)
    else:
        if len(detected)>0:
            redditron.logger(strftime("%H:%M:%S"))
            redditron.logger('detected: '+str(detected))
            redditron.logger('response: '+response)
            redditron.postresponse(source, response)
            redditron.sleepafterresponse()
            return True
    return False




