import re

"""An object of class 'GitServerProjectBranch' uniquely identifies
a GIT branch/heads object of a project that's hosted on a server.
Textual representation of an object of 'GitServerProjectBranch' is of the form
<server>/<project>:<branch> where,
   <project> is the name of the project
   <server> is the name of the host where <project> is hosted
   <branch> refers to refs/heads/<branch> of <project>."""
class GitServerProjectBranch(object):
  #TODO:
    # 1) Add '.git' to project names if it's not already there for consistency
    # 2) Make project and branch required parameters to the constructor
    # 3) Add GIT URL generation support
    # 4) Constructor could accept git urls along with a refspec

  _supported_transport_protocols_syntax = { 
                                            #git://host.xz[:port]/path/to/repo.git
                                            'git': re.compile('^git://([^:/]+)(?::\d+)?(?:/[^/]+)+(?:.git)?$'),
                                            #ssh://[user@]host.xz[:port]/path/to/repo.git
                                            'ssh': re.compile('^ssh://(?:[^@]+@)?([^:/]+)(?::\d+)?(?:/[^/]+)+(?:.git)?$'),
                                          }
  
  @staticmethod
  def validate_and_decompose_url(url):
    m = re.search('^([^:/]+)://', url)
    if not m:
      raise Exception('%s is an invalid URL.' % url)
   
    transport_protocol = m.group(1)
    if transport_protocol not in GitServerProjectBranch._supported_transport_protocols_syntax:
      raise Exception('%s is not a supported transport protocol.' % transport_protocol)
    
    m = GitServerProjectBranch._supported_transport_protocols_syntax[transport_protocol].search(url)
    
    if not m:
      raise Exception('%s is an invalid URL.' % url)

    return {'host':m.group(1)}      
    
  def __init__(self, server='git.quicinc.com', project='', branch='', textual_representation=''):
    if textual_representation:
      #<server>/<project>:<branch>
      #<server>, <project> and <branch> cannot contain ':'
      m = re.search('^([^/:]+)/([^:]+):([^:]+)$', textual_representation)
      if m:
        self.__dict__['_server'], self.__dict__['_project'], self.__dict__['_branch'] = m.group(1,2,3)
        self.__dict__['_textual_representation'] = textual_representation
      else:
        raise Exception('Invalid textual representation. Format is <server>/<project>:<branch>.')
    else:
      self.__dict__['_server'] = server
      self.__dict__['_project'] = project
      self.__dict__['_branch'] = branch
      self.__dict__['_textual_representation'] = self.server + '/' + self.project + ':' + self.branch

  def __setattr__(self, name, value):
    raise Exception("Objects of class '%s' are immutable" % type(self))

  def __str__(self):
    return self._textual_representation

  def __repr__(self):
    return self._textual_representation

  def __eq__(self, other):
    if not (isinstance(other, GitServerProjectBranch) and isinstance(self, GitServerProjectBranch)):
      raise Exception("Cannot compare objects of type '%s' to objects of type '%s'." % (type(self), type(other)))

    return (self.server, self.project, self.branch) == (other.server, other.project, other.branch)

  def __cmp__(self, other):
    if not (isinstance(other, GitServerProjectBranch) and isinstance(self, GitServerProjectBranch)):
      raise Exception("Cannot compare objects of type '%s' to objects of type '%s'." % (type(self), type(other)))

    if (self.server, self.project, self.branch) < (other.server, other.project, other.branch):
      return -1
    elif (self.server, self.project, self.branch) == (other.server, other.project, other.branch):
      return 0
    elif (self.server, self.project, self.branch) > (other.server, other.project, other.branch):
      return 1

  def __hash__(self):
    return hash(self._textual_representation)

  def __nonzero__(self):
    if self.server or self.project or self.branch:
      return True
    else:
      return False

  def generateURL(self, protocol='git', user=None, port=None):
    if protocol not in self._supported_transport_protocols_syntax:
      raise Exception("'%s' is not a supported transport protocol. Supported protocols are %s." % (protocol, self._supported_transport_protocols_syntax.keys()))
    
    if protocol == 'git':
      return self.generateGITURL(port=port)
    elif protocol == 'ssh':
      return self.generateSSHURL(user=user, port=port)
      
  #ssh://[user@]host.xz[:port]/path/to/repo.git
  def generateSSHURL(self, user=None, port=None):
    user_specifier = ''
    if user:
      user_specifier = '%s@' % user
      
    port_specifier = ''
    if port:
      port_specifier = ':%s' % port
      
    return 'ssh://' + user_specifier + self.server + port_specifier + '/' + self.project
    
  #git://host.xz[:port]/path/to/repo.git
  def generateGITURL(self, port=None):
    port_specifier = ''
    if port:
      port_specifier = '%s:' % port
   
    return 'git://' + self.server + port_specifier + '/' + self.project
      
  def getServer(self):
    return self._server

  def getProject(self):
    return self._project

  def getBranch(self):
    return self._branch

  server = property(getServer)
  project = property(getProject)
  branch = property(getBranch)

"""An object of class 'Manifest' uniquely identifies a manifest that's usable by REPO.
Textual representation of an object of 'Manifest' is of the form
<server>/<project>:<branch>:<path> where,
   <project> is the name of the manifest project
   <server> is the name of the host, where <project> is hosted
   <branch> refers to refs/heads/<branch> of <project>
   <path> refers to the path to the manifest file in the manifest project repo"""
class Manifest(GitServerProjectBranch):
  #TODO:
  # 1) Make branch a required parameter to the constructor

  def __init__(self, server='git.quicinc.com', project='platform/manifest',
               branch='', path='default.xml', textual_representation=''):
    if textual_representation:
      #:<branch>:<path> | :<branch> (allows for the path to the manifest be optional)
      m = re.search('^([^:]+:[^:]+)(?::([^:]+))?$', textual_representation)
      if m:
        GitServerProjectBranch.__init__(self, textual_representation=m.group(1))
        if m.group(2):
          self.__dict__['_path'] = m.group(2)
        else:
          self.__dict__['_path'] = path
      else:
        raise Exception('Invalid textual representation. Format is <server>/<project>:<branch>:<path>, where :<path> is optional.')
    else:
      GitServerProjectBranch.__init__(self, server=server, project=project, branch=branch)
      self.__dict__['_path'] = path

    self.__dict__['_textual_representation'] = self._textual_representation + ':' + self.path

  def __eq__(self, other):
    if not (isinstance(other, Manifest) and isinstance(self, Manifest)):
      raise Exception("Cannot compare objects of type '%s' to objects of type '%s'." % (type(self), type(other)))

    return GitServerProjectBranch.__eq__(self, other) and (self.path == other.path)

  def __cmp__(self, other):
    if not (isinstance(other, Manifest) and isinstance(self, Manifest)):
      raise Exception("Cannot compare objects of type '%s' to objects of type '%s'." % (type(self), type(other)))

    result = GitServerProjectBranch.__cmp__(self, other)
    if result == 0:
      if self.path < other.path:
        return -1
      elif self.path == other.path:
        return 0
      elif self.path > other.path:
        return 1
    else:
      return result

  def __hash__(self):
    return hash(self._textual_representation)

  def __nonzero__(self):
    if self.server or self.project or self.branch or self.path:
      return True
    else:
      return False

  def getPath(self):
    return self._path

  path = property(getPath)