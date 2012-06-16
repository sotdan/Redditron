import sys, cPickle, responses, sqlite3, unicodedata
'''
loads quotes from a txt file to a pickle file'''


RESPONSES = responses.Responses()

def decode(bytes):
    try: text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try: text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text


def writetotxtfile(args):
    if len(args)>0:
        filename = args[0]
        f = open(sys.path[0]+'/'+filename, 'w')
        f.write(RESPONSES.getstring())
        print 'done.'
        f.close()
    else: 
        print 'writes responses to a txt file'
        print 'needs a filename as an argument'

def addresponses(args):
    if len(args)>0:
        filename = args[0]
        f = open(sys.path[0]+'/'+filename, 'r')
        f.write(RESPONSES.getstring())
        print 'done.'
    else:
        print 'adds responses from a txt file'
        print 'needs filename as an argument'
        return
    errors,new,alreadyexist=0,0,0
    for line in f:
        msg = line.split(" --- ")
        if len(msg) == 2:
            tag=msg[0]
            response=msg[1].rstrip()
            rc=RESPONSES.add(tag,response)
            if rc==0:
                errors+=1
            elif rc==1: 
                new+=1
            elif rc==2:
                alreadyexist+=1
    RESPONSES.savetofile()
    print '%s error(s) while adding' %str(errors)
    print 'Added %s new quote(s).' % str(new)
    print '%s quote(s) already existed' % str(alreadyexist)
    stats('')

def reviewquotesbyqid(qids):
    for qid in qids:
        quote= RESPONSES.getquoteforqid(qid[0],qid[1])
        if quote==[]:
            pass
        else:
            print '\n'+quote[0].upper()
            print quote[1]+'\n'
            msg= raw_input('>> enter d to delete or q to return: ')
            if msg == 'd' or msg == 'D':
                RESPONSES.deletequoteprompt(qid[0],qid[1])
            elif msg == 'q':
                print 'exiting review'
                return    


def reviewquotes(args):
    reviewquotesbyqid(RESPONSES.getallqids())

def findnotstr(args):
    addednew,tagnotstr,quotenotstr=0,0,0
    for qid in RESPONSES.getallqids():
        quote= RESPONSES.getquoteforqid(qid[0],qid[1])
        if quote==[]:
            print 'invalid qid'
        else:
            if not isinstance(quote[0],str):
                print quote
                tagnotstr+=1
                rc=RESPONSES.add(quote[0],quote[1])
                if rc==0:
                    print 'error while adding'
                elif rc==1: 
                    print 'added as str! \n'
                    addednew +=1
                elif rc==2:
                    print 'quote already exists'
                #RESPONSES.deletequoteprompt(qid[0],qid[1])
            if not isinstance(quote[1],str):
                quotenotstr+=1
    print '%s tags and %s quotes are not strings' % (tagnotstr,quotenotstr)
    print 'added %s new quotes as str' % addednew


def stats(args):
    print RESPONSES.stats()

def search(args):
    if len(args) == 0:
        print 'needs an argument'
    else:
        lit=' '.join(args)
        result=RESPONSES.searchdb(lit)
        print 'found %s matches' % len(result)
        for x in result:
            print 'Quote ID: '+str(x[0])
            print x[1]+' --- '+x[2]
        if len(result)>0:
            msg= raw_input('>> enter r to review these quotes: ')
            if msg=='r':
                qids=[]
                for x in result:
                    qids.append(x[0])
                reviewquotesbyqid(qids)

def delete(args):
    if len(args) == 2:
        if args[0].isdigit() and args[1].isdigit():
            RESPONSES.deletequoteprompt(int(args[0]), int(args[1]))
        else: print 'args need to be digits'
    else: print 'needs args'

def todb(args):
    if len(args) == 1:
        con = sqlite3.connect(args[0])
        cur = con.cursor()
        for qid in RESPONSES.getallqids():
            tagquote= RESPONSES.getquoteforqid(qid[0],qid[1])
            tagquote[0] = decode(tagquote[0])
            tagquote[1] = decode(tagquote[1])
            if isinstance(tagquote[0], unicode):
                tag = tagquote[0]
            else: tag=unicode(tagquote[0].lower())
            if isinstance(tagquote[1], unicode):
                quote = tagquote[1]
            else: quote=unicode(tagquote[1])
            cur.execute(u'select id from tags where (tag = "{0}")'.format(tag))
            rows = cur.fetchall()
            if len(rows) == 0:
                cur.execute(u'insert into tags (tag) values (?)',
                        [tag])
                tid = cur.lastrowid
                con.commit()
            else:
                tid = rows[0][0]
            cur.execute(u'select id from quotes where (quote = "{0}")'.format(quote))
            rows = cur.fetchall()
            if len(rows) == 0:
                cur.execute(u'insert into quotes (quote) values (?)',
                     [quote])
                qid = cur.lastrowid
                con.commit()
            else:
                qid = rows[0][0]
            cur.execute('insert or ignore into connections (tid, qid) values ({0}, {1})'.format(tid,qid))
            con.commit()
            print "added "+str(tagquote)+" in "+str(tid)+", "+str(qid)
    else:
        print "needs an arg"


def main():
    while True:
        msg= raw_input('>>')
        if msg == u'q':
            sys.exit("Bye")
        if msg == u'help':
            print 'stats | addresponses | writetotxtfile | reviewquotes | todb'
        else:
            args=[]
            if len(msg.split())>1:
                msg=msg.split()
                args=msg[1:]
                msg=msg[0]
            msg = msg+'(args)'
            eval(msg)
            #try: eval(msg)
            #except: 
            #    print sys.exc_info()


if __name__ == '__main__': 
   main()