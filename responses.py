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
    res = rexp.search(haystack.lower())
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

    def delorphantags(self):
        '''
        finds and deletes tags that are not associated with any quotes
        '''
        cur = self.con.cursor()
        q= '''
           select tags.id, tags.tag, count(connections.id) as c 
           from tags left join connections on (connections.tid = tags.id) 
           group by tags.id having c = 0;
           '''
        cur.execute(q)
        rows = cur.fetchall()
        tags = [tag[1] for tag in rows]
        tids = [tag[0] for tag in rows]
        if tids:
            q = """
                delete from 
                tags where id in ({0})""".format(",".join(["?" for _ in tids]))
            cur.execute(q, tuple(tids))
            self.con.commit()
        return tags

    def gettagsforquote(self, qid):
        '''
        returns a list of tags for a qid
        '''
        cur=self.con.cursor()
        q = '''select tag from
               tags where id in
               (select tid from connections
                where qid = ?)
            '''
        cur.execute(q, (qid,))
        rows = cur.fetchall()
        if rows:
            return [row[0] for row in rows]
        else: return rows

    def getquote(self, qid):
        '''
        returns the quote for a quote id
        '''
        cur = self.con.cursor()
        cur.execute("select quote from quotes where id = ?", (qid,))
        rows = cur.fetchall()
        if rows:
            return rows[0][0]
        else: return rows

    def delquote(self, qid):
        '''
        deletes a quote
        '''
        cur = self.con.cursor()
        quote = self.getquote(qid)
        if quote:
            #delete the quote
            cur.execute("delete from quotes where id = ?", (qid,))
            #delete its connections
            cur.execute("delete from connections where qid = ?", (qid,))
            self.con.commit()
            resp = "Deleted quote no. "+str(qid)+"."
            deltags = self.delorphantags()
            if deltags:
                resp+=" Deleted the tags: "+", ".join(deltags)
        else: resp = "There is no quote for that ID."
        return resp, quote
            
    def getquotefor(self, tag):
        '''
        returns a random quote for a tag, or for a list of tags
        '''
        cur = self.con.cursor()
        tags = [tag] if (type(tag) == type("")) else tag
        q = """select quotes.id, quote from 
                quotes join connections on (quotes.id = connections.qid) 
                join tags on (tags.id = connections.tid)
                where tag in ({0}) 
                order by random() limit 1""".format(",".join(["?" for _ in tags]))
        cur.execute(q, tuple(tags))
        quote = cur.fetchall()
        if quote:
            return dict(id = quote[0][0], quote=quote[0][1])
        else: return "This is an orphaned tag."

    def detect(self, msg):
        '''checks if there are any triggers in a string'''
        cur = self.con.cursor()
        q = 'select tag from tags where FITS(tag, ?)'
        cur.execute(q, (msg,))
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

    def randomquote(self):
        '''
        returns a tuple with a random quote and its ID
        '''
        cur = self.con.cursor()
        cur.execute("select id, quote from quotes order by RANDOM() LIMIT 1")
        return cur.fetchall()[0]

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