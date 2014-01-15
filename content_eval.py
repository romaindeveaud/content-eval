#!/usr/bin/python

from lxml import etree
from nltk import word_tokenize
from optparse import OptionParser
from collections import defaultdict
from trec import TrecRun,TrecRetDoc
from utils import *

import operator

#class Document:
#
#  def __init__(self,string):
#    self.p = dict()
#    for word in word_tokenize(string)


def load_ref(ref_file):
  f = open(ref_file)
  s = f.read()
  f.close()

  parser = etree.XMLParser(recover=True)
  root = etree.fromstring(s,parser)

  return root

def rel_docs(qrels_file):
  results = defaultdict(list)
  for line in open(qrels_file):
    l = line.split()
    if int(l[3]) > 0:
      results[int(l[0])].append(l[2]) 
  
  return results

def compute_lm(docs):
  text = ' '.join([get_doc_by_id(ref,d) for d in docs])

  freq = defaultdict(int)
  words = word_tokenize(text.lower())
  for w in words: 
    if not (w in english_stopwords or len(w) <= 2):
      freq[w] += 1

  return dict((w,float(freq[w])/len(words)) for w in freq)
   

def get_doc_by_id(ref,id):
  return ref.findtext("document[@id='"+id+"']").strip()


def main():
  parser = OptionParser()
  parser.add_option("-r", "--run", dest="run",
                  help="Path to the run file", metavar="FILE")
  parser.add_option("-q", "--qrels",
                  dest="qrels", help="Path to the qrels file", metavar="FILE")
  parser.add_option("-t", "--text",
                  dest="text", help="Path to the textual reference file (outputs of test_collection_to_text.rb)", metavar="FILE")

  (options, args) = parser.parse_args()

  mandatories = ['run','qrels','text']
  for m in mandatories:
    if not options.__dict__[m]:
      print "mandatory option is missing\n"
      parser.print_help()
      exit(-1)

  return options


if __name__ == "__main__":
  options = main()

  ref        = load_ref(options.text)
  hash_qrels = rel_docs(options.qrels)
  trec_run   = TrecRun(options.run,100)

  for topic,trecretdocs in trec_run.items():
    docs = [r.doc for r in trecretdocs]
    docs_text = compute_lm(docs[:1])
    ref_text  = compute_lm(hash_qrels[topic])

    estimate_docs = sorted(docs_text.iteritems(), key=operator.itemgetter(1),reverse=True)[:100]
    estimate_ref = sorted(ref_text.iteritems(), key=operator.itemgetter(1),reverse=True)[:100]

    voc_docs = unique([t[0] for t in estimate_docs])
    voc_ref  = unique([t[0] for t in estimate_ref])

    set(voc_docs).

    break
