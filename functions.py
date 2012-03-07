import random, re, time, datetime, sys, ConfigParser
from time import strftime
from urllib import urlopen, urlencode


def _freespeech(redditron,input):
    responded=False
    if redditron.config.exitfreespeechphrase.lower() in input.lower():
        redditron.freespeech=False
        logger('exiting free speech mode')
        say(input.source,'...')
        return
    elif re.match('(redditron(.*)a bot)|(a bot(.*)redditron)', input.lower()):
        detected(redditron,input)
    elif redditron.nick.lower() in input.lower() and 'a bot' in input.lower():
        detected(redditron,input)
    elif 'shut up' in input or 'stfu' in input:
        if redditron.nick in input:
            stfu(redditron,input)
    elif re.match('h(ello|ey|i)\ '+ redditron.nick, input):
        _greet(redditron,input)
    elif re.match(redditron.nick.lower()+'(:|,|\ )', input.lower()):
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
    if input.priv:
        reply= random.choice(redditron.config.greetings)
    else:
        reply=random.choice(redditron.config.greetings)[:-1]+', '+input.nick
    redditron.say(input.source,reply,True)

def fallback(redditron, input):
    if input.text.rstrip().endswith('?'):
        reply= random.choice(redditron.config.qfallbackr)
    else:
        reply= random.choice(redditron.config.fallbackr)
    if input.priv:
        redditron.say(input.source,reply,True)
    else:
        reply= input.nick+', '+reply[0].lower()+reply[1:]
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
    msg = input.split()
    if len(msg) ==2:
        redditron.logger(strftime("%H:%M:%S"))
        redditron.logger("changing nick to "+msg[1])
        redditron.nickch(msg[1])
        redditron.nick = msg[1] 		
changenick.commands=['changenick']
changenick.admin=1

def partchan(redditron,input):
    '''
    Parts from a channel.
    '''
    msg =input.split()
    if len(msg) ==2:
        redditron.logger(strftime("%H:%M:%S"))
        redditron.logger("parting "+msg[1])
        redditron.partch(msg[1])
partchan.commands=['partchan']
partchan.admin=1

