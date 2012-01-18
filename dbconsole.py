import sys, cPickle, responses
'''
loads quotes from a txt file to a pickle file'''


RESPONSES = responses.Responses()


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

def main():
    while True:
        msg= raw_input('>>')
        if msg == u'q':
            sys.exit("Bye")
        if msg == u'help':
            print 'stats | addresponses | writetotxtfile | reviewquotes'
        else:
            args=[]
            if len(msg.split())>1:
                msg=msg.split()
                args=msg[1:]
                msg=msg[0]
            msg = msg+'(args)'
            #eval(msg)
            try: eval(msg)
            except: 
                print sys.exc_info()[1]


if __name__ == '__main__': 
   main()