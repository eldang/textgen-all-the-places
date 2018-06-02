# textgen all the places

I am a fan of [Janelle Shane](https://www.twitter.com/JanelleCShane)'s [experiments with neural networks as generators for names of various things](http://aiweirdness.com/). While walking in the [Cotswolds](https://www.cotswolds.com/plan-your-trip/towns-and-villages) recently it occurred to me that it would be fun to see her approach applied to places names in Britain. Rather than make a request, I decided to try doing it myself.

## tools

Janelle is kind enough to maintain a [FAQ](http://aiweirdness.com/faq) which leads with recommendations of the neural network frameworks she prefers. Out of those, I chose [Max Woolf](https://github.com/minimaxir)'s [textgen-rnn](https://github.com/minimaxir/textgenrnn) because I'm familiar with Python and want to run this locally rather than messing with a cloud platform.

## data

### tube stations

Conveniently, the OpenStreetMap wiki has a public domain [list of London Underground stations](https://wiki.openstreetmap.org/wiki/List_of_London_Underground_stations) in a form that's easy to copy-paste into Excel. I'm including DLR stations because although they have a bit of a distinct feel to them they're not radically different.

## method

To install the RNN: `pip3 install -r requirements.txt`

To run it with some simple presets: `python3 gen.py`

## TODO

Either make `gen.py` configurable or start playing with this interactively.
