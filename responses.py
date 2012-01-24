import cPickle as pickle
import random, sys

class Responses(object):
   
   def __init__(self):
       self.quotes = self.loaddb()

   def loaddb(self):
       x=''
       try:
           output=open(sys.path[0]+"/responses.dat")
           x=pickle.load(output)
           output.close()
       except:pass
       if isinstance(x, dict):
           return x
       else: 
           print 'responsefile is not a dict'
           return {}

   def checkiffilechanged(self):
       fromfile = self.loaddb
       if self.quotes!=fromfile:
           self.quotes=fromfile

   def savetofile(self):
       if self.quotes != self.loaddb():
           print 'saving.'
           output = open(sys.path[0]+"/responses.dat",'wb')
           if isinstance(self.quotes, dict):
               pickle.dump(self.quotes, output)
               return 1#saved
           else: 
               print 'quotes are not a dict'
               return 0#didn't save
           output.close()
       else: print 'nothing new to save'
       return 0

   def getkeys(self):
       r=''
       for x in self.quotes.keys():
           r += x+'\n'
       return r.strip()

   def stats(self):
       tags=self.quotes.keys()
       q = 0
       for x in tags:
           if self.quotes[x] == None:
               print 'removing '+x
               del self.quotes[x]
           else:
               q+=len(self.quotes[x])
       return 'There are '+str(len(tags))+' tags and '+str(q)+' quotes.'

   def detect(self, msg):
        response, logmsg="",""
        keys = self.quotes.keys()
        detected=[]
        for key in keys:
            if key in msg:
                detected.append(key)
        if len(detected)>0:
            key = random.choice(detected)
            if self.quotes[key] ==None:
                response = 'error'
            else: 
                responselist = self.quotes[key]
                response = random.choice(responselist)
        return detected, response

   def getresponses(self, msg):
       '''Returns all the responses for a tag'''
       response =""
       try:
           responselist = self.quotes[msg]
           response='Quotes about %s:\n\n' % msg.upper()
           for q in responselist:
               response+=q+'\n\n'
           return True, response
       except: return False, "No quotes about '%s'" % msg

   def getresponseslist(self):
       '''returns a list with all the responses'''
       r=[]
       for x in self.quotes.keys():
           if self.quotes[x] != None:
               for y in self.quotes[x]:
                   r.append(y)
       return r

   def getstring(self):
       '''Returns the db as a fancy string'''
       r=""
       for x in self.quotes.keys():
           if self.quotes[x] != None:
               for y in self.quotes[x]:
                   r+=(x+' --- '+y+'\n\n')
       return r
   
   def searchdb(self, lit):
       '''Returns a list of qid-tag-quote lists'''
       result=[]
       xid=0
       for x in self.quotes.keys():
           xid+=1
           if self.quotes[x] != None:
               yid=0
               for y in self.quotes[x]:
                   yid+=1
                   if lit in y:
                       qid=[xid,yid]
                       result.append([qid,x,y])
       return result
   
   def getallqids(self):
       '''returns a list of all quote IDs'''
       result=[]
       xid=0
       for x in self.quotes.keys():
           xid+=1
           if self.quotes[x] != None:
               yid=0
               for y in self.quotes[x]:
                   yid+=1
                   result.append([xid,yid])
       return result

   def getquoteforqid(self,tagid,responseid):
       xid=0
       result=[]
       for x in self.quotes.keys():
           xid+=1
           if xid==tagid:
               if self.quotes[x] != None:
                   yid=0
                   for y in self.quotes[x]:
                       yid+=1
                       if responseid==yid:
                           result= [x,y]
       return result
                       
   def deletequote(self,xid,yid):
       quote=self.getquoteforqid(xid,yid)
       self.quotes[quote[0]].remove(quote[1])
       self.savetofile()                        

   def deletequoteprompt(self,tagid,responseid):
       quote= self.getquoteforqid(tagid,responseid)
       if quote==[]:
           print 'quote not found'
       else:
           print 'are you sure want to delete: '
           print quote[0]+' - '+quote[1]
           print '? (y/n)'
           msg= raw_input('>>')
           if msg =='y' or msg=='Y':
               self.deletequote(tagid,responseid)
           else: print 'aborted.'

   def randomquote(self):
       vals=self.quotes.values()
       r = random.choice(vals)
       return random.choice(r)
  
   def add(self, tag, response):
       '''return codes:
       0: error - 1: added - 2: quote already exists
       '''
       tag=tag.lower()
       if tag in self.quotes:
           if self.quotes[tag]==None:
               return 0
           else:
               if not response in self.quotes[tag]:
                   self.quotes[tag].append(response)
                   return 1
               else: return 2
       else:
           self.quotes[tag] = [response]
           return 1