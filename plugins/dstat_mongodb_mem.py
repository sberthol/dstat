### Author: <gianfranco@mongodb.com>
import sys, os

global mongodb_user
mongodb_user = os.getenv('DSTAT_MONGODB_USER') or os.getenv('USER')

global mongodb_pwd
mongodb_pwd = os.getenv('DSTAT_MONGODB_PWD')

global mongodb_host
mongodb_host = os.getenv('DSTAT_MONGODB_HOST') or '127.0.0.1:27017'

class dstat_plugin(dstat):
  """
  Plugin for MongoDB.
  """
  def __init__(self):
    global pymongo
    import pymongo

    try:
      self.m = pymongo.MongoClient(mongodb_host)
      if mongodb_pwd:
        self.m.admin.authenticate(mongodb_user, mongodb_pwd)
      self.db = self.m.admin
    except Exception, e:
      raise Exception, 'Cannot interface with MongoDB server: %s' % e

    line = self.db.command("serverStatus")
    if 'storageEngine' in line:
      self.storageEngine = line.get('storageEngine').get('name')
    else:
      self.storageEngine = 'mmapv1'

    self.name    = 'mongodb mem'
    self.nick    = ('res', 'virt')
    self.vars    = ('mem.resident', 'mem.virtual')
    self.types   = ('b', 'b')
    self.width   = 5
    self.scale   = 2
    self.lastVal = {}

    if self.storageEngine == 'mmapv1':
      self.nick  = self.nick + ('map', 'mapj', 'flt')
      self.vars  = self.vars + ('mem.mapped', 'mem.mappedWithJournal', 'extra_info.page_faults')
      self.types = ('b', 'b', 'b', 'b', 'd')


  def extract(self):
    status = self.db.command("serverStatus")

    for name in self.vars:
      if name in ('extra_info.page_faults'):
        if not name in self.lastVal:
          self.lastVal[name] = long(self.getDoc(status, name))
        self.val[name] = (long(self.getDoc(status, name)) - self.lastVal[name])
        self.lastVal[name] = self.getDoc(status, name)
      else:
        self.val[name] = (long(self.getDoc(status, name)))



  def getDoc(self, dic, doc):
    par = doc.split('.')
    sdic = dic
    for p in par:
      sdic = sdic.get(p)

    return sdic
