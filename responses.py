#!/usr/bin/env python

import random, sys, unicodedata, sqlite3

def decode(bytes):
    try: text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try: text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text

class Responses(object):

    def __init__(self):
        self.con = sqlite3.connect('rq.db')

    def getkeys(self):
        cur = self.con.cursor()
        cur.execute("select tag from tags")
        return ('\n').join([row[0] for row in cur.fetchall()])

    def getsample(self, amount):
        '''returns a list with a random sample of tags.'''
        cur = self.con.cursor()
        cur.execute("select tag from tags")
        return (', ').join([row[0] for row in random.sample(cur.fetchall(), amount)])

    def stats(self):
        cur = self.con.cursor()
        cur.execute("select id from tags")
        tags = cur.fetchall()
        cur.execute("select id from quotes")
        q = cur.fetchall()
        return 'There are '+str(len(tags))+' tags and '+str(len(q))+' quotes.'

    def getquotefor(self,msg):
        '''
        returns a random quote for a tag
        '''
        cur = self.con.cursor()
        cur.execute('select id from tags where (tag = "{0}")'.format(msg))
        tid = cur.fetchall()[0][0]
        cur.execute('select qid from connections where (tid = {0})'.format(tid))
        qids = [row[0] for row in cur.fetchall()]
        qid = random.choice(qids)
        cur.execute("select quote from quotes where (id = {0})".format(qid))
        return str(cur.fetchall()[0][0])

    def detect(self, msg):
        '''checks if there are any triggers in a string'''
        cur = self.con.cursor()
        cur.execute("select id, tag from tags")
        tags = [dict(id= row[0],tag= row[1]) for row in cur.fetchall()]
        response=""
        detected=[]
        for t in tags:
            if t['tag']+' ' in ' '+msg.lower()+' ' or ' '+t['tag'] in ' '+msg.lower()+' ':
                detected.append(t)
        if len(detected)>0:
            key = random.choice(detected)
            cur.execute('select qid from connections where (tid = {0})'.format(key['id']))
            qids = [row[0] for row in cur.fetchall()]
            if len(qids)>0:
                qid = random.choice(qids)
                cur.execute('select quote from quotes where (id = {0})'.format(qid))
                response = str(cur.fetchall()[0][0])
        return [d['tag'] for d in detected], response

    def getresponses(self, msg):
        '''Returns all the responses for a tag'''
        cur = self.con.cursor()
        cur.execute('select id from tags where (tag = "{0}")'.format(msg))
        rows = cur.fetchall()
        quotes = []
        if len(rows) >0:
            tid = rows[0][0]
            cur.execute('select qid from connections where (tid = {0})'.format(tid))
            for row in cur.fetchall():
                cur.execute('select quote from quotes where (id = {0})'.format(row[0]))
                quotes.append(cur.fetchall()[0][0])
        return quotes

    def fixdb(self):
        response=""
        cur = self.con.cursor()


        #find tags that are not lowercase and fix them
        cur.execute("select * from tags")
        tagtuples = cur.fetchall()
        notlower=[]
        for tagtuple in tagtuples:
            if not str(tagtuple[1]).islower():
                notlower.append(tagtuple)
        response+= "tags that are not lowercase: "+str(len(notlower))+'\n'
        response+=", ".join([t[1] for t in notlower])+'\n'
        cee=0
        for nl in notlower:
            nll = nl[1].lower()
            for tagtuple in tagtuples:
                if nll == tagtuple[1]:
                    cur.execute("select qid from connections where (tid = {0})".format(nl[0]))
                    targetqids = cur.fetchall()
                    for targetqid in targetqids:
                        cur.execute("select * from connections where (tid = {0} and qid = {1})".format(tagtuple[0], targetqid))
                        if cur.fetchall() > 0:
                            cee+=1

        response+='Need to move: '+str(cee)
        return response



    def randomquote(self):
        cur = self.con.cursor()
        cur.execute("select quote from quotes")
        return random.choice(cur.fetchall())[0]

    def add(self, tag, quote):
        '''
        adds a quote to the database
        '''

        if isinstance(tag, unicode):
            tag = tag.lower()
        else: tag=unicode(tag.lower())
        if isinstance(quote, unicode):
            pass
        else: quote=unicode(quote)
        cur = self.con.cursor()

        #add the tag if it doesn't exist
        cur.execute(u'select id from tags where (tag = "{0}")'.format(tag))
        rows = cur.fetchall()
        if len(rows) != 0:
            tid = rows[0][0]
        else:
            cur.execute(u'insert into tags (tag) values ("{0}")'.format(tag))
            tid = cur.lastrowid
            self.con.commit()

        #add the quote if it doesn't exist
        cur.execute(u'select id from quotes where (quote = "{0}")'.format(quote))
        rows = cur.fetchall()
        if len(rows) != 0:
            qid = rows[0][0]
        else:
            cur.execute(u"insert into quotes (quote) values (?)", [quote])
            qid = cur.lastrowid
            self.con.commit()

        #add the connection if it doesn't exist
        cur.execute(u'select * from connections where (qid = ? and tid = ?)', (qid, tid))
        rows = cur.fetchall()
        if len(rows) != 0:
            return "The exact quote already exists."
        else:
            cur.execute('insert or ignore into connections (tid, qid) values ({0}, {1})'.format(tid,qid))
            self.con.commit()
            return 'Added a new quote to the tag "{0}".'.format(tag)


