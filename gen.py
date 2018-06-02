from textgenrnn import textgenrnn


def main():
	textgen = textgenrnn()
	textgen.train_from_file("data/tube_stations_with_coords.csv", num_epochs=5)
	for i in range(0.25, 1, 0.25):
		textgen.generate_to_file('output/temp-' + str(i) + '.csv', n=10, temperature=i)



if __name__ == "__main__":
	try:
		main()
	except:
		import sys
		print(sys.exc_info()[0])
		import traceback
		print(traceback.format_exc())

