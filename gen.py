#! /usr/bin/env python3

# Python standard library includes
import os
import sys
import time

# Includes that have to be installed
from textgenrnn import textgenrnn

# A convenience function I'll call a bunch:
def print_with_timestamp(msg):
	print(time.ctime() + ": " + str(msg))
	sys.stdout.flush()

# Where we look for files (all relative to the directory this script is in)
inputdir = "data"
outputdir = "output"



# Get things started
## Make sure we have an output directory and it's empty
if os.path.isdir(outputdir):
	for fname in os.listdir(outputdir):
		if fname != "README.md": # we'll keep this one so Github keeps the directory
			os.remove(os.path.join(outputdir, fname))
else:
	os.mkdir(outputdir)

## Now load all the data
print_with_timestamp("Loading input data from " + inputdir + "/")
infiles = os.listdir(inputdir)
amalgamated = []
individuals = {}
for fname in infiles:
	if fname[-4:] == ".csv":
		text = []
		with open(os.path.join(inputdir, fname), 'r') as infile:
			for line in infile:
				text.append(line.replace('\n', '').replace('\ufeff', ''))
				# the two .replace() calls above are just to clean up typical artefacts
		individuals[fname[:-4]] = text
		amalgamated += text
print_with_timestamp("Read " + str(len(individuals)) + " datasets.")

## Start the RNN
textgen = textgenrnn()
textgen.reset()



for i in range(1, 3):
	textgen.train_on_texts(amalgamated, new_model=True, num_epochs=1)
	for j in range(1, 1+i):
		textgen.generate_to_file('output/iteration-' + str(i) + '-temp-' + str(j/4) + '.csv', n=10, temperature=j/4)


