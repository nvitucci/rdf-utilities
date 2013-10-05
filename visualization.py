#!/usr/bin/python

# treectrl.py

import wx, rdflib, sys
from rdflib import RDF, RDFS, OWL

class MyFrame(wx.Frame):
	def viewMode(self, item, g, mode):
		if mode == 'qname':
			try:
				return g.namespace_manager.compute_qname(item)[2]
			except:
				return '[' + item + ']'
		elif mode == 'norm':
				return g.namespace_manager.normalizeUri(item)
		else:
			return item

	def fillTree(self, tree, rootName, firstLevel, childrenMatrix, g, mode):
		new_lev = firstLevel
		new_ptrs = {}

		root = tree.AddRoot(self.viewMode(rootName, g, mode))

		for i in new_lev:
			new_ptrs[i] = tree.AppendItem(root, self.viewMode(i, g, mode))

		while len(new_lev) > 0:
			new_lev_temp = []
			for i in new_lev:
				new_sub = [x[0] for x in childrenMatrix if x[1] == i]
				for s in new_sub:
					new_ptrs[s] = tree.AppendItem(new_ptrs[i], self.viewMode(s, g, mode))
					new_lev_temp.append(s)

			new_lev = new_lev_temp

	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(800, 600))

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		vbox1 = wx.BoxSizer(wx.VERTICAL)
		vbox2 = wx.BoxSizer(wx.VERTICAL)
		vbox3 = wx.BoxSizer(wx.VERTICAL)
		panel1 = wx.Panel(self, -1)
		panel2 = wx.Panel(self, -1)
		panel3 = wx.Panel(self, -1)
		panelX = wx.Panel(self, -1)

		# This hides root
		# self.classTree = wx.TreeCtrl(panel1, 1, wx.DefaultPosition, (-1,-1), wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)

		# Do not hide root
		self.classTree = wx.TreeCtrl(panel1, 1, wx.DefaultPosition, (-1,-1), wx.TR_HAS_BUTTONS)
		self.objPropTree = wx.TreeCtrl(panel2, 1, wx.DefaultPosition, (-1,-1), wx.TR_HAS_BUTTONS)
		self.dataPropTree = wx.TreeCtrl(panel3, 1, wx.DefaultPosition, (-1,-1), wx.TR_HAS_BUTTONS)

		# ----------------------------
		
		g = rdflib.Graph()
		g.parse(file=open(sys.argv[1], 'r'), format='turtle')

		# Set of all classes
		classes = set()
		for t in g:
		    if t[2] == OWL['Class'] and not type(t[0]) == rdflib.BNode:
		        classes.add(t[0].toPython())

		# Set of all object properties
		objprops = set()
		for t in g:
		    if t[2] == OWL['ObjectProperty'] and not type(t[0]) == rdflib.BNode:
		        objprops.add(t[0].toPython())

		# Set of all datatype properties
		dataprops = set()
		for t in g:
		    if t[2] == OWL['DatatypeProperty'] and not type(t[0]) == rdflib.BNode:
		        dataprops.add(t[0].toPython())

		# List of pairs of (subclass, superclass)
		subclasses = []
		for t in g:
		    if t[1] == RDFS['subClassOf']:
		        subclasses.append((t[0].toPython(), t[2].toPython()))

		# List of pairs of (subproperty, superproperty)
		subprops = []
		for t in g:
		    if t[1] == RDFS['subPropertyOf']:
		        subprops.append((t[0].toPython(), t[2].toPython()))

		# Top classes (classes not having a superclass)
		new_lev_cl = classes.difference(set([x[0] for x in subclasses]))
		new_lev_op = objprops.difference(set([x[0] for x in subprops]))
		new_lev_dp = dataprops.difference(set([x[0] for x in subprops]))

		# Build the trees

		self.fillTree(self.classTree, OWL['Thing'], new_lev_cl, subclasses, g, 'qname')
		self.fillTree(self.objPropTree, OWL['topObjectProperty'], new_lev_op, subprops, g, 'qname')
		self.fillTree(self.dataPropTree, OWL['topDataProperty'], new_lev_dp, subprops, g, 'qname')		

		# ----------------------------

		self.classTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)
		self.display = wx.StaticText(panelX, -1, '',(10,10), style=wx.ALIGN_CENTRE)
		
		vbox1.Add(self.classTree, 1, wx.EXPAND)
		vbox2.Add(self.objPropTree, 1, wx.EXPAND)
		vbox3.Add(self.dataPropTree, 1, wx.EXPAND)
		hbox.Add(panel1, 1, wx.EXPAND)
		hbox.Add(panel2, 1, wx.EXPAND)
		hbox.Add(panel3, 1, wx.EXPAND)
		hbox.Add(panelX, 1, wx.EXPAND)
		panel1.SetSizer(vbox1)
		panel2.SetSizer(vbox2)
		panel3.SetSizer(vbox3)
		
		self.SetSizer(hbox)
		self.Centre()

	def OnSelChanged(self, event):
		item =  event.GetItem()
		self.display.SetLabel(self.classTree.GetItemText(item))

class MyApp(wx.App):
	def OnInit(self):
		frame = MyFrame(None, -1, 'treectrl.py')
		frame.Show(True)
		self.SetTopWindow(frame)
		return True

app = MyApp(0)
app.MainLoop()

