import sys, MySQLdb

#exports the db to a text file

mysqlhost = 'localhost'
mysqluser = 'sotdan'
mysqlpassword = 'neckbeard'
database = 'redditron'


db = MySQLdb.connect(host=mysqlhost, user=mysqluser, 
                     passwd=mysqlpassword, db=database)
cursor = db.cursor()
cursor.execute("SELECT id FROM responses")
keys = cursor.fetchall()

f = open('db.txt', 'w')
for x in keys:
    cursor.execute(
        "SELECT keyword FROM responses WHERE id = '%s'" % (x[0]))
    key = str(cursor.fetchall()[0][0])
    cursor.execute(
        "SELECT response FROM responses WHERE id = '%s'" %(x[0]))
    response = str(cursor.fetchall()[0][0])
    print key
    f.write(key+' --- '+response+'\n')
