#!/bin/bash

# This is a script example of the sequence of commands that allow to
# generate textual runs and relevance judgments for the TREC 2004
# Robust track.

# First, use the download.pl script (provided by Claudia Hauff https://gist.github.com/chauff/4224411).
# Mind that it needs a login and a password that you need to ask to the TREC
# organisers. See http://trec.nist.gov/results.html.
perl download.pl http://trec.nist.gov/results/trec13/robust.input.html robust2004

# Then, use the test_collection_to_text.py. It iterates through all the run files
# the have previously been downloaded in the robust2004 directory, as well as the
# qrels file.
# It needs an Indri index (see http://www.lemurproject.org/indri.php) of the document
# collection, which needs to be indexed using the storeDocuments option set to true
# (in order to extract the text).
python test_collection_to_text.py -c /path/to/indri/index/of/Robust2004 -q /path/to/qrels/file -r robust2004 -o /path/to/output/xml/file
