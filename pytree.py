#! /usr/bin/env python3

import os
from os import listdir, sep
from os.path import abspath, basename, isdir, expanduser
from sys import argv

from binaryornot.check import is_binary

import json

# needs to take in exclusion (node_modules for instance)

# GitHub does - folders in alphabetical
# Then, files in alphabetical
# how about, files first, then folder

# hmm what if you convert it into JSON, then create
# a React app to display it?
# that's why you want it in this form

# crunch algo?
# ah yes it makes counts weird

# ignorefile

# has ext list
# config['ext'] = ['asm', ...]
config = {}

def loadConfig():
    homeDirPath = expanduser('~')
    configPath = homeDirPath + sep + '.pytree/config.json'
    configFile = open(configPath, 'r')
    jdec = json.JSONDecoder()
    s = configFile.read()
    configFile.close()
    doc = jdec.decode(s)
    config['ext'] = doc['ext']
    config['includeFiles'] = doc['includeFiles']
    config['excludeFolders'] = doc['excludeFolders']

class File(object):
    def __init__(self):
        self.lineCount = 0
        self.name = ''

class Folder(object):
    def __init__(self):
        self.lisFiles = []
        self.lisFolders = []
        self.name = ''
        # these are then generated
        self.totalLineCount = 0
        self.totalFileCount = 0
        # immediate can be easily generated

def createTree():
    # right now, not read any OS stuff
    n1 = File()
    n1.name = 'Bat.java'
    n1.lineCount = 100
    n2=Folder()
    n2.name='src'
    n2.lisFiles.append(n1)
    n2.totalLineCount=100
    n2.totalFileCount=1
    n3=Folder()
    n3.name='bar'
    n3.lisFolders.append(n2)
    n3.totalLineCount=100
    n3.totalFileCount=1
    n4=File()
    n4.name='baz.txt'
    n4.lineCount=100
    n5=File()
    n5.name='zaz.txt'
    n5.lineCount=100
    n6=Folder()
    n6.name='foo'
    n6.lisFolders.append(n3)
    n6.totalLineCount=300
    n6.totalFileCount=3
    n6.lisFiles.append(n4)
    n6.lisFiles.append(n5)
    return n6

def crunchTree(node):
    # base case: File, or no more
    if len(node.lisFiles) == 0 and len(node.lisFolders) == 0:
        return
    # src/main/java kind of thing
    while len(node.lisFiles) == 0 and len(node.lisFolders) == 1:
        # crunch
        tmp = node.lisFolders[0]
        node.name += '/' + tmp.name # change upper name
        node.lisFolders = tmp.lisFolders # eat bottom
        node.lisFiles = tmp.lisFiles
    # recurse
    for f in node.lisFolders:
        crunchTree(f)

def totalLines(node):
    # that is, do total lines
    # this will always be a folder
    tl = 0
    for f in node.lisFiles:
        tl += f.lineCount
    for fol in node.lisFolders:
        tl += totalLines(fol)
    # then set
    node.totalLineCount = tl
    return tl

def totalFiles(node):
    # then, total files
    tf = 0
    tf += len(node.lisFiles)
    for fol in node.lisFolders:
        tf += totalFiles(fol)
    node.totalFileCount = tf
    return tf

# can do: sort by count, sort alphabetically
def printTreeRec(node, indent, kind='alpha'):
    # this itself has to be a folder
    ifcount = str(len(node.lisFiles))
    print(' ' * indent + '('+node.name+') ('+str(node.totalFileCount)+'TF, '+ifcount+'IF, ' + str(node.totalLineCount) + 'TL)')
    # do immediate files first
    # sort here
    if kind=='alpha':
        for f in sorted(node.lisFiles, key=lambda x: x.name):
            print(' ' * (indent+4) + '[' + str(f.lineCount) + '] ' + f.name)
    else:
        for f in sorted(node.lisFiles, key=lambda x: -x.lineCount):
            print(' ' * (indent+4) + '[' + str(f.lineCount) + '] ' + f.name)
    # then folders
    for f in sorted(node.lisFolders, key=lambda x: x.name):
        printTreeRec(f, indent + 4, kind=kind)

def printTree(node):
    printTreeRec(node, 0)

def lineCount(path):
    i = -1
    with open(path) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def getExt(fname):
    if '.' in fname:
        return fname.split('.')[1]
    else:
        return None

# so we will be appending to this directory name
di = '.'
def createTree2(di):
    n = Folder()
    n.name = basename(abspath(di))
    lisFiles = []
    lisFolders = []
    # using similar views as before
    # using those procedures
    dirItems = listdir(di)
    dirItems = filter(lambda x : x[0] != '.', dirItems)
    for i in dirItems:
        currPath = di + sep + i
        ext = getExt(i)
        goodExt = ext is not None and ext in config['ext']
        if not isdir(currPath) and ((i in config['includeFiles']) or goodExt or (goodExt and not is_binary(currPath))): # this is a file, is it binary or not?
            f = File()
            f.name = i
            f.lineCount = lineCount(currPath)
            lisFiles.append(f)
        elif isdir(currPath) and i not in config['excludeFolders']: # this is a folder
            fol = createTree2(currPath)
            lisFolders.append(fol)
        else:
            continue
    n.lisFiles = lisFiles
    n.lisFolders = lisFolders
    return n

def everything(di, kind='lc'):
    loadConfig()
    a = createTree2(di)
    crunchTree(a)
    totalLines(a)
    totalFiles(a)
    printTreeRec(a, 0, kind=kind)

helpMsg = """pytree
  pytree help
  pytree . alpha
  pytree .
  pytree config
  pytree . --save
  pytree . --save myfolder
  pytree view myfolder
  pytree list
"""

def main():
    if len(argv) == 1:
        everything('.')
    elif len(argv) == 2:
        # print just directories
        path = argv[1]
        if path == 'config':
            # open editor
            os.system('vim ~/.pytree/config.json')
        elif path == 'help':
            print(helpMsg)
        elif isdir(path):
            everything(path)
        else:
            print('ERROR: \'' + path + '\' is not a directory')
    elif len(argv) == 3:
        path = argv[1]
        if isdir(path):
            everything(path, 'alpha')
        else:
            print('ERROR')
    else:
        # add alphabetical
        print('pyTree')

if __name__ == '__main__':
    main()

