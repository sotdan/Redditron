import random, re, time, datetime, sys,twitter
from time import strftime
from urllib import urlopen, urlencode


def _freespeech(redditron,input):
    msg=input.text
    responded=False
    if redditron.config.exitfreespeechphrase.lower() in msg.lower():
        redditron.freespeech=False
        logger('exiting free speech mode')
        say(input.source,'...')
        return
    if re.match(redditron.nick.lower()+'(:|,|\ )', msg.lower()):
        if redditron.cooldown == False:
            responded = detecttrigger(redditron,input)
        if responded == False:
            fallback(redditron,input)
            responded = True
    else:
        if redditron.cooldown == False:
            responded = detecttrigger(redditron,input)

def _posttopastebin(msg):
    try: msg = msg.encode('utf-8')
    except: pass
    url="http://pastebin.com/api/api_post.php"
    args={"api_dev_key":"fc4f3b4a851dc450d97932233d5bf546",
          "api_option":"paste",
          "api_paste_code":msg, 
          "api_paste_expire_date":"10M"}
    try:
        p = urlopen(url,urlencode(args)).read()
        rawlink = p.replace('m/','m/raw.php?i=')
    except:
        print >> sys.stderr, sys.exc_info()[1]
        rawlink="couldn't connect to pastebin"
    return rawlink

def _greet(redditron,input):
    msg=input.text
    if input.priv:
        reply= random.choice(redditron.config.greetings)
    else:
        reply=random.choice(redditron.config.greetings)[:-1]+', '+input.nick
    redditron.say(input.source,reply,True)

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
    '''
    self-explanatory
    '''
    msg=input.text
    msg = msg.split()
    if msg[1] == 'changenick':
        if len(msg) ==3:
            redditron.logger(strftime("%H:%M:%S"))
            redditron.logger("changing nick to "+msg[2])
            redditron.nickch(msg[2])
            redditron.nick = msg[2] 		
        else:
            redditron.say(input.source, 'yer doin it rong')
changenick.commands=['changenick']
changenick.admin=1

def partchan(redditron,input):
    '''
    Parts from a channel.
    '''
    msg =input.text
    msg = msg.split()
    if msg[1] == 'partchan':
        if len(msg) ==3:
            redditron.logger(strftime("%H:%M:%S"))
            redditron.logger("parting "+msg[2])
            redditron.partch(msg[2])
        else:
            redditron.say(input.source, 'yer doin it rong')
partchan.commands=['partchan']
partchan.admin=1

def joinchan(redditron,input):
    '''
    Joins a channel.
    '''
    msg=input.text
    msg = msg.split()
    if msg[1] == 'joinchan':
        if len(msg) ==3:
            redditron.joinch(msg[2])
        else:
            redditron.say(input.source, 'yer doin it rong')
joinchan.commands=['joinchan']
joinchan.admin=1

def selfdestruct(redditron, input):
    redditron.say(input.source, "____ ___  ____ ____ ___ _ _  _ ____ ")
    redditron.say(input.source, "|__| |__] |  | |__/  |  | |\ | | __ ")
    redditron.say(input.source, "|  | |__] |__| |  \  |  | | \| |__] ")
    redditron.logger(strftime("%H:%M:%S")+' - leaving '+input.source)
    redditron.partch(input.source)
selfdestruct.commands=['selfdestruct']
selfdestruct.admin=1

def decode(bytes):
    try: text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try: text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text

def genmantra(redditron, input):
    '''
    Generates a mantra. Format: genmantra word1 word2
    '''
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
        link = _posttopastebin(result)
        redditron.say(input.source, link)
    else:
        redditron.say(input.source, 'format: genmantra word1 word2')
        return
genmantra.commands=['genmantra']

def bobsmantra(redditron, input):
    '''
    Spams the mantra.
    '''
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
        m= decode(m)
        if replace == True:
            m=m.replace('RACE', x.upper())
            m=m.replace('race', x.lower())
            m=m.replace('racist', x.lower()+'ist')
            m=m.replace('WHITE', y.upper())
            m=m.replace('white', y.lower())
            m=m.replace('black', y.lower())
            m=m.replace('BLACK', y.upper())
        if redditron.waitfactor==0: waitfor=0
        else: waitfor=len(m)/(redditron.waitfactor)
        redditron.logger("waiting for "+str(waitfor))
        time.sleep(waitfor)
        redditron.say(input.source, str(m))
bobsmantra.commands=['bobsmantra']
bobsmantra.admin=1

