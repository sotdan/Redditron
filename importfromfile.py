import sys, cPickle
'''
loads quotes from a txt file to a pickle file'''


RESPONSEFILE = sys.path[0]+"/responses.dat"
RESPONSES = {}

f = open(sys.path[0]+'/db.txt', 'r')


for line in f:
    msg = line.split(" --- ")
    if len(msg) == 2:
        tag=msg[0]
        response=msg[1].rstrip()
        print 'adding: "'+response+'" with the tag '+tag
        if tag in RESPONSES:
            RESPONSES[tag].append(response)
        else:
            RESPONSES[tag] = ([response])
output = open(RESPONSEFILE, 'wb')
cPickle.dump(RESPONSES, output)

