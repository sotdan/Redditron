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
        cur.execute("select id from tags where (tag = {0})".format(msg))
        responses = [row[0] for row in cur.fetchall()]
        try: return random.choice(responses)
        except: return 'no quotes for '+msg

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
        cur.execute("select id from tags where (tag = '{0}')".format(msg))
        rows = cur.fetchall()
        if len(rows) >0:
            quotes = []
            tid = rows[0][0]
            cur.execute('select qid from connections where (tid = {0})'.format(tid))
            for row in cur.fetchall():
                cur.execute('select quote from quotes where (id = {0})'.format(row[0]))
                quotes.append(cur.fetchall()[0][0])
            response='Quotes about %s:\n\n' % msg.upper()
            return response+('\n\n').join(quotes)
        else: return False, "No quotes about '%s'" % msg

    def randomquote(self):
        cur = self.con.cursor()
        cur.execute("select quote from quotes")
        return random.choice(cur.fetchall())[0]
  
    def add(self, tag, quote):
        '''
        adds a quote to the database
        '''
        
        if isinstance(tag, unicode):
            pass
        else: tag=unicode(tag.lower())
        if isinstance(quote, unicode):
            pass
        else: quote=unicode(quote)
        cur = self.con.cursor()
        cur.execute("select id from tags where (tag = '{0}')".format(tag))
        rows = cur.fetchall()
        tagexists= False
        if len(rows) != 0:
            tagexists, tid = True, rows[0][0]
        else:
            cur.execute(u'insert into tags (tag) values ("{0}")'.format(tag))
            tid = cur.lastrowid
            self.con.commit()
        cur.execute(u'select id from quotes where (quote ="{0}")'.format(quote))
        rows = cur.fetchall()
        if len(rows) == 0:
            cur.execute(u"insert into quotes (quote) values (?)", [quote])
            qid = cur.lastrowid
            cur.execute('insert or ignore into connections (tid, qid) values ({0}, {1})'.format(tid,qid))
            self.con.commit()
            return 'Added a new quote to the tag "{0}".'.format(tag)
        else:
            if tagexists:
                return "The exact quote already exists."
            else:
                qid = rows[0][0]
                cur.execute('insert or ignore into connections (tid, qid) values ({0}, {1})'.format(tid,qid))
                self.con.commit()
                return 'Added a new tag to the quote.'

