#!/usr/bin/python
"""Copyright (C) 2014 Romain Deveaud <romain.deveaud@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


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

 
def progress(width, percent):
    """
    `width` defines the width of the progressbar
    `percent` defines the current progress percentage 
    """
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

  # get a list of docnos from the qrel file.
  documents = unique(get_docs_from_qrels(options['qrels']))

  print("qrels done ("+str(len(documents))+" documents).")

  # get the list of all docnos for all the TREC runs contained in the
  # supplied directory.
  for folder in options['folders']:
    for file in glob.glob(folder+'/*'):
      documents += get_docs_from_run(file,100)

  # only keep the unique docnos.
  documents = unique(documents)

  print("Runs parsed ! "+ str(len(documents)) + " documents.")
  print("Now fetching text...")


  # create the output XML file that will contain the text of all the documents
  # identified by the docnos in `documents`.
  output = open(options['out'],'w')

  output.write("<?xml version='1.0' encoding='UTF-8' standalone='no' ?>\n")
  output.write("<documents>\n")

  # initialisation of the progressbar.
  widgets = ["Finished ", Counter(), " documents so far. ",
              Bar(), ' ',
              Percentage(), ' ',
              AdaptiveETA()]
  pbar = ProgressBar(widgets=widgets, maxval=len(documents))
  pbar.start()

  i = 0
  for d in documents:
    # get the internal Indri id associated with the current docno `d`, and
    # get the text of this document.
    indri_id = subprocess.Popen(["dumpindex", options['coll'], "di" ,"docno", d],stdout=subprocess.PIPE).communicate()[0].strip()
    doc      = subprocess.Popen(["dumpindex", options['coll'], "dt", indri_id],stdout=subprocess.PIPE).communicate()[0].strip()

    output.write("<document id=\""+d+"\">")

    # remove the HTML from the text, then write in the XML file.
    cleaner = Cleaner(kill_tags=['script','SCRIPT','style'],page_structure=False)
    text = lxml.html.document_fromstring(cleaner.clean_html(doc))
    output.write(re.sub(' +', ' ', re.sub(r"[\n\r\t\W]",' ',text.text_content()))+"\n")

    output.write("</document>\n")
    i+=1
    pbar.update(i)

  pbar.finish()

  output.write("</documents>")

  print("Done !")
