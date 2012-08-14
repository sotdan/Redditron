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
    elif 'shut up' in input.lower() or 'stfu' in input.lower():
        if redditron.nick in input:
            stfu(redditron,input)
    elif re.match('h(ello|ey|i)\ '+ redditron.nick, input.lower()):
        _greet(redditron,input)
    elif re.match(redditron.nick.lower()+'(:|,|\ )', input.lower()):
        if redditron.cooldown == False:
            msg = input.split(' ')
            msg=(' ').join(msg[1:])
            class Origin(object):
                def __init__(self):
                    self.sender=input.source
                    self.nick=input.nick
            origin = Origin()
            input = redditron.input(origin, msg, input.args)
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
        reply=random.choice(redditron.config.greetings)[:-1]+', '+input.nick+'!'
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
partchan.commands=['part']
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
joinchan.commands=['join']
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
ageofconsent.commands=['aoc']

def getquotes(redditron, input):
    '''
    Posts all the quotes for a tag (or just all the quotes) to pastebin.
    '''
    msg = input.split()
    if len(msg) ==1:
        redditron.say(input.source,'Needs a tag.')
    elif len(msg) >= 2:
        withids = 'getqids' in msg[0]
        msg = msg[1:]
        tag = ' '.join(msg).rstrip()
        quotestr = redditron.responses.getquotes(tag, withids)
        if quotestr:
            redditron.say(input.source,_posttopastebin(quotestr))
        else: redditron.say(input.source,"No quotes about '%s'" % tag)
getquotes.commands=['getquotes', 'getqids']

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
    posts a list of all the triggers to pastebin, or gives you the tags for a quote ID.
    '''
    msg = input.split()
    withids = 'gettids' in msg[0]
    if len(msg) == 2:
        try: 
            qid = int(msg[1])
            tags = redditron.responses.gettagsforquote(qid)
            if tags:
                if len(tags) > 1:
                    resp = "The tags for quote no. "+msg[1]+" are: "+", ".join(tags)
                else:
                    resp = "The tag for quote no. "+msg[1]+" is: "+tags[0]
            else: resp = "No tags for that quote ID."
        except: resp = "The quote ID needs to be a number."
    elif len(msg) == 1:
        resp = _posttopastebin(redditron.responses.getkeys(withids))
    else: resp = random.choice(redditron.config.fallbackr)
    redditron.say(input.source, resp)
gettags.commands=['tags','triggers','gettids']

def getquote(redditron, input):
    '''
    says the quote for an ID.
    '''
    msg = input.split()
    if len(msg) == 2:
        try:
            qid = int(msg[1])
            quote = redditron.responses.getquote(qid)
            if quote:
                resp= quote
            else: resp = "No quote for that ID."
        except: resp = "The quote ID needs to be a number."
    else: resp = "Needs a quote ID."
    redditron.say(input.source, resp)
getquote.commands=['getquote']

def delquote(redditron, input):
    '''
    deletes a quote. needs the id of the quote.
    '''
    msg = input.split()
    if len(msg) == 2:
        try:
            qid = int(msg[1])
            resp, quote = redditron.responses.delquote(qid)
            if quote:
                redditron.say(input.source, "Deleted quote: "+quote)
        except: resp = "The quote ID needs to be a number."
    else: resp = "Needs a quote ID."
    redditron.say(input.source, resp)
delquote.commands=['delquote']
delquote.admin=1

def hint(redditron, input):
    '''
    posts a random sample of tags
    '''
    sample = redditron.responses.getsample(7)
    redditron.say(input.source, "AMA about "+sample+", and more.")
hint.commands=['tip']

def stats(redditron, input):
    '''
    Spams some quote-database statistics.
    '''
    redditron.say(input.source, redditron.responses.stats())
stats.commands=['stats']

def getuptime(redditron, input):
    seconds = time.time() - redditron.starttime
    #redditron.say(input.source, 'I have been up and running for %s seconds.' % seconds)
    redditron.say(input.source, 'Uptime: '+str(datetime.timedelta(seconds=seconds)))
getuptime.commands=['uptime']

def posthelpmsg(redditron,input):
    '''
    posts a list of the commands or a help message for a specific command
    '''
    msg=input.split()
    commanddict=redditron.commands
    if len(msg)==1:
        _greet(redditron,input)
        redditron.say(input.source, 'I am a robot and a proud redditor!')
        redditron.say(input.source, 'List of commands: '+', '.join(commanddict.keys()))
        redditron.say(input.source, 'Type '+redditron.nick+': help *command* to get some help with my commands!')
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
        response=responses.add(tag,response)
        redditron.say(input.source,response)
        redditron.logger(response)
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
            redditron.postresponse(input.source,q['quote'])
            redditron.logger('responding with quote no. '+str(q['id']))
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
fucksrstk.commands=['srscheck']

def randomquote(redditron, input):
    '''
    Spams a random quote.
    '''
    response=redditron.responses.randomquote()
    redditron.logger(strftime("%H:%M:%S"))
    redditron.logger('posting random quote: no. '+str(response[0]))
    redditron.postresponse(input.source,response[1])
randomquote.commands=['random']

def detecttrigger(redditron, input):
    detected, response = redditron.responses.detect(input.strip())
    if len(detected)>0:
        redditron.logger(strftime("%H:%M:%S"))
        redditron.logger('detected: '+(', ').join(detected))
        redditron.logger('responding with quote no. '+str(response['id']))
        redditron.postresponse(input.source, response['quote'])
        return True
    else:
        return False

def leave(redditron,input):
    reply= random.choice(redditron.config.spamresponses)
    chan = input.source
    redditron.postresponse(chan, reply)
    msg =input.split()
    redditron.logger(strftime("%H:%M:%S"))
    redditron.logger("parting "+chan+" due to spam")
    redditron.partch(chan)
    time.sleep(100)
    redditron.joinch(chan)





