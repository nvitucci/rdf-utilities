import sys
import urllib2
import rdflib
from rdflib import RDF, OWL

endpoint = sys.argv[1]
graph = sys.argv[2]
output_name = sys.argv[3]
ontology_name = sys.argv[4]

output_file = output_name + '.nt'

# for Virtuoso: endpoint = 'http://localhost:8890/sparql?query='

useRDFlib = True

if useRDFlib:
	g = rdflib.Graph()
	ns = rdflib.Namespace(ontology_name + '/')
	g.add((rdflib.URIRef(ontology_name), RDF['type'], OWL['Ontology']))
else:
	f = open(output_file, 'w')
	f.write('<' + ontology_name + '>' + ' <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Ontology> .\n')

print 'SPARQL endpoint: ' + endpoint + ', graph: ' + graph + ', output file: ' + output_file

# q = 'CONSTRUCT {?p a owl:ObjectProperty} FROM ' + graph + ' WHERE {?s ?p ?o FILTER (!STRSTARTS(STR(?p), "http://www.w3.org/") && ISURI(?o))}'
# q = 'CONSTRUCT {?p a owl:ObjectProperty} FROM ' + graph + ' WHERE {?s ?p ?o FILTER (!STRSTARTS(STR(?p), "http://www.w3.org/") && ISURI(?o))} GROUP BY ?p'
q = 'CONSTRUCT {?p a owl:ObjectProperty} FROM ' + graph + ' WHERE {?s ?p ?o FILTER (ISURI(?o))} GROUP BY ?p'

req = urllib2.Request(endpoint + urllib2.quote(q))
req.add_header('Accept', 'text/plain')
print q 
# print req.get_full_url()
res = urllib2.urlopen(req)
r = ''.join(res.readlines())
if useRDFlib:
	g.parse(data=r, format='nt')
else:
	if not r.find('Empty'):
		f.write(r)

# q = 'CONSTRUCT {?p a owl:DatatypeProperty} FROM ' + graph + ' WHERE {?s ?p ?o FILTER (!STRSTARTS(STR(?p), "http://www.w3.org/") && ISLITERAL(?o))}'
# q = 'CONSTRUCT {?p a owl:DatatypeProperty} FROM ' + graph + ' WHERE {?s ?p ?o FILTER (!STRSTARTS(STR(?p), "http://www.w3.org/") && ISLITERAL(?o))} GROUP BY ?p'
q = 'CONSTRUCT {?p a owl:DatatypeProperty} FROM ' + graph + ' WHERE {?s ?p ?o FILTER (ISLITERAL(?o))} GROUP BY ?p'
req = urllib2.Request(endpoint + urllib2.quote(q))
req.add_header('Accept', 'text/plain')
print q 
res = urllib2.urlopen(req)
r2 = ''.join(res.readlines())
if useRDFlib:
	g.parse(data=r2, format='nt')
else:
	if not r2.find('Empty'):
		f.write(r2)

q = 'CONSTRUCT {?c a rdfs:Class} FROM ' + graph + ' WHERE {?s a ?c}'
req = urllib2.Request(endpoint + urllib2.quote(q))
req.add_header('Accept', 'text/plain')
print q 
res = urllib2.urlopen(req)
r3 = ''.join(res.readlines())
if useRDFlib:
	g.parse(data=r3, format='nt')
else:
	if not r3.find('Empty'):
		f.write(r3)

if useRDFlib:
	g.commit()

	rdf_file = open(output_file, 'w')
	rdf_file.write(g.serialize(format='nt'))
	# rdf_file.write(g.serialize(format='n3'))
	# rdf_file.write(g.serialize(format='turtle'))

	rdf_file.close()
	g.close()
else:
	f.close()
