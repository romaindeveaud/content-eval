#!/usr/bin/python

import sys
import time
import math
import argparse
import glob
import subprocess
import re

import lxml.html
from lxml.html.clean import Cleaner
from optparse import OptionParser

from progressbar import Bar, Counter, AdaptiveETA, Percentage, ProgressBar
from trec import *
from utils import *

 
# width defines bar width
# percent defines current percentage
def progress(width, percent):
    marks = math.floor(width * (percent / 100.0))
    spaces = math.floor(width - marks)
     
    loader = '[' + ('=' * int(marks)) + (' ' * int(spaces)) + ']'
       
    sys.stdout.write("%s %d%%\r" % (loader, percent))
    if percent >= 100:
        sys.stdout.write("\n")
    sys.stdout.flush()



def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--coll", dest="coll",
                  help="Path to an Indri index of the collection", metavar="FOLDER")
  parser.add_argument("-q", "--qrels",
                  dest="qrels", help="Path to the qrels file", metavar="FILE")
  parser.add_argument("-r", "--run_folders",
                  dest="folders", help="Folders where TREC runs are stored", metavar="FOLDERS",nargs='*')
  parser.add_argument("-o", "--out",
                  dest="out", help="Path to the output file", metavar="FILE")

  options = vars(parser.parse_args())

  mandatories = ['coll','qrels','folders','out']
  for m in mandatories:
    if options[m] == None:
      print "mandatory option is missing\n"
      parser.print_help()
      exit(-1)

  return options



if __name__ == "__main__":
  options = main()

  print("Parsing all runs from ("+ ', '.join(options['folders']) +"), collection index: "+options['coll'])

  documents = unique(get_docs_from_qrels(options['qrels']))
  print("qrels done ("+str(len(documents))+" documents).")

  for folder in options['folders']:
    for file in glob.glob(folder+'/*'):
      documents += get_docs_from_run(file,100)

  documents = unique(documents)

  print("Runs parsed ! "+ str(len(documents)) + " documents.")
  print("Now fetching text...")

  output = open(options['out'],'w')

  output.write("<?xml version='1.0' encoding='UTF-8' standalone='no' ?>\n")
  output.write("<documents>\n")

  widgets = ["Finished ", Counter(), " documents so far. ",
              Bar(), ' ',
              Percentage(), ' ',
              AdaptiveETA()]
  pbar = ProgressBar(widgets=widgets, maxval=len(documents))
  pbar.start()

  i = 0
  for d in documents:
    indri_id = subprocess.Popen(["dumpindex", options['coll'], "di" ,"docno", d],stdout=subprocess.PIPE).communicate()[0].strip()
    doc      = subprocess.Popen(["dumpindex", options['coll'], "dt", indri_id],stdout=subprocess.PIPE).communicate()[0].strip()

    output.write("<document id=\""+d+"\">")

    cleaner = Cleaner(kill_tags=['script','SCRIPT','style'],page_structure=False)
    text = lxml.html.document_fromstring(cleaner.clean_html(doc))
    output.write(re.sub(' +', ' ', re.sub(r"[\n\r\t\W]",' ',text.text_content()))+"\n")

    output.write("</document>\n")
#progress(50, (i + 1)/len(documents)) 
    i+=1
    pbar.update(i)

  pbar.finish()

  output.write("</documents>")

  print("Done !")
