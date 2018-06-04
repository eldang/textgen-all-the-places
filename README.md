# textgen all the places
I am a fan of [Janelle Shane](https://www.twitter.com/JanelleCShane)'s [experiments with neural networks as generators for names of various things](http://aiweirdness.com/). While walking in the [Cotswolds](https://www.cotswolds.com/plan-your-trip/towns-and-villages) recently it occurred to me that it would be fun to see her approach applied to places names in Britain. Rather than make a request, I decided to try doing it myself.


## tools
Janelle is kind enough to maintain a [FAQ](http://aiweirdness.com/faq) which leads with recommendations of the neural network frameworks she prefers. Out of those, I chose [Max Woolf](https://github.com/minimaxir)'s [textgen-rnn](https://github.com/minimaxir/textgenrnn) because I'm familiar with Python and want to run this locally rather than messing with a cloud platform.


## data
### tube stations
Conveniently, the OpenStreetMap wiki has a public domain [list of London Underground stations](https://wiki.openstreetmap.org/wiki/List_of_London_Underground_stations) in a form that's easy to copy-paste into Excel. They give the Docklands Light Railway its own category, and those station names do have something of a distinct character to them, but I decided to put them all together because there just aren't enough DLR stations on their own.

### places around England
These all came from an OpenStreetMap data export, with some fairly simple processing:

1. Extracted all points tagged with feature classes like `city`, `farm`, `hamlet`, `locality`, `suburb`, `town` and `village`
2. Cleaned up a few that had commas or digits in the names, because those cause problems with the _extremely simplistic_ way I handle the files.
3. Used [GADM](https://gadm.org/data.html)'s shapefiles to tag the points with the name of the county they are in.
4. Separated off all the farms, into one set of input data, saved as `farms.csv`.  Because this particular subset contained many more repeated names than the others (so many "Home Farm"s…), I deduplicated it, just keeping the first instance of each name regardless of the coordinates.
5. Separated off everything that didn't get tagged with a county, assuming that was because it's in the sea, and made those into a second set of input data, saved as `maritime.csv`.
6. Made a few more input data files based on very approximate regions of England, by grouping together points from the relevant counties (e.g. Kent, East & West Sussex, Brighton & Hove, Surrey, Hampshire, the Isle of Wight, Portsmouth and Southampton as `southeast.csv`).

## method
### basic howto
* To install the RNN: `pip3 install -r requirements.txt`
* To run it with some simple presets: `python3 gen.py`
* To make it share your CPU more generously if you're going to leave it running in the background (unix/linux/Mac OS X): `nice -n19 python3 gen.py`
* Output will be saved as a series of CSV files in the `/output/` folder

### to add your own data
Simply save training data as a CSV with 3 unlabelled columns:
```csv
place name, latitude in decimal degrees, longitude in decimal degrees
```
Note that the following restrictions will be imposed on output data, so you'll get better results with input data that conform to this:

* Three columns that go `word[s], number, number`.
* Place names contain only unaccented Latin letters, apostrophes, spaces, parentheses, ampersands, and dashes, with no repeated spaces or punctuation.
* Latitude & longitude are valid real numbers in a range defined by the extremes of the input data.

This is very UK-centric, because I'm specifically using it for British place names.  If you want to work on data from a region or language which these are a poor fit for, it shouldn't be too hard to tweak the restrictions, or remove them altogether by making the `evaluate_string()` function always return `True`.

### to start tweaking in other ways
I've tried to keep all the parameters controlled by variables at the start of the main function, so you can easily tweak those without having dig through much. To get a sense of what they do and what other customisations are available, I recommend looking over the iPython examples that Max shares as [documentation for textgenrnn](https://github.com/minimaxir/textgenrnn/tree/master/docs). I've found those really helpful.

### what it's doing
1. Scan `data/` folder for all available `.csv` files.
2. Load them individually and also create a massive amalgamated set from all of them.
3. Wipe the `output/` folder.
4. Starting with a fresh clean RNN model, train that `n_overall_passes` times on the whole set.
5. Each iteration, generate `output_size` rows of sample output at a range of temperatures in `n_temp_increments` increments, going higher the more times it's been trained so far.
6. Remove rows that don't fit the output patterns described above, or have a name already in the input or output data, saving them to `output/rejects.csv` so you can check if the requirements are making sense.
7. Save rows that do fit expectations to `output/amalgamated.csv` with the same 3 columns as the input plus three more which store the number of training iterations, the temperature that were used to generate them, and a score that estimates how likely I reckon it is that this combination of parameters will produce a believable fake name.
8. Save the model that's been built to this point, and then start iterating over the invididual files' contents:
9. Train the model `n_individual_passes` more times, on just the individual dataset.
10. Generate output in the same way as for the amalgamated one, saving each set with a filename that matches the input file.
11. Reload the model that was saved after the overall training, and repeat for the next file.


