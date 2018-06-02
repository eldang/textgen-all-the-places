from textgenrnn import textgenrnn


textgen = textgenrnn()
textgen.reset()
textgen.train_from_file("data/tube_stations_with_coords.csv", num_epochs=5)
for i in range(1, 5):
	textgen.generate_to_file('output/temp-' + str(i/5) + '.csv', n=10, temperature=i/4)


