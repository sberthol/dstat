### Author: <gianfranco@mongodb.com>

global mongodb_user
mongodb_user = os.getenv('DSTAT_MONGODB_USER') or os.getenv('USER')

global mongodb_pwd
mongodb_pwd = os.getenv('DSTAT_MONGODB_PWD')

global mongodb_host
mongodb_host = os.getenv('DSTAT_MONGODB_HOST') or '127.0.0.1:27017'

class dstat_plugin(dstat):
  """
  Plugin for MongoDB commands.
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

    self.name    = 'mongodb con'
    self.nick    = ('curr', 'avail')
    self.vars    = ('connections.current', 'connections.available')
    self.type    = 'd'
    self.width   = 5
    self.scale   = 2
    self.lastVal = {}

  def extract(self):
    status = self.db.command("serverStatus")

    for name in self.vars:
      self.val[name] = (long(self.getDoc(status, name)))

  def getDoc(self, dic, doc):
    par = doc.split('.')
    sdic = dic
    for p in par:
      sdic = sdic.get(p)

    return sdic
