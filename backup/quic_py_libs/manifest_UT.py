from manifest_repr import GitServerProjectBranch, Manifest

b1 = GitServerProjectBranch(project='platform/manifest', branch='gingerbread_house')
b2 = GitServerProjectBranch(server='review.quicinc.com', project='platform/manifest', branch='honeycomb_mr2_release')
b3 = GitServerProjectBranch(textual_representation='review.quicinc.com/platform/manifest:honeycomb_mr2')
b4 = GitServerProjectBranch(textual_representation='review.quicinc.com/platform/manifest:honeycomb_mr2_release')

print b1
print b2
print b3
print b4

print b1.generateURL()
print b1.generateURL(port='29418')
print b2.generateURL(protocol='ssh', user='gohulanb', port='29418')
print b3.generateURL(protocol='ssh', user='gohulanb')
print b4.generateURL(protocol='ssh')
print b4.generateURL(protocol='ftp')

#exercise GitServerProjectBranch.__eq__
if (b2 == b4):
  print 'b2 and b4 are equal'

s = set([])
s.add(b2)
s.add(b1)
s.add(b3)
s.add(b4)

print 'unsorted: %s' % s
#exercise GitServerProjectBranch.__cmp__
print 'sorted: %s' % sorted(s)

#exercise GitServerProjectBranch.__hash__
h = {b1:'', b2:'', b3:'', b4:''}
print h

print

m1 = Manifest(branch='gingerbread_house')
m2 = Manifest(textual_representation='review.quicinc.com/platform/manifest:honeycomb_mr2:default.xml')
m3 = Manifest(textual_representation='review.quicinc.com/platform/manifest:honeycomb_mr2')
m4 = Manifest(server='git.quicinc.com', project = 'platform/manifest', branch='gingerbread_house', path='default.xml')

print m1
print m2
print m3
print m4

#exercise Manifest.__eq__
if (m1 == m4):
  print 'm1 and m4 are equal'

r = set([])
r.add(m2)
r.add(m1)
r.add(m4)
r.add(m3)

print 'unsorted: %s' % r
#exercise Manifest.__cmp__
print 'sorted: %s' % sorted(r)

#exercise Manifest.__hash__
e = {m1:'', m2:'', m3:'', m4:''}
print e