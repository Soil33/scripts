l1 = ['name1']
l2 = ['name2', 'sname2']
t = l2
s = "%s-%s"%(t[0], t[1][1:4]) if len(t) > 1 else "%s-NONE"%t[0]
print (s)