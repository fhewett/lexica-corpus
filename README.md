# lexica-corpus
Files &amp; script for lexica corpus for German text simplification

## About

The corpus consists of texts from three Wiki-based lexica in German language: [MiniKlexikon](https://miniklexikon.zum.de/wiki/Hauptseite), [Klexikon](https://klexikon.zum.de/) and [Wikipedia](https://de.wikipedia.org/wiki/Wikipedia:Hauptseite). 
The articles in the Wikis are created by volunteers and can be written, discussed, and improved upon collaboratively. 
Klexikon is aimed specifically at children aged between 6 and 12 and MiniKlexikon is designed for children who are beginner readers, and is therefore an even simpler version of the Klexikon. We make the assumption that the three different sub-corpora represent three different levels of conceptual complexity due to the target groups they are written for: younger children, children and adults. As Wikipedia articles can be extremely long, in comparison to the other two lexica, only the introduction or abstract was taken for this corpus.

This repository contains the corpora from the original study (295 texts per sub-corpus in the `orig_files` folder), extended versions with ca. 1000 texts (as of August 2021) per sub-corpus (the `miniklexi_corpus.txt`, `klexi_corpus.txt`, `wiki_corpus.txt` files in this folder: **updated August 2021, current size 2934 total texts**) and a script to update the extended version as new articles are added to the Klexikon and MiniKlexikon.

### Note on the format

The sub-corpora feature a symbol for "end of paragraph": MiniKlexikon and Klexikon `<eop>`and in Wikipedia just `*`

### Statistics for the original (smaller) corpora

Sub-corpus | Avg. article length | Avg. sentence length
---------- | ------------------- | --------------------
MiniKlexikon | 134.86 | 9.57
Klexikon | 305.45 | 13.29
Wikipedia | 169.89 | 18.41

## How to use the script

Run the script `build.sh` to update the corpus, using the default options (or if you use Conda then use `build_conda.sh`)

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

The Klexikon and MiniKlexikon files are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

The Wikipedia files are licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)

## Citation

tbc

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5196030.svg)](https://doi.org/10.5281/zenodo.5196030)
