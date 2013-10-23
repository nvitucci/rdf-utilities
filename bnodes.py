import rdflib
from rdflib import RDF, RDFS, OWL

def printRecursive(l):
    for i in l:
        if type(i) == list:
            print '[' + str(printRecursive(i)) + ']',
        else:
            # print g.namespace_manager.normalizeUri(i),
            print type(i),

def isListNode(n, bnodes):                                                                                                
    return type(n) == rdflib.BNode and len(bnodes[n]) == 2 and bnodes[n][0][0] in [RDF['first'], RDF['rest']] and bnodes[n][1][0] in [RDF['first'], RDF['rest']]

def isClassNode(n, bnodes):                                                                                                
    return type(n) == rdflib.BNode and len(bnodes[n]) == 2 and bnodes[n][0][0] == RDF['type'] and bnodes[n][1][0] in [OWL['unionOf'], OWL['intersectionOf']]

def getFirstRest(n, bnodes):
    if isListNode(n, bnodes):
        first = [p[1] for p in bnodes[n] if p[0] == RDF['first']][0]
        rest = [p[1] for p in bnodes[n] if len(p) == 2 and p[0] == RDF['rest']][0]

        return first, rest
    else:
        return None

def loopNode(n, bnodes):
    bn_chains = []
    if isListNode(n, bnodes):
        first, rest = getFirstRest(n, bnodes)
        if isListNode(first, bnodes): 
            first = loopNode(first, bnodes)
        elif isClassNode(first, bnodes):
            un_or_in = [p[1] for p in bnodes[first] if p[0] in [OWL['unionOf'], OWL['intersectionOf']]][0]
            first = loopNode(un_or_in, bnodes)

        bn_chains.append(first)

        while rest != RDF['nil']:
            first, rest = getFirstRest(rest, bnodes)
            # print 'Rest $$$ ' + first + ', ' + str(isListNode(first, bnodes)) + ', ' + str(isClassNode(first, bnodes)) + ', ' + str(type(first))
            if isListNode(first, bnodes):
                first = loopNode(first, bnodes)
            elif isClassNode(first, bnodes):
                un_or_in = [p[1] for p in bnodes[first] if p[0] in [OWL['unionOf'], OWL['intersectionOf']]][0]
                first = loopNode(un_or_in, bnodes)
            
            bn_chains.append(first)
        
        return bn_chains
    else:
        return None

g = rdflib.Graph()
g.parse(file=open('/home/nick/tmp/question.ttl', 'r'), format='turtle')

# Map of "list" BNodes
list_bnodes = {}

for t in g:                                                                        
    if type(t[0]) == rdflib.BNode:
        if t[1] in [RDF['first'], RDF['rest']]:
            if t[0] not in list_bnodes.keys(): 
                list_bnodes[t[0]] = [(t[1], t[2])]
            else: 
                list_bnodes[t[0]].append((t[1], t[2]))

# Map of all BNodes
bnodes = {}

for t in g:                                                                   
    if type(t[0]) == rdflib.BNode:
        if t[0] in bnodes.keys(): 
            bnodes[t[0]].append((t[1], t[2]))
        else: 
            bnodes[t[0]] = [(t[1], t[2])]

for k, n in bnodes.iteritems():
    # if isListNode(k, bnodes):
        for t in n:
            print k + ' ### ' + str([g.namespace_manager.normalizeUri(t[0]), g.namespace_manager.normalizeUri(t[1])])

print '\nBNodes:\n'

# Loop over "list" BNodes checking also all BNodes
for n in list_bnodes: 
    l = loopNode(n, bnodes)
    if l != None:
        # print l
        printRecursive(l)
        print '\n'
