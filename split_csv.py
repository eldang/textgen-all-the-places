#! /usr/bin/env python3

# Python standard library includes
import os
import re
import sys
import time

def main():
	inputdir = "maps"
	outputdir = "data"
	inputfile = "england_places.csv"
	skiplist = ["farms"]
	threshold = 200

	inputpath = os.path.join(inputdir, inputfile)

	if not os.path.exists(outputdir):
		os.mkdir(outputdir)

	print_with_timestamp("Loading input data from " + inputpath)
	counties = {}
	with open(inputpath, 'r') as infile:
		for line in infile:
			# clean up typical artefacts from reading an Excel CSV as text
			cleaned = line.replace('\n', '').replace('\ufeff', '')
			if cleaned != '':
				county = cleaned.split(",")[0]
				if county not in skiplist:
					if county not in counties:
						counties[county] = []
					counties[county].append(cleaned.replace(county + ",", "", 1))

	print_with_timestamp("Read data from " + str(len(counties)) + " counties")
	exported = 0
	for county in counties.keys():
		if len(counties[county]) >= threshold:
			outputpath = os.path.join(outputdir, county.replace(" ", "_").lower() + ".csv")
			print(outputpath)
			with open(outputpath, 'w') as outfile:
				for line in counties[county]:
					outfile.write(line + "\n")
			exported += 1
	print_with_timestamp("Wrote separate files for the " + str(exported) + " counties which had at least " + str(threshold) + " place names each")









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