def joinchan(redditron,input):
    '''
    Joins a channel.
    '''
    msg=input.split()
    if len(msg) ==2:
        redditron.joinch(msg[1])
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
    Generates a mantra. Format: $MYNICK: genmantra word1 word2
    '''
    msg=input.split()
    result = ''
    mantra = open(sys.path[0]+"/bobsmantra.txt", 'rb')
    if len(msg) == 3:
        redditron.logger(strftime("%H:%M:%S")+" - generating the mantra...")
        redditron.say(input.source, 'Generating the mantra...')
        x = msg[1]
        y = msg[2]
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
    msg=input.split()
    if len(msg) == 3:
        replace = True
        x,y = msg[1],msg[2]
    elif len(msg) == 1:
        replace = False
    else:
        redditron.say(input.source, 'Format: bobsmantra word1 word2')
        return
    mantra = open(sys.path[0]+"/bobsmantra.txt", 'rb')
    mantra =mantra.read()
    redditron.logger(strftime("%H:%M:%S")+" - starting to spam the mantra")
#        m= decode(m)
    if replace == True:
        mantra=mantra.replace('RACE', x.upper())
        mantra=mantra.replace('race', x.lower())
        mantra=mantra.replace('racist', x.lower()+'ist')
        mantra=mantra.replace('WHITE', y.upper())
        mantra=mantra.replace('white', y.lower())
        mantra=mantra.replace('black', y.lower())
        mantra=mantra.replace('BLACK', y.upper())
    #if redditron.waitfactor==0: waitfor=0
    #else: waitfor=len(m)/(redditron.waitfactor)
    #redditron.logger("waiting for "+str(waitfor))
    #time.sleep(waitfor)
    redditron.postresponse(input.source, mantra)
bobsmantra.commands=['bobsmantra']
bobsmantra.admin=1

def setoption(redditron, input):
    cmd = input.split()
    option = cmd[0]
    if cmd[1].isdigit():
        if option=='cooldown':
            redditron.cooldown = int(cmd[1])
        elif option=='waitfactor':
            redditron.waitfactor= int(cmd[1])
        a=option+' time is now '+cmd[1]+' second(s).'
        redditron.logger(a)
        redditron.say(input.source,a)
setoption.commands=['cooldown','waitfactor']
setoption.admin=1

def ageofconsent(redditron,input):
    '''
    Tells you some interesting facts about a country.
    '''
    cmd = input.split()
    aoc = ConfigParser.ConfigParser()
    aoc.read(sys.path[0]+"/aoc.txt")
    if len(cmd)>1:
        country = ' '.join(cmd[1:])
        try: age = aoc.get('agesofconsent', country.lower())
        except: age = ''
        country=country.title()
        if age:
            msg='The age of consent in '+country+' is '+age+'.'
        else: msg= "Sadly I don't know about the age of consent in "+country
    else: msg='What country do you want to know about?'
    if not input.priv:
        msg=input.nick+', '+msg[0].lower()+msg[1:]
    redditron.say(input.source,msg)
ageofconsent.commands=['aoc','ageofconsent']

def getquotes(redditron, input):
    '''
    Posts all the quotes for a tag (or just all the quotes) to pastebin.
    '''
    msg = input.split()
    if len(msg) ==1:
        redditron.say(input.source,'Working...')
        redditron.say(input.source,_posttopastebin(redditron.responses.getstring()))
    elif len(msg) >= 2:
        msg = msg[1:]
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
    try: import twitter
    except:
        redditron.say(input.source,"I'm missing the twitter module")
        return
    msg = input.split()[1:]
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
#twitter.commands=['twitterpost']

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
    try: import twitter
    except:
        redditron.say(input.source,"I'm missing the twitter module")
        return
    msg = input.split()[1:]
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
getrandomtwitterpost.commands=['twitter']

def gettweets(redditron, input):
    '''
    Spams 5 tweets for a user.
    '''
    try: import twitter
    except:
        redditron.say(input.source,"I'm missing the twitter module")
        return
    msg = input.split()
    print msg
    msg = msg[1]
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
gettweets.commands=['tweets']

def changemode(redditron, input):
    '''
    enters FREE SPEECH mode
    '''
    if input.priv and not redditron.freespeech:
        redditron.freespeech = True
        redditron.logger('Entering FREE SPEECH mode...')
        redditron.say(input.source,'Entering FREE SPEECH mode...')
changemode.commands=['changemode']
changemode.admin=1

def gettags(redditron, input):
    '''
    posts a list of all the triggers to pastebin
    '''
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
#getuptime.commands=['uptime','getuptime']

def posthelpmsg(redditron,input):
    '''
    posts a list of the commands or a help message for a specific command
    '''
    msg=input.split()
    commanddict=redditron.commands
    if len(msg)==1:
        _greet(redditron,input)
        redditron.say(input.source, 'List of commands: '+', '.join(commanddict.keys()))
    else:
        cmd=(' ').join(msg[1:])
        msg=''
        for c in commanddict:
            if cmd == c:
                func=commanddict[c]
                msg=func.__doc__
                if msg:
                    msg=msg.replace('$MYNICK',redditron.nick)
                    msg=msg.strip()
                    redditron.say(input.source,cmd+': '+msg)
        if not msg:
            redditron.say(input.source,"I don't have a help msg for '"+cmd+"'")
posthelpmsg.commands=['help']

def addredditry(redditron, input):
    '''
    Adds a quote to the database along with a tag. Format: $MYNICK: addquote "tag" "quote"'
    '''
    responses=redditron.responses
    msg = input.split('"')
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

def quotegasm(redditron,input):
    '''
    spams a lot of words about something
    '''
    msg = input.split()
    y = 5
    if len(msg)==2:
        try: y=int(msg[1])
        except: pass
    if msg[0] == 'paulgasm':
        for x in range(0,y):
            q=redditron.responses.getquotefor('ron paul')
            redditron.postresponse(input.source,q)
quotegasm.commands=['paulgasm']

def fucksrstk(redditron,input):
    '''
    sends a request to fucksrs.tk to check if a username belongs to an SRSer.
    '''
    msg = input.split()
    if len(msg)==2:
        nomenclature=random.choice(['SRSer','SRSister'])
        url="http://fuckSRS.tk/main/api/"+msg[1]
        try:
            if urlopen(url).read()=='1':
                response=msg[1]+' is an '+nomenclature+'.'
            else: response=msg[1]+' is not an '+nomenclature+'.'
        except:
            response="Couldn't connect to fuckSRS.tk"
    elif len(msg)==1:
        response='gimme a nick so I can check'
    else:
        response='usernames are just one word, silly'
    redditron.say(input.source,response)
fucksrstk.commands=['isasrser','srscheck']

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
    detected, response = redditron.responses.detect(input.strip())
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




