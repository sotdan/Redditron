import random, re, time, datetime, sys,twitter
from time import strftime
from urllib import urlopen, urlencode


def _freespeech(redditron,input):
    msg=input.text
    responded=False
    if redditron.config.exitfreespeechphrase.lower() in msg.lower():
        redditron.freespeech=False
        return
    if re.match(redditron.nick.lower()+'(:|,|\ )', msg.lower()):
        if redditron.sleeping == False:
            responded = functions.detecttrigger(self,input)
        if responded == False:
            functions.fallback(self,input)
            responded = True
    else:
        if self.sleeping == False:
            responded = functions.detecttrigger(self,input)

def posttopastebin(msg):
    url="http://pastebin.com/api/api_post.php"
    args={"api_dev_key":"fc4f3b4a851dc450d97932233d5bf546",
          "api_option":"paste",
          "api_paste_code":msg.encode('utf-8'), 
          "api_paste_expire_date":"10M"}
    try:
        p = urlopen(url,urlencode(args)).read()
        rawlink = p.replace('m/','m/raw.php?i=')
    except:
        print >> sys.stderr, sys.exc_info()[1]
        rawlink="couldn't connect to pastebin"
    return rawlink

def fallback(redditron, input):
    msg=input.text
    if input.priv:
        if msg.rstrip().endswith('?'):
            reply= random.choice(redditron.config.qfallbackr)
        else:
            reply= random.choice(redditron.config.fallbackr)
    else:
        if msg.rstrip().endswith('?'):
            reply=input.nick+', '+random.choice(redditron.config.qfallbackr).lower()
        else:
            reply=input.nick+', '+random.choice(redditron.config.fallbackr).lower()
    redditron.say(input.source,reply,True)

def detected(redditron,input):
    redditron.logger("WARNING - i may have been detected in "+input.source)
    redditron.logger(strftime("%H:%M:%S")+' - responding')
    redditron.say(input.source,random.choice(redditron.config.botresponses), True)

def stfu(redditron,input):
    redditron.logger(strftime("%H:%M:%S")+" - stfu detected")
    redditron.logger('responding')
    redditron.say(input.source,random.choice(redditron.config.stfuresponses),True)

def changenick(redditron,input):
    msg=input.text
    msg = msg.split()
    if msg[1] == 'changenick':
        if input.admin:
            if len(msg) ==3:
                redditron.logger(strftime("%H:%M:%S"))
                redditron.logger("changing nick to "+msg[2])
                redditron.push('NICK '+msg[2]+'\r\n')
                redditron.nick = msg[2] 		
            else:
                redditron.say(input.source, 'yer doin it rong')
        else:
            redditron.say(input.source, 'Only botadmins can do that.')

def partchan(redditron,input):
    msg =input.text
    msg = msg.split()
    if msg[1] == 'partchan':
        if input.admin:
            if len(msg) ==3:
                redditron.logger(strftime("%H:%M:%S"))
                redditron.logger("parting "+msg[2])
                redditron.partch(msg[2])
            else:
                redditron.say(input.source, 'yer doin it rong')
        else:
            redditron.say(input.source, 'Only botadmins can do that.')

def joinchan(redditron,input):
    msg=input.text
    msg = msg.split()
    if msg[1] == 'joinchan':
        if input.admin:
            if len(msg) ==3:
                redditron.joinch(msg[2])
            else:
                redditron.say(input.source, 'yer doin it rong')
        else:
            redditron.say(input.source, 'Only botadmins can do that.')

def selfdestruct(redditron, input):
    if input.admin:
        redditron.say(input.source, "____ ___  ____ ____ ___ _ _  _ ____ ")
        redditron.say(input.source, "|__| |__] |  | |__/  |  | |\ | | __ ")
        redditron.say(input.source, "|  | |__] |__| |  \  |  | | \| |__] ")
        redditron.logger(strftime("%H:%M:%S")+' - leaving '+input.source)
        redditron.partch(input.source)
    else:
		redditron.say(input.source, 'Only botadmins can do that.')

def decode(bytes):
    try: text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try: text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text

def genmantra(redditron, input):
    msg=input.text
    msg = msg.split()
    result = ''
    mantra = open(sys.path[0]+"/bobsmantra.txt", 'rb')
    if len(msg) == 4:
        redditron.logger(strftime("%H:%M:%S")+" - generating the mantra...")
        redditron.say(input.source, 'Generating the mantra...')
        x = msg[2]
        y = msg[3]
        for m in mantra:
            m= decode(m)
            m=m.replace(u'RACE', x.upper())
            m=m.replace(u'race', x.lower())
            m=m.replace(u'racist', x.lower()+u'ist')
            m=m.replace(u'WHITE', y.upper())
            m=m.replace(u'white', y.lower())
            m=m.replace(u'black', y.lower())
            m=m.replace(u'BLACK', y.upper())
            result+=m+'\r\n'
        link = posttopastebin(result)
        redditron.say(input.source, link)
    else:
        redditron.say(input.source, 'format: genmantra word1 word2')
        return

