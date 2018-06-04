#! /usr/bin/env python3

# Python standard library includes
import os
import re
import sys
import time

# Includes that have to be installed
import psutil
from textgenrnn import textgenrnn

def main():
# Control parameters
## Where we look for files (all relative to the directory this script is in)
	inputdir = "data"
	outputdir = "output"
	rejects = "rejects.csv"
	savedweights = "deliberately_saved_weights.hdf5"

## How many times to repeat various things
	n_overall_passes =  1			# training iterations on the combined dataset
	n_individual_passes = 20	# training iterations on each individual dataset
	output_size =  1					# how many rows to generate at each set of parameters
	n_temp_increments = 200		# how many different temperatures to try

# Get things started
## First call to this function sets up its tracking
	psutil.cpu_times_percent(interval=None, percpu=False)
## Make sure we have an output directory and it's empty
	if os.path.isdir(outputdir):
		for fname in os.listdir(outputdir):
			if fname != "README.md": # we'll keep this one so Github keeps the directory
				os.remove(os.path.join(outputdir, fname))
	else:
		os.mkdir(outputdir)

## Now load all the data
	print_with_timestamp("Loading input data from " + inputdir + "/*.csv")
	infiles = os.listdir(inputdir)
	amalgamated = []
	individuals = {}
	alreadyseen = []
	for fname in infiles:
		if fname[-4:] == ".csv":
			text = []
			with open(os.path.join(inputdir, fname), 'r') as infile:
				for line in infile:
					# clean up typical artefacts from reading an Excel CSV as text
					cleaned = line.replace('\n', '').replace('\ufeff', '')
					if cleaned != '':
						text.append(cleaned)
						alreadyseen.append(cleaned.split(",")[0])
			individuals[fname[:-4]] = text
			amalgamated += text
	print_with_timestamp("Read " + str(len(individuals)) + " datasets.")

## Start the RNN
	textgen = textgenrnn()
	textgen.reset()

## Open the rejects file
	with open(os.path.join(outputdir, rejects), 'w') as rejectsfile:
		rejectsfile.write("source,reason,epoch,temp,difficulty\n")

# Train on and apply to the amalgamated dataset
		handle_dataset(textgen, outputdir, rejectsfile, "amalgamated", amalgamated, n_overall_passes, n_temp_increments, output_size, alreadyseen, True)

# Train on and apply to the individual datasets
		textgen.save(savedweights)
		for dataset in individuals.keys():
			textgen = textgenrnn(savedweights)
			handle_dataset(textgen, outputdir, rejectsfile, dataset, individuals[dataset], n_individual_passes, n_temp_increments, output_size, alreadyseen, False)





def handle_dataset(textgen, outputdir, rejectsfile, datasetname, data, n_passes, n_temp_increments, output_size, alreadyseen, newmodel):
	bounds = find_bounds(data)
	with open(os.path.join(outputdir, datasetname + ".csv"), 'w') as outfile:
		outfile.write("name,lat,lon,epoch,temp,difficulty\n")
		print_with_timestamp(
			"Starting work on dataset '" + datasetname +
			"' which contains " + str(len(data)) +
			" entries and will get " + str(n_passes) + " iteration[s] of training."
		)
		dynamic_wait(1)
		textgen.train_on_texts(data, new_model=newmodel, num_epochs=1)
		for i in range(1, 1 + n_passes):
			# Make sure the file gets saved at least once per training cycle
			flushbuffers([outfile, rejectsfile])
			if i > 1:
				print_with_timestamp(
					"Training iteration " + str(i) + " of " + str(n_passes) +
					" on dataset '" + datasetname + "'"
				)
				dynamic_wait(n_passes)
				textgen.train_on_texts(data, new_model=False, num_epochs=1)
			print_with_timestamp(
				"Generating " + str(n_temp_increments * output_size) +
				" output entries at " + str(n_temp_increments) +
				" temperatures from dataset '" + datasetname +
				"' training iteration " + str(i) + " of " + str(n_passes)
			)
			for j in range(1, 1 + n_temp_increments):
				temp = set_temperature(i, j, n_passes, n_temp_increments)
				texts = textgen.generate(n=output_size, temperature=temp, return_as_list=True)
				for text in texts:
					metadata = str(i) + "," + str(temp) + "," + calc_difficulty(i, j, n_passes, n_temp_increments)
					verdict = evaluate_string(text, alreadyseen, bounds)
					if verdict == "accept":
						outfile.write(text + "," + metadata + "\n")
						alreadyseen.append(text.split(",")[0])
					else:
						rejectsfile.write(datasetname + "," + verdict + ", " + metadata)
						rejectsfile.write("," + text + "\n")
				dynamic_wait(n_temp_increments)





