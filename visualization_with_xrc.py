#!/usr/bin/python

# treectrl.py

import wx, rdflib, sys
import wx.xrc as xrc
from rdflib import RDF, RDFS, OWL

class MyApp(wx.App):
	def updateObjProp(self, ch):
		for p in self.objPropBoxes.values():
			p.SetValue(False)
		
		for c in ch:
			self.objPropBoxes[c].SetValue(True)
		
	def updateDataProp(self, ch):
		for p in self.dataPropBoxes.values():
			p.SetValue(False)

		for c in ch:
			self.dataPropBoxes[c].SetValue(True)
		
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
			new_ptrs[i] = tree.AppendItem(root, self.viewMode(i, g, mode), data=wx.TreeItemData(i))

		while len(new_lev) > 0:
			new_lev_temp = []
			for i in new_lev:
				new_sub = [x[0] for x in childrenMatrix if x[1] == i]
				for s in new_sub:
					new_ptrs[s] = tree.AppendItem(new_ptrs[i], self.viewMode(s, g, mode), data=wx.TreeItemData(s))
					new_lev_temp.append(s)

			new_lev = new_lev_temp

	def OnInit(self):
		self.chars = [
			OWL['FunctionalProperty'], 
			OWL['InverseFunctionalProperty'], 
			OWL['TransitiveProperty'], 
			OWL['SymmetricProperty'], 
			OWL['AsymmetricProperty'], 
			OWL['ReflexiveProperty'], 
			OWL['IrreflexiveProperty']]
		
		xrcfile = 'gui.xrc'
		self.xrc = xrc.XmlResource(xrcfile)

		self.frame = self.xrc.LoadFrame(None, "MainFrame")
		self.frame.Maximize()

		self.classTree = xrc.XRCCTRL(self.frame, "classTree")
		self.objPropTree = xrc.XRCCTRL(self.frame, "objPropTree")
		self.dataPropTree = xrc.XRCCTRL(self.frame, "dataPropTree")

		self.objPropBoxes = {}
		self.objPropBoxes[self.chars[0]] = xrc.XRCCTRL(self.frame, "funcProp")
		self.objPropBoxes[self.chars[1]] = xrc.XRCCTRL(self.frame, "invFuncProp")
		self.objPropBoxes[self.chars[2]] = xrc.XRCCTRL(self.frame, "transProp")
		self.objPropBoxes[self.chars[3]] = xrc.XRCCTRL(self.frame, "symProp")
		self.objPropBoxes[self.chars[4]] = xrc.XRCCTRL(self.frame, "asymProp")
		self.objPropBoxes[self.chars[5]] = xrc.XRCCTRL(self.frame, "refProp")
		self.objPropBoxes[self.chars[6]] = xrc.XRCCTRL(self.frame, "irrefProp")

		self.dataPropBoxes = {}
		self.dataPropBoxes[self.chars[0]] = xrc.XRCCTRL(self.frame, "dataFuncProp")

		# ----------------------------
		
		g = rdflib.Graph()
		g.parse(file=open(sys.argv[1], 'r'), format='turtle')

		# Set of all classes
		classes = set()
		for t in g:
		    if t[2] == OWL['Class'] and not type(t[0]) == rdflib.BNode:
		        classes.add(t[0])

		# Set of all object properties
		objprops = set()
		for t in g:
			if t[2] == OWL['ObjectProperty'] and not type(t[0]) == rdflib.BNode:
				objprops.add(t[0])

		# Set of all datatype properties
		dataprops = set()
		for t in g:
			if t[2] == OWL['DatatypeProperty'] and not type(t[0]) == rdflib.BNode:
				dataprops.add(t[0])

		# List of pairs of (subclass, superclass)
		subclasses = []
		for t in g:
			if t[1] == RDFS['subClassOf']:
				subclasses.append((t[0], t[2]))

		# List of pairs of (subproperty, superproperty)
		subprops = []
		for t in g:
			if t[1] == RDFS['subPropertyOf']:
				subprops.append((t[0], t[2]))

		# Characteristics of each property
		self.prop_chars = []

		for t in g:                     
			if (t[0] in objprops or t[0] in dataprops) and t[1] == RDF['type'] and t[2] in self.chars:
				self.prop_chars.append((t[0], t[2]))

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
		self.frame.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelPropChanged, id=xrc.XRCID("objPropTree"))
		self.frame.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelDataPropChanged, id=xrc.XRCID("dataPropTree"))
		
		self.frame.Centre()
		self.frame.Show(1)

		return True

	def OnSelPropChanged(self, event):
		item = self.objPropTree.GetPyData(event.GetItem())
		chars = [x[1] for x in self.prop_chars if x[0] == item]

		self.updateObjProp(chars)

	def OnSelDataPropChanged(self, event):
		item = self.dataPropTree.GetPyData(event.GetItem())
		chars = [x[1] for x in self.prop_chars if x[0] == item]

		self.updateDataProp(chars)

	def OnSelChanged(self, event):
		item = event.GetItem()
		self.display.SetLabel(self.classTree.GetItemText(item))

if __name__ == '__main__':
	app = MyApp(0)
	app.MainLoop()

