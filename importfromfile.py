import sys, MySQLdb

#imports to the db from a text file

mysqlhost = 'localhost'
mysqluser = 'sotdan'
mysqlpassword = 'neckbeard'
database = 'redditron'

f = open('scriptz/irc-bot/db', 'r')

for line in f:
    msg = line.split(" --- ")
    if len(msg) == 2:
        tag=msg[0]
        response=msg[1].rstrip()
        response=response.replace("'","\\'")
        db = MySQLdb.connect(host=mysqlhost, user=mysqluser, 
                                 passwd=mysqlpassword, db=database)
        cursor = db.cursor()
        print 'adding: "'+response+'" with the tag '+tag
        cursor.execute("INSERT INTO responses VALUES ('', '%s', '%s')" % (tag,response))