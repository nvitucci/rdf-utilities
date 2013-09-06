import rdflib
import sys, getopt

def usage():
	print sys.argv[0] + ' -d <data_file> -o <ont_file> '

def get_format(filename):
	ext = filename.split('.')[1]

	if ext == 'nt':
		return 'nt'
	elif ext == 'n3':
		return 'n3'
	elif ext == 'ttl':
		return 'turtle'

# data_in_format = 'turtle'
# ont_in_format = 'turtle'
# out_format = 'nt'

# data_file = open(sys.argv[1], 'r')
# ont_file = open(sys.argv[2], 'r')
# comb_file = open(sys.argv[1].split('.')[0] + '_comb.' + out_format, 'w')

data_files = []
ont_files = []
comb_files = []

try:
	opts, args = getopt.getopt(sys.argv[1:], "hd:o:c:", ["data_file=", "ont_file=", "comb_file="])
except getopt.GetoptError:
	usage()
	sys.exit(2)

for opt, arg in opts:
	if opt == '-h':
		usage()
		sys.exit()
	elif opt in ("-d", "--data_file"):
		data_files.append(arg)
	elif opt in ("-o", "--ont_file"):
		ont_files.append(arg)
	elif opt in ("-c", "--comb_file"):
		comb_files.append(arg)

print 'Data files: ', data_files
print 'Ontology files: ', ont_files
print 'Combined files: ', comb_files

g = rdflib.Graph()

for d in data_files:
	form = get_format(d)
	print 'File: ' + d + ', format: ' + form
	
	data_file = open(d, 'r')
	g.parse(file=data_file, format=form)
	data_file.close()

for o in ont_files:
	form = get_format(o)
	print 'File: ' + o + ', format: ' + form
	
	ont_file = open(o, 'r')
	g.parse(file=ont_file, format=form)
	ont_file.close()

for c in comb_files:
	form = get_format(c)
	print 'File: ' + c + ', format: ' + form
	
	comb_file = open(c, 'w')
	comb_file.write(g.serialize(format=form))
	comb_file.close()

