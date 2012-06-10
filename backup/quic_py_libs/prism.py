#!/usr/bin/env python2.6

from datetime import datetime, timedelta
from suds.client import Client
from suds.transport import http
from suds.transport.https import WindowsHttpAuthenticated
from suds import WebFault
import logging

#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds').setLevel(logging.DEBUG)

class Prism:
  def __init__(self, server, authfile):
    self.server = server
    self.CR_url = "http://" + self.server + "/ChangeRequestWebService.svc?wsdl"
    self.search_url = "http://" + self.server + "/SearchService.svc?wsdl"

    try:
      f = open(authfile)
      user = f.readline()
      user = user.rstrip()
      passwd = f.readline()
      passwd = passwd.rstrip()
    except ValueError:
      print "ERROR: Invalid authentication file."
      exit(1)

    self.CR_soapclient = Client(self.CR_url,
      transport=WindowsHttpAuthenticated(username=user, password=passwd))
    self.search_soapclient = Client(self.search_url,
      transport=WindowsHttpAuthenticated(username=user, password=passwd))

  def getChangeRequestById(self, key):
    request = self.CR_soapclient.factory.create('ns2:CRRequest')
    request['ChangeRequestId'] = str(key)
    response = self.CR_soapclient.service.GetChangeRequestById([request])
    return response['ChangeRequest']

  def saveChangeRequest(self, CR):
    if not CR['Analysis']['Text']:
      CR['Analysis']['Text'] = ''
    request = self.CR_soapclient.factory.create('ns4:SaveCRRequest')
    request['ChangeRequest'] = CR
    request['UserName'] = 'lnxbuild'
    response = {}
    try:
      response = self.CR_soapclient.service.SaveChangeRequest([request])
    except WebFault as e:
      response = None
      if "read-only" in "%s" % e:
        print "Error: Insufficient permissions to update CR %s" % CR['Id']
        print "  Please check the participant's subsystems on the CR."
      else:
        print "Error: Could not save CR %s" % CR['Id']
        print e
    if response and type(response) != str:
      return response['ChangeRequestId']
    elif type(response) == str:
      print "Error: %s" % response
      return 0
    else:
      return 0

  def editObject(self, obj, **kwargs):
    for key, value in kwargs.iteritems():
      if key in obj:
        obj[key] = value
    return obj

  def updateChangeRequest(self, CR, **kwargs):
    newCR=editObject(CR, kwargs)
    saveChangeRequest(newCR)

  def updateChangeRequestById(self, CRkey, **kwargs):
    CR = getChangeRequestById(CRkey)
    return updateChangeRequest(CR, kwargs)

  def search(self, criteria, results=100):
    """Search PRISM using for CR's matching all of the criteria specified.
       criteria - an array of tuples in the form ('field', 'operator', 'value')
       results - the maximum number of results to return
    """
    request = self.search_soapclient.factory.create('ns6:SearchRequest')
    request['Paging']['PageNumber'] = 1
    request['Paging']['PageSize'] = results
    request['SearchParameters']['Operator'] = 'And'
    request['ViewName'] = 'ChangeRequestsView'
    filters = request['SearchParameters']['Criteria']['SearchCriteriaEntity']

    for cri in criteria:
      criterion=self.search_soapclient.factory.create('ns3:ItemCriteriaEntity')
      criterion['Criteria']['FieldName'] = cri[0]
      criterion['Criteria']['Operator'] = cri[1]
      criterion['Criteria']['FieldValue'] = cri[2]
      criterion['Operator'] = 'And'
      filters.append(criterion)

    response = self.search_soapclient.service.Search(request)

    ret = []
    if response['SearchResults']:
      for CR in response['SearchResults']['PrismSearchResult']:
        for field in CR['Fields']['Field']:
          if field['FieldName'] == 'CRId':
            ret.append(field['FieldValue'])
            continue
    return ret

  def getCRsByGerritUrl(self, url, results=100):
    return self.search([('PLGerritCodeChangeUrl', 'Equals', url),
                        ('PLStatus', 'NotEqual', 'Ready') ], results=results)

  def getGerritURLsByCR(self, CR_ID, validPLStatus=None):
    gerritURLs = {}
    CR = self.getChangeRequestById(CR_ID)
    CR_PLs = CR['ProductLines']['ProductLineEntity']
    for pl in CR_PLs:
      if validPLStatus and pl['Status'] not in validPLStatus:
        continue
      urls = []
      if pl['CodeChangeReferences']:
        for ref in pl['CodeChangeReferences']['CodeChangeReference']:
          urls.append(ref['CodeChangeUrl'])
      gerritURLs[pl['ProductLineName']] = urls
    return gerritURLs

  def getReleaseNotesStatusByCR(self, CR_ID):
    CR = self.getChangeRequestById(CR_ID)
    return CR['ReleaseNotes']['ReleaseNotesStatus']

  def getCRTitleAndDescription(self, CR_ID):
    CR = self.getChangeRequestById(CR_ID)
    summary = CR['Title']
    desc = CR['Description']
    return summary, desc

  def removeGerritRefFromCR(self, CR_ID, PL, gerrit_url):
    removed = 0
    CR = self.getChangeRequestById(CR_ID)
    CR_PLs = CR['ProductLines']['ProductLineEntity']
    code_refs = None
    for pl in CR_PLs:
      if pl['ProductLineName'] == PL:
        if 'CodeChangeReferences' in pl:
          code_refs = pl['CodeChangeReferences']['CodeChangeReference']
        else:
          code_refs = None
      if code_refs:
        for ref in code_refs:
          if ref['CodeChangeUrl'] == gerrit_url:
            code_refs.remove(ref)
            removed += 1
    if removed:
      ret = self.saveChangeRequest(CR)
    else:
      ret = None
    return (removed, ret)

  def addGerritRefToCR(self, CR_ID, PL, target=None, gerrit_url=None,
                         workflow_url=None, add_new_pls=False):
    codeRef = self.CR_soapclient.factory.create('ns2:CodeChangeReference')
    codeRef['System'] = 'Gerrit'
    if gerrit_url:
      codeRef['CodeChangeUrl'] = gerrit_url
    if workflow_url:
      codeRef['IntegrationWorkflowUrl'] = workflow_url

    added = 0
    CR = self.getChangeRequestById(CR_ID)
    CR_PLs = CR['ProductLines']['ProductLineEntity']
    code_refs = None
    found = False
    for pl in CR_PLs:
      if pl['ProductLineName'] == PL:
        code_refs = pl['CodeChangeReferences']
        if not code_refs:
          code_refs=self.CR_soapclient.factory.create('ns2:ArrayOfCodeChangeReference')
          pl['CodeChangeReferences'] = code_refs
        found = True
        break
    if (not found) and add_new_pls:
      CR = self.addPLtoCR(CR, PL, target)
      pl = CR_PLs[-1]
      code_refs=self.CR_soapclient.factory.create('ns2:ArrayOfCodeChangeReference')
      pl['CodeChangeReferences'] = code_refs
    if code_refs:
      add=True
      for ref in code_refs['CodeChangeReference']:
        if ref['CodeChangeUrl'] == codeRef['CodeChangeUrl']:
          add=False
      if add:
        added += 1
        code_refs['CodeChangeReference'].append(codeRef)

    if added:
      ret = self.saveChangeRequest(CR)
    else:
      ret = None
    return (added, ret)

  def addPLtoCR(self, CR, PL, target):
    newPL = self.CR_soapclient.factory.create('ns2:ProductLineEntity')
    newPL['ProductLineName'] = PL
    newPL['Status'] = 'Analysis'
    newPL['AnalysisDueDate'] = datetime.now() + timedelta(days=7)
    newPL['Priority'] = 1
    newPL['TargetName'] = target
    CR['ProductLines']['ProductLineEntity'].append(newPL)
    return CR

  def addSoftwareUnitToCR(self, CR, PL, VU, saveCR=False):
    swUnit = self.CR_soapclient.factory.create('ns2:SoftwareUnit')
    swUnit['Name'] = VU['Name']
    swUnit['UnitVersion'] = VU['Version']
    swUnit['EmailText'] = VU['Text']

    CR_PLs = CR['ProductLines']['ProductLineEntity']
    sw_units = None
    found = False
    for pl in CR_PLs:
      if pl['ProductLineName'] == PL:
        sw_units = pl['SoftwareUnits']
        if not sw_units:
          sw_units=self.CR_soapclient.factory.create('ns2:ArrayOfSoftwareUnit')
          pl['SoftwareUnits'] = sw_units
        found = True
        break
    if not found:
      return (1, "Could not find PL")
    sw_units['SoftwareUnit'].append(swUnit)
    if saveCR:
      self.saveChangeRequest(CR)
    return (CR)

  def movePLsToFixed(self, CR_ID, PLs):
    return self.updatePLsStatus(CR_ID, PLs, 'Fix')

  def movePLsToReady(self, CR_ID, PLs, VUs):
    return self.updatePLsStatus(CR_ID, PLs, 'Ready', VUs=VUs)

  def updatePLsStatus(self, CR_ID, PLs, status, VUs=None):
    if PLs:
      CR = self.getChangeRequestById(CR_ID)
      CR_PLs = CR['ProductLines']['ProductLineEntity']
      for pl in CR_PLs:
        if pl['ProductLineName'] in PLs:
          pl['Status'] = status
          if status == 'Ready':
            for VU in VUs:
              CR = self.addSoftwareUnitToCR(CR, pl['ProductLineName'], VU)
          PLs.remove(pl['ProductLineName'])
      return (self.saveChangeRequest(CR), PLs)
    else:
      return (0, PLs)

if __name__ == '__main__':
  prism = Prism('qctprismtst:8000', '/usr2/kdegi/prismauth')

  #print prism.CR_soapclient
  #print prism.search_soapclient

  CR = prism.getChangeRequestById('293155')
  print CR
  CR = prism.addPLtoCR(CR, 'MSM8660.LA.3.0', 'MSM8660')
  print CR

  #print prism.addGerritRefToCR('291900', 'MSM8660.LA.3.0', 'https://review-android.quicinc.com/31337')

  #print prism.movePLsToFixed('291900', ['MSM8660.LA.3.0'])

  print prism.addSoftwareUnitToCR(CR, 'MSM8660.LA.3.0', {'Name':'Test', 'Version':'Test1', 'Text':'Text for test1'})

  print prism.getCRsByGerritUrl('https://review-android.quicinc.com/60140', '10')

  print prism.getReleaseNotesStatusByCR('291900')
