import sys, MySQLdb

#imports to the db from a text file


BOTADMIN = 'sotdan'
mysqlhost = 'localhost'
mysqluser = 'sotdan'
mysqlpassword = 'neckbeard'
database = 'redditron'

f = open('db.txt', 'r')


def setbotadmin(nick):
    dbcmd("INSERT INTO botadmins VALUES ('%s')" % (nick))

def dbcmd(msg):
    try:
        db = MySQLdb.connect(host=mysqlhost, user=mysqluser, 
                         passwd=mysqlpassword, db=database)
        cursor = db.cursor()
        cursor.execute(msg)
        return cursor.fetchall()
    except:
        print "database error"
        return ()

for line in f:
    msg = line.split(" --- ")
    if len(msg) == 2:
        tag=msg[0]
        response=msg[1].rstrip()
        response=response.replace("'","\\'")
        print 'adding: "'+response+'" with the tag '+tag
        dbcmd("INSERT INTO responses VALUES ('', '%s', '%s')" % (tag,response))
        
setbotadmin(BOTADMIN)