def find_bounds(data):
	minX = 180
	maxX = -180
	minY = 90
	maxY = -90
	for row in data:
		X = float(row.split(",")[2])
		Y = float(row.split(",")[1])
		if X < minX: minX = X
		if X > maxX: maxX = X
		if Y < minY: minY = Y
		if Y > maxY: maxY = Y
	return {
		'minX': minX,
		'maxX': maxX,
		'minY': minY,
		'maxY': maxY
	}




# checks output for being in broadly the right format
def evaluate_string(text, alreadyseen, bounds):
	parts = text.split(",")
	# this regex should match:
	## starts with a capitalised word
	## may contain more words, separated by single spaces, dashes or ampersands
	## and up to 1 parenthesised word or set of words
	## no caps that aren't at the start of words, but only the first word has have a starting capital letter
	## See https://www.debuggex.com/r/eUjXEGWUUtEY8f2- for a diagram
	namespattern = r"([A-Z][a-z]*)+( & ([A-Z]?[a-z]*))?([ '\-]([A-Z]?[a-z]*)+)*(\(([A-Z]?[a-z]*)+( &)?([ '\-]([A-Z]?[a-z]*)+)*\))?"
	# this regex should match:
	## any valid number with 1-3 digits before an optional decimal point
	## and 1 or more after a point if present.
	## See https://www.debuggex.com/r/h-XQ3XwR6iPsCtVH for a diagram
	digitspattern = r"\-?\d\d?\d?(\.\d+)?"
	if len(parts) < 3:
		return "missing column"
	elif len(parts) > 3:
		return "extra column"
	elif re.fullmatch(namespattern, parts[0]) is None:
		return "name invalid"
	elif re.fullmatch(digitspattern, parts[1]) is None:
		return "lat invalid"
	elif re.fullmatch(digitspattern, parts[2]) is None:
		return "lon invalid"
	elif float(parts[1]) < bounds['minY']:
		return "S of bounds"
	elif float(parts[1]) > bounds['maxY']:
		return "N of bounds"
	elif float(parts[2]) < bounds['minX']:
		return "W of bounds"
	elif float(parts[2]) > bounds['maxX']:
		return "E of bounds"
	elif parts[0] in alreadyseen:
		return "repeat"
	else:
		return "accept"




# some silly maths to just get a range of temperatures that creeps up higher as we do more training passes
def set_temperature(training_epoch, output_iteration, n_epochs, n_iterations):
	x = 1.1	# arbitrary multiplier
	y = 0.1	# arbitrary amount to add
	return (training_epoch / n_epochs + output_iteration) / n_iterations * x + y



# some slightly less silly maths to come up with a vague approximation of how closely I expect a given entry to resemble the training data
def calc_difficulty(training_epoch, output_iteration, n_epochs, n_iterations):
	return str((training_epoch / n_epochs + 1 - output_iteration / n_iterations) / 2)



# wait an amount of time that relates to CPU load, so as to share better
def dynamic_wait(divisor):
	times = psutil.cpu_times_percent(interval=None, percpu=False)
	foreground = times.user + times.nice
	background = times.system + times.idle
	if foreground > background:
		sys.stdout.flush()
		time.sleep((foreground - background) / divisor)





def flushbuffers(fds):
	sys.stdout.flush()
	for fd in fds:
		fd.flush()
		os.fsync(fd)




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
