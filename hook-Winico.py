import os

from PyInstaller.build import Tree
from PyInstaller.hooks.hookutils import exec_statement

def hook(mod):
	tclroot = exec_statement('from Tkinter import Tcl; t = Tcl(); print(t.eval("info library"))')
	
	winicodir = os.path.join('_MEI', 'winico')
	winicoroot = os.path.join(os.path.dirname(tclroot), 'winico0.6')
	
	winicotree = Tree(winicoroot, winicodir, excludes=['demo.tcl', 'sample.tcl', 'sample2.tcl', '*.css', '*.html', '*.ico'])
	
	mod.pyinstaller_datas.extend(winicotree)
	
	return mod
