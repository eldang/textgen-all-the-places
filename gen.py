from textgenrnn import textgenrnn


textgen = textgenrnn()
textgen.reset()
for i in range(1, 11):
	textgen.train_from_file("data/tube_stations_with_coords.csv", num_epochs=1)
	for j in range(1, 1+i):
		textgen.generate_to_file('output/iteration-' + str(i) + '-temp-' + str(j/4) + '.csv', n=10, temperature=j/4)


