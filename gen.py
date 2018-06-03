#! /usr/bin/env python3

# Python standard library includes
import os
import sys
import time

# Includes that have to be installed
from textgenrnn import textgenrnn

def main():
# Control parameters
## Where we look for files (all relative to the directory this script is in)
	inputdir = "data"
	outputdir = "output"

## How many times to repeat various things
	n_overall_passes = 20		# training iterations on the combined dataset
	n_individual_passes = 2	# training iterations on each individual dataset
	output_size =  1				# how many rows to generate at each set of parameters
	n_temp_increments = 100	# how many different temperatures to try

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
	names = []
	for fname in infiles:
		if fname[-4:] == ".csv":
			text = []
			with open(os.path.join(inputdir, fname), 'r') as infile:
				for line in infile:
					# clean up typical artefacts from reading an Excel CSV as text
					cleaned = line.replace('\n', '').replace('\ufeff', '')
					text.append(cleaned)
					names.append(cleaned.split(",")[0])
			individuals[fname[:-4]] = text
			amalgamated += text
	print_with_timestamp("Read " + str(len(individuals)) + " datasets.")

## Start the RNN
	textgen = textgenrnn()
	textgen.reset()

# Train on the amalgamated dataset
	with open(os.path.join(outputdir, "amalgamated.csv"), 'w') as outfile:
		outfile.write("name,lat,lon,epoch,temp,difficulty\n")
		textgen.train_on_texts(amalgamated, new_model=True, num_epochs=1)
		for i in range(1, 1 + n_overall_passes):
			# Make sure the file gets saved at least once per training cycle
			outfile.flush()
			os.fsync(outfile)
			if i > 1:
				textgen.train_on_texts(amalgamated, new_model=False, num_epochs=1)
			for j in range(1, 1 + n_temp_increments):
				temp = set_temperature(i, j, n_overall_passes, n_temp_increments)
				for k in range(0, output_size):
					text = textgen.generate(n=1, temperature=temp, return_as_list=True)[0]
					if text is not None:
						row = str(text) + "," + str(i) + "," + str(temp)
						# TODO: come up with a difficulty rating
						outfile.write(row+"\n")

# TODO:
## step through that rejecting as necessary and adding the 3 metadata columns
## save rejects out as one set, accepts all into a single file
## then start going through the individual files
## then find more data!





# some silly maths to just get a range of temperatures that creeps up higher as we do more training passes
def set_temperature(training_epoch, output_iteration, n_epochs, n_iterations):
	return (training_epoch / n_epochs + output_iteration - 1) / n_iterations + 0.1






def print_with_timestamp(msg):
	print(time.ctime() + ": " + str(msg))
	sys.stdout.flush()
# explicitly flushing stdout makes sure that a .out file stays up to date
# otherwise it can be hard to keep track of whether a background job is hanging





if __name__ == "__main__":
	try:
		main()
	except:
		print(sys.exc_info()[0])
		import traceback
		print(traceback.format_exc())
