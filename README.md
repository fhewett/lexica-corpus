# lexica-corpus
Files &amp; script for lexica corpus for German text simplification

## About

The corpus consists of texts from three Wiki-based lexica in German language: [MiniKlexikon](https://miniklexikon.zum.de/wiki/Hauptseite), [Klexikon](https://klexikon.zum.de/) and [Wikipedia](https://de.wikipedia.org/wiki/Wikipedia:Hauptseite). 
The articles in the Wikis are created by volunteers and can be written, discussed, and improved upon collaboratively. 
Klexikon is aimed specifically at children aged between 6 and 12 and MiniKlexikon is designed for children who are beginner readers, and is therefore an even simpler version of the Klexikon. We make the assumption that the three different sub-corpora represent three different levels of conceptual complexity due to the target groups they are written for: younger children, children and adults. As Wikipedia articles can be extremely long, in comparison to the other two lexica, only the introduction or abstract was taken for this corpus.

This repository contains the corpora from the original study (

## How to use the script

Run the script `build.sh` to update the corpus, using the default options

Alternatively, create your own environment using the requirements and use the following options:

- to build the corpus from scratch:

`python parse_lexica.py --create_new_corpus`

- to check the Wikipedia disambiguations individually:

`python parse_lexica.py --more_info`

- to change the file names of the sub-corpora:

`--klexi_file`
`--miniklexi_file`
`--wiki_file`

## Contributors

Freya Hewett & Christopher Richter

## License

https://creativecommons.org/licenses/by-sa/4.0/
"Der Link in der URL führt dann auch zu jener Version. So kann der spätere Weiterverwender nachvollziehen, auf welche Artikelversion man sich bezieht (die Artikel können sich ja ändern). Hinzu fügt man die verlinkte Angabe "CC-BY-SA" für die Lizenz. "
Klexikon and MiniKlexikon: CC BY-SA 4.0

https://creativecommons.org/licenses/by-sa/3.0/
Wikipedia: CC BY-SA 3.0

## Citation

tbc
