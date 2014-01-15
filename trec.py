#!/usr/bin/python

import sys
import gc

class TrecRetDoc:

  def __init__(self,line):
    t = line.split()
    self.topic = int(t[0])
    self.doc   = t[2]
    self.rank  = int(t[3])
    self.score = float(t[4])
    self.run   = t[5]

class TrecRun(dict):

  def __init__(self,path,limit=1000):
    for line in open(path):
      t = TrecRetDoc(line.strip())    
      if t.rank > limit:
        continue
      if t.topic not in self:
        self[t.topic] = [] 
      self[t.topic].append(t)



def get_docs_from_run(run_file,limit=1000):
  documents = []
  for line in open(run_file):
    try:
      l = line.split()
      rank = int(l[3])
      if rank > limit:
        continue
      doc  = l[2]

      gc.disable()
      documents.append(doc) 
      gc.enable()
    except:
      print("TREC result error in file "+run_file)

  return documents

def get_docs_from_qrels(qrels_file):
  results = []
  for line in open(qrels_file):
    l = line.split()
    if int(l[3]) > 0:
      results.append(l[2]) 
  
  return results
