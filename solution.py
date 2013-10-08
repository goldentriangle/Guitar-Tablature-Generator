'''
Guitar Tablature Generator
By Kai
'''

import os
import sys
import json
import math
import unicodedata
from time import time

inputfile= 'chords.json'
notedict={'A':0, 'A#':1, 'Bb':1, 'B':2, 'Cb':2, 'B#':3,'C':3, 'C#':4, 'Db':4, 'D':5, 'D#':6, 'Eb':6, 'E':7, 'Fb':7, 'E#':8,'F':8, 'F#':9, 'Gb':9, 'G':10, 'G#':11, 'Ab':11}
basenote={1:'E', 2:'B', 3:'G', 4:'D', 5:'A', 6:'E'} #string numbering from 1 to 6
basenotecode={}
nstring= 6
nfret= 24       #inclusive
fret_range=6    #inclusive

assignstr=[]
notecode=[]

stop= False
'''
uncomment to get more friendly output
and comment #1 and #2
'''
def outputTab(f, name, tablature):
    f.write('Chord: %s \n'%(name))
    #f.write('note to string assignment: %s \n'%(' '.join(assignstr)))
    i= nstring-1
    while i>=0:
        if tablature[i]=='X':
            f.write('%s ---X---\n'%( basenote[i+1]))#1
            #f.write('%s ---X---%s\n'%( basenote[i+1], assignstr[i]))
        else:
            f.write('%s ---%s---\n'%( basenote[i+1], tablature[i]))#2
            #f.write('%s ---%s---%s\n'%( basenote[i+1], tablature[i],assignstr[i] ))
        i=i-1
    f.write('\n')

    
def getFret(notecode, stringNo):
    frets=[]
    t= notecode- notedict[basenote[stringNo]]
    if t<0:
        t=t+12
    frets.append(t)
    if(t+12<= nfret):
        t=t+12
        frets.append(t)
        if(t+12<= nfret):
           t=t+12
           frets.append(t)
    return frets

'''
scan from fret 0 to fret 23
return valid result that is within 6 fret
'''
def scanFrets(assign, name, notes, fout):
    global stop
    distinctTab= {}
    '''for j in range(nstring):
            frets= getFret(notecode[assign[j]], j+1)
            print j, notes[assign[j]-1], frets
    print '------------------'
    stop= True
    return'''
    for i in range(nfret-fret_range):
        tablature=[]
        tabnoX=[]
        valid= True
        # check if the note on each string is within the range
        for j in range(nstring):
            if assign[j]==0:
                validfret= 'X'
                tablature.append(validfret)
                continue
            
            frets= getFret(notecode[assign[j]], j+1)
            validfret= -1
            for item in frets:
                #within range
                if item <= i+ fret_range:
                    validfret= item
            
            if validfret== -1:
                valid = False
                break
            else:
                tablature.append(validfret)
                tabnoX.append(validfret)
        
        if valid== True:
            tmp= [str(item) for item in tablature]
            tmp= ','.join(tmp)
            if distinctTab.has_key(tmp)== False:
                distinctTab[tmp]= True
                #print tmp
                #outputTab(f, name, tablature)
                #print f, name, tablature
                if (max(tabnoX)-min(tabnoX))<= fret_range:
                    outputTab(fout, name, tablature)


'''
return a mapping from note to string
'''
def convert2baseN(num, base):
    result=[]
    flag={}
    #key is the notecode, value indidates whether it's assigned to a string. mark 1 to base-1
    for i in range(base):
        if i==0:
            continue
        flag[i]= False

    for i in range(nstring):
        result.insert(0, num% base)
        num= num/base
        if flag.has_key(result[0])==True:
            del flag[result[0]]
    
    #print num, result
    #return the assignment if and only if every note has been assigned to a string, otherwise return None 
    if len(flag)==0:
        return result
    else:
        return None

    
def tabGenerator(name, notes, fout):
    global assignstr
    global notecode
    
    n= len(notes)
    if n> nstring:
        print 'error: number of notes exceeds 6!'
        sys.exit(1)
    notecode=[-1]+[notedict[note] for note in notes]
    print notecode
    #consider all assignment of a note to a string as a base n+1 number. when assign 0 to a string, the string is not played
    #alphabetic set is {0, 1, ... n}
    maxBaseNstring= int(math.pow(n+1,nstring))
    for i in range(maxBaseNstring):
        assign= convert2baseN(i, n+1)
        if assign is None:
            continue
        else:
            assignstr=[]
            for j, item in enumerate(assign):
                if item==0:
                    assignstr.append( 'X')
                else:
                    assignstr.append( notes[item-1])
            #print 'assign is: %s'%(','.join(assignstr))   # from high to low
            scanFrets(assign, name, notes, fout)
            if stop== True:
                return
    
     
def driver(fname):
    fout= open('results.txt', 'w')
    for i in range(nstring):
        basenotecode[i+1]= notedict[basenote[i+1]]
    print basenotecode
    f=open(fname)
    data= json.load(f)
    f.close()
    size= len(data)

    #print size
    for i, item in enumerate(data):
        notes= [ unicodedata.normalize('NFD',note.strip()).encode('ascii', 'ignore')  for note in data[i][u'Notes'].split(',')]
        name= unicodedata.normalize('NFD',data[i][u'Name'].strip()).encode('ascii', 'ignore')
        print i, name, notes
        tabGenerator(name, notes, fout)
    fout.close()


if __name__=='__main__':
    driver(inputfile)
    #convert2baseN( 170, 6)
