import rdflib
import sys

data_in_format = 'turtle'
ont_in_format = 'turtle'
out_format = 'nt'

data_file = open(sys.argv[1], 'r')
ont_file = open(sys.argv[2], 'r')
comb_file = open(sys.argv[1].split('.')[0] + '_comb.' + out_format, 'w')

g = rdflib.Graph()

g.parse(file=data_file, format=data_in_format)
g.parse(file=ont_file, format=ont_in_format)

comb_file.write(g.serialize(format=out_format))

data_file.close()
ont_file.close()
comb_file.close()