def bobsmantra(redditron, input):
    if input.admin:
        msg=input.text
        msg = msg.split()
        mantra = open(sys.path[0]+"/bobsmantra.txt", 'rb')
        if len(msg) == 4:
            replace = True
            x = msg[2]
            y = msg[3]
        elif len(msg) == 2:
            replace = False
        else:
            redditron.say(input.source, 'Format: bobsmantra word1 word2')
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
            redditron.say(input.source, m)
    else:
        redditron.say(input.source, 'Only botadmins can do that.')

def setsleeptime(redditron, input):
    msg=input.text
    sleeptimecmd = msg.split()
    if sleeptimecmd[2].isdigit():
        redditron.sleeptime = int(sleeptimecmd[2])
        a='Sleeptime is now '+sleeptimecmd[2]+' second(s).'
        redditron.logger(a)
        redditron.say(input.source,a)

def setwaitfactor(redditron, input):
    msg=input.text
    msg = msg.split()
    if msg[2].isdigit():
         redditron.waitfactor = int(msg[2])
         redditron.logger('waitfactor is now '+msg[2]+' second(s).')
         redditron.say(input.source,'Waitfactor is now '+msg[2]+' second(s).')

def getquotes(redditron, input):
    msg=input.text
    msg = msg.split()
    if len(msg) ==2:
        if msg[1]=='getquotes':
            redditron.say(input.source,'Working...')
            redditron.say(input.source,posttopastebin(redditron.responses.getstring()))
    elif len(msg) >= 3:
        msg = msg[2:]
        tag = ' '.join(msg)
        a,b = redditron.responses.getresponses(tag.rstrip())
        if a == True:
            redditron.say(input.source,posttopastebin(b))
        else: redditron.say(input.source,b)


def twitterpost(redditron, input):
    '''posts tweets for a hash on pastebin'''
    msg=input.text
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
        redditron.say(input.source, posttopastebin(result))
    else:
        redditron.say(input.source, "something isn't right")

def getrandomtwitterpost2(redditron,input):
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


def getrandomtwitterpost(redditron, input):
    msg=input.text
    msg = msg.split()
    if msg[1] == 'twitter':
        msg = msg[2:]
        tag = ' '.join(msg)
        redditron.logger(strftime("%H:%M:%S")+' - gettin posts for '+tag)
        client = twitter.Api()
        try:
            latest_posts = client.GetSearch(tag)
            for l in latest_posts[:5]:
                redditron.say(input.source, str(l.text))
                time.sleep(7)
        except:
            redditron.say(input.source,"Twitter error.")
    else:
        redditron.say(input.source, "something isn't right")

def changemode(redditron, input):
    if redditron.freespeech:
        redditron.freespeech = False
        redditron.logger('Entering PC Mode...')
        redditron.say(input.source,'Entering PC Mode...')
    else:
        redditron.freespeech = True
        redditron.logger('Entering FREE SPEECH mode...')
        redditron.say(input.source,'Entering FREE SPEECH mode...')

def gettags(redditron, input):
    link = posttopastebin(redditron.responses.getkeys())
    redditron.say(input.source, link)

def stats(redditron, input):
    redditron.say(input.source, redditron.responses.stats())

def getuptime(redditron, input):
    redditron.say(input.source, 'Uptime: '+str(datetime.timedelta(seconds=TIME)))

def addredditry(redditron, input):
    responses=redditron.responses
    msgpart=input.text
    if '"' in msgpart:
        msg = msgpart.split('"')
        if len(msg) == 5:
            tag=msg[1]
            response=msg[3]
            redditron.logger(strftime("%H:%M:%S"))
            c=responses.add(tag,response)
            if c==0:
                redditron.say(input.source,'Error.')
                redditron.logger('error while adding quote')
            elif c==1: 
                responses.savetofile()
                redditron.say(input.source, 'Added!')
                redditron.logger("added:\n"+response+'\nwith the tag:\n'+tag)
            elif c==2:
                msg='The exact quote already exists.'
                redditron.say(input.source,msg)
                redditron.logger(msg)
        else:
            redditron.say(input.source, 'Format: '+redditron.nick+': addquote "tag" "quote"')
    else:
        redditron.say(input.source, 'Format: '+redditron.nick+': addquote "tag" "quote"')

def randomquote(redditron, input):
    response=redditron.responses.randomquote()
    redditron.logger(strftime("%H:%M:%S"))
    redditron.logger('posting random response: '+response)
    redditron.postresponse(input.source,response)

def detecttrigger(redditron, input):
    msg=input.text
    if not redditron.freespeech and not input.priv:
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
            redditron.postresponse(input.source, response)
            return True
    return False