def setcooldown(redditron, input):
    msg=input.text
    cooldown = msg.split()
    if cooldown[2].isdigit():
        redditron.cooldown = int(cooldown[2])
        a='Cooldown time is now '+cooldown[2]+' second(s).'
        redditron.logger(a)
        redditron.say(input.source,a)
setcooldown.commands=['cooldown']
setcooldown.admin=1

def setwaitfactor(redditron, input):
    msg=input.text
    msg = msg.split()
    if msg[2].isdigit():
         redditron.waitfactor = int(msg[2])
         redditron.logger('waitfactor is now '+msg[2]+' second(s).')
         redditron.say(input.source,'Waitfactor is now '+msg[2]+' second(s).')
setwaitfactor.commands=['waitfactor']
setwaitfactor.admin=1

def getquotes(redditron, input):
    '''
    Posts all the quotes for a tag (or just all the quotes) to pastebin.
    '''
    msg=input.text
    msg = msg.split()
    if len(msg) ==2:
        if msg[1]=='getquotes':
            redditron.say(input.source,'Working...')
            redditron.say(input.source,_posttopastebin(redditron.responses.getstring()))
    elif len(msg) >= 3:
        msg = msg[2:]
        tag = ' '.join(msg)
        a,b = redditron.responses.getresponses(tag.rstrip())
        if a == True:
            redditron.say(input.source,_posttopastebin(b))
        else: redditron.say(input.source,b)
getquotes.commands=['getquotes']

def twitterpost(redditron, input):
    '''
    Posts a shitload of tweets for a hashtag to pastebin.
    '''
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
        redditron.say(input.source, _posttopastebin(result))
    else:
        redditron.say(input.source, "something isn't right")
twitter.commands=['twitterpost']

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
    '''
    Spams 5 tweets for a hashtag.
    '''
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
getrandomtwitterpost.commands=['twitter']

def gettweets(redditron, input):
    '''
    Spams 5 tweets for a user.
    '''
    msg=input.text
    msg = msg.split()
    print msg
    if msg[1] == 'tweets':
        msg = msg[2]
        redditron.logger(strftime("%H:%M:%S")+' - gettin posts of '+msg)
        client = twitter.Api()
        try:
            print msg
            latest_posts = client.GetUserTimeline(screen_name=msg)
            for l in latest_posts[:5]:
                print l.text
                redditron.say(input.source, str(l.text))
                time.sleep(7)
        except:
            redditron.say(input.source,"Twitter error.")
    else:
        redditron.say(input.source, "something isn't right")
gettweets.commands=['tweets']

def changemode(redditron, input):
    if input.priv and not redditron.freespeech:
        redditron.freespeech = True
        redditron.logger('Entering FREE SPEECH mode...')
        redditron.say(input.source,'Entering FREE SPEECH mode...')
changemode.commands=['changemode']
changemode.admin=1

def gettags(redditron, input):
    link = _posttopastebin(redditron.responses.getkeys())
    redditron.say(input.source, link)
gettags.commands=['triggers','tags','gettags','gettriggers']    

def stats(redditron, input):
    '''
    Spams some quote-database statistics.
    '''
    redditron.say(input.source, redditron.responses.stats())
stats.commands=['stats','getstats']

def getuptime(redditron, input):
    redditron.say(input.source, 'Uptime: '+str(datetime.timedelta(seconds=TIME)))
getuptime.commands=['uptime','getuptime']

def posthelpmsg(redditron,input):
    msg=input.text.split()
    if msg[1]=='help':
        commanddict=redditron.commands
        if len(msg)==2:
            redditron.say(input.source, 'List of commands: '+', '.join(commanddict.keys()))
        else:
            cmd=(' ').join(msg[2:])
            for c in commanddict:
                if cmd == c:
                    func=commanddict[c]
                    redditron.say(input.source,func.__doc__)
posthelpmsg.commands=['help']

def addredditry(redditron, input):
    '''
    Adds a quote to the database along with a tag. Format: $MYNICK: addquote "tag" "quote"'
    '''
    responses=redditron.responses
    msgpart=input.text
    msg = msgpart.split('"')
    if len(msg) == 5:
        tag,response=msg[1],msg[3]
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
addredditry.commands=['addquote']

def randomquote(redditron, input):
    '''
    Spams a random quote.
    '''
    response=redditron.responses.randomquote()
    redditron.logger(strftime("%H:%M:%S"))
    redditron.logger('posting random response: '+response)
    redditron.postresponse(input.source,response)
randomquote.commands=['randomquote','random']

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




