#!/usr/bin/python

# treectrl.py

import wx, rdflib, sys
import wx.xrc as xrc
from rdflib import RDF, RDFS, OWL

class MyApp(wx.App):
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

	def OnInit(self):
		xrcfile = 'gui.xrc'
		self.xrc = xrc.XmlResource(xrcfile)

		self.frame = self.xrc.LoadFrame(None, "MainFrame")
		self.frame.Maximize()

		self.classTree = xrc.XRCCTRL(self.frame, "classTree")
		self.objPropTree = xrc.XRCCTRL(self.frame, "objPropTree")
		self.dataPropTree = xrc.XRCCTRL(self.frame, "dataPropTree")

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

		self.display = xrc.XRCCTRL(self.frame, "status")
		
		# wx.EVT_TREE_SEL_CHANGED(self.classTree, self.classTree.GetId(), self.OnSelChanged)
		self.frame.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=xrc.XRCID("classTree"))
		
		self.frame.Centre()
		self.frame.Show(1)

		return True

	def OnSelChanged(self, event):
		item = event.GetItem()
		self.display.SetLabel(self.classTree.GetItemText(item))

if __name__ == '__main__':
	app = MyApp(0)
	app.MainLoop()

