#!/usr/bin/env python

import random, sys, unicodedata, sqlite3, re

def decode(bytes):
    try: text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try: text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text

def fits(needle, haystack):
    #haystack = haystack.encode('ascii','ignore').strip()
    rx = r'\b{0}'.format(needle)
    rexp = re.compile(rx)
    res = rexp.search(haystack)
    return res is not None

class Responses(object):

    def __init__(self):
        self.con = sqlite3.connect('rq.db')
        self.con.create_function('fits', 2, fits)

    def getkeys(self, withids):
        cur = self.con.cursor()
        cur.execute("select id, tag from tags")
        if withids:
            return ('\n').join([str(row[0])+'. '+row[1] for row in cur.fetchall()])
        else:
            return ('\n').join([row[1] for row in cur.fetchall()])

    def getsample(self, amount):
        '''returns a list with a random sample of tags.'''
        cur = self.con.cursor()
        cur.execute("select tag from tags order by random() limit ?", (amount,))
        return (', ').join([row[0] for row in cur.fetchall()])

    def stats(self):
        cur = self.con.cursor()
        cur.execute("select count(id) from tags")
        tag_count = cur.fetchall()[0][0]
        cur.execute("select count(id) from quotes")
        q_count = cur.fetchall()[0][0]
        return 'There are '+str(tag_count)+' tags and '+str(q_count)+' quotes.'

    def getquotefor(self, tag):
        '''
        returns a random quote for a tag, or for a list of tags
        '''
        cur = self.con.cursor()
        tags = [tag] if (type(tag) == type("")) else tag
        q = """select quote from 
                quotes join connections on (quotes.id = connections.qid) 
                join tags on (tags.id = connections.tid)
                where tag in ({0}) 
                order by random() limit 1""".format(",".join(["?" for _ in tag]))
        cur.execute(q, tuple(tags))
        quote = cur.fetchall()
        if quote:
            return str(quote[0][0])
        else: return quote

    def detect(self, msg):
        '''checks if there are any triggers in a string'''
        cur = self.con.cursor()
        q = 'select tag from tags where FITS(tag, ?)'
        cur.execute(q, (msg.lower(),))
        tags = [tag for (tag,) in cur.fetchall()]
        resp = self.getquotefor(tags)
        return tags, resp

    def getquotes(self, tag, withid):
        '''Returns a string representation of all the responses for a tag'''
        cur = self.con.cursor()
        cur.execute("""select quotes.id, quote from 
                    quotes join connections on (quotes.id = connections.qid) 
                    join tags on (tags.id = connections.tid)
                    where tag = ?""", (tag,))
        rows = cur.fetchall()
        if rows:
            response= str(len(rows))+' quotes about %s:\n\n' % tag.upper()
            if withid:
                response+=('\n\n').join([str(row[0])+". "+row[1] for row in rows])
            else:
                response+=('\n\n').join([row[1] for row in rows])
            return response
        else: return False

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
                    cur.execute("select qid from connections where (tid = ?)", (nl[0],))
                    targetqids = cur.fetchall()
                    for targetqid in targetqids:
                        cur.execute("select * from connections where (tid = ? and qid = ?)", (tagtuple[0], targetqid))
                        if cur.fetchall() > 0:
                            cee+=1

        response+='Need to move: '+str(cee)
        return response


    def randomquote(self):
        cur = self.con.cursor()
        cur.execute("select quote from quotes order by RANDOM() LIMIT 1")
        return cur.fetchall()[0][0]

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
        cur.execute(u'select id from tags where (tag = ?)', (tag,))
        rows = cur.fetchall()
        if len(rows) != 0:
            tid = rows[0][0]
        else:
            cur.execute(u'insert into tags (tag) values (?)', (tag,))
            tid = cur.lastrowid
            self.con.commit()

        #add the quote if it doesn't exist
        cur.execute(u'select id from quotes where (quote = ?)', (quote,))
        rows = cur.fetchall()
        if len(rows) != 0:
            qid = rows[0][0]
        else:
            cur.execute(u"insert into quotes (quote) values (?)", (quote,))
            qid = cur.lastrowid
            self.con.commit()

        #add the connection if it doesn't exist
        cur.execute(u'select * from connections where (qid = ? and tid = ?)', (qid, tid))
        rows = cur.fetchall()
        if len(rows) != 0:
            return "The exact quote already exists."
        else:
            cur.execute('insert or ignore into connections (tid, qid) values (?, ?)', (tid, qid))
            self.con.commit()
            return 'Added a new quote to the tag "{0}".'.format(tag)