import sys, cPickle, responses
'''
loads quotes from a txt file to a pickle file'''


RESPONSES = responses.Responses()


def writetotxtfile():
    f = open(sys.path[0]+'/db.txt', 'w')
    for x in RESPONSES.quotes.keys():
        if RESPONSES.quotes[x] == None:
            print RESPONSES[x]
        else:
            for y in RESPONSES.quotes[x]:
                f.write(x+' --- '+y+'\n')

def addresponses():
    f = open(sys.path[0]+'/db.txt', 'r')
    for line in f:
        msg = line.split(" --- ")
        if len(msg) == 2:
            tag=msg[0]
            response=msg[1].rstrip()
            print 'adding: "'+response+'" with the tag '+tag
            RESPONSES.add(tag,response)
    RESPONSES.dumptofile()

def stats():
    print RESPONSES.stats()

def q():
    sys.exit(0)

def main():
    while True:
        print '>>stats | addresponses | writetotxtfile'
        msg= raw_input('>>')
        msg = msg+'()'
        try: eval(msg)
        except: print 'wrong command'

if __name__ == '__main__': 
   main()