from os import error
import requests
import re
from bs4 import BeautifulSoup
import json
import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument(
    "--create_new_corpus",
    help="create a new corpus from scratch (takes a while)",
    action="store_true",
)
parser.add_argument(
    "--klexi_file", help="path to file with klexikon corpus", default="klexi_corpus.txt"
)
parser.add_argument(
    "--miniklexi_file",
    help="path to file with miniklexikon corpus",
    default="miniklexi_corpus.txt",
)
parser.add_argument(
    "--wiki_file", help="path to file with wikipedia corpus", default="wiki_corpus.txt"
)
parser.add_argument(
    "--more_info",
    help="makes you choose the associated Wikipedia article",
    action="store_true"
)

args = parser.parse_args()

def remove_duplicates(corpus):
    """Removes duplicate titles from corpus"""

    corpus_key = list(corpus.keys())[0]
    page_names = [p["title"] for p in corpus[corpus_key]]
    seen = set()
    uniq, dup = [], []
    for elem in corpus[corpus_key]:
        if elem["title"] not in seen:
            uniq.append(elem["title"])
            seen.add(elem["title"])
        else:
            dup.append(elem)

    for elem in dup:
        corpus[corpus_key].remove(elem)

    return corpus


def check_corpus(filename):
    """Opens the JSON file, adds titles and IDs to list"""

    titles, ids = [], []
    with open(filename, encoding="utf-8") as json_file:
        data = json.load(json_file)

    corpus_key = list(data.keys())[0]
    for p in data[corpus_key]:
        titles.append(p["title"])
        ids.append(p["id"])

    return titles, ids


def wiki_dis(pagename):

    """Adapted from __load function here: https://github.com/goldsmith/Wikipedia/blob/master/wikipedia/wikipedia.py
    Checks if the Klexikon pages are available on Wikipedia or if they lead to disambiguations,
    missing pages or redirected pages"""

    disambiguations, missing, redirected = None, None, None

    URL = "https://de.wikipedia.org/w/api.php"

    params = {
        "prop": "info|pageprops",
        "inprop": "url",
        "ppprop": "disambiguation",
        "redirects": "",
        "titles": pagename,
        "format": "json",
        "action": "query",
        }

    response = requests.get(url = URL, params = params).json()
    query = response["query"]
    pageid = list(query["pages"].keys())[0]
    page = query["pages"][pageid]

    # missing is present if the page is missing
    if "missing" in page:
        missing = pagename

    elif "redirects" in query:
        redirected = pagename

    elif "pageprops" in page:
        params = {
            "prop": "revisions",
            "rvprop": "content",
            "rvparse": "",
            "rvlimit": 1,
            "titles": pagename,
            "format": "json",
            "action": "query",
            }

        response = requests.get(url = URL, params = params).json()
        html = response["query"]["pages"][pageid]["revisions"][0]["*"]

        lis = BeautifulSoup(html, "html.parser").find_all("li")
        filtered_lis = [
            li for li in lis if not "tocsection" in "".join(li.get("class", []))
        ]
        may_refer_to = [li.a.get_text() for li in filtered_lis if li.a]
        ref_explanation = [li.get_text() for li in filtered_lis if li.a]

        disambiguations = solveWikiDis(pagename, may_refer_to, ref_explanation) if args.more_info else may_refer_to[0]

    return disambiguations, missing, redirected


def parse_klexikon(page_names, id_dict):
    """Sends get requests to the Klexikon API and creates the formatted corpus"""

    corpus = {}
    corpus["klexikon"] = []
    klexi_url = "https://klexikon.zum.de/wiki/"

    for i, page in enumerate(page_names):
        progbar(i, len(page_names))

        URL = "https://klexikon.zum.de/api.php"
        PARAMS = {
            "action": "parse",
            "page": page,
            "format": "json",
            "prop": "wikitext",
            "redirects": True,
        }

        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()
        try:
            text1 = DATA["parse"]["wikitext"]["*"]
        except KeyError:  # if it doesn't exist in the wiki
            page_names.remove(page)
            print("...removed: ", page)
            continue

        text2 = text1.replace("\n", "\\n")  # To make RegEx compatible
        matches = re.findall(
            r"\]\]\\n(?!\[\[Datei|\[\[Kategorie)(.*?){{Artikel|\}\}\\n(?!\[\[Kategorie)(.*?){{Artikel", text2, re.MULTILINE # extracting the article text bulk
        )
        matches = [tuple(j for j in i if j)[-1] for i in matches] # need to merge the 2 capture groups

        if matches == []:
            page_names.remove(page)
            print("...removed: ", page)
            continue
        else:
            klexi_text = matches[0]
            klexi_text = re.sub(
                r"(<Gallery>|<gallery>)(.*?)(</Gallery>|</gallery>)", "", klexi_text
            )
            klexi_text = re.sub(r"\[\[([\w\-öäßü ]*)\]\]", r"\1", klexi_text)
            klexi_text = re.sub(r"(\[\[Datei:|\[\[File:)([\s\S]*?)\]\] ?\\n", "", klexi_text)
            klexi_text = re.sub(r"\[\[[\S\s]*?\|([\S\s]*?)\]\]", r"\1", klexi_text)
            #This is the <eop> (end of paragraph) marker
            klexi_text = klexi_text.replace("\\n\\n", "<eop>")
            klexi_text = klexi_text.replace("\\n", " ")
            klexi_text = klexi_text.replace("==", "")
            klexi_text = klexi_text.replace("  ", " ")
            klexi_text = klexi_text.replace("[[", "")
            klexi_text = klexi_text.replace("]]", "")

            corpus["klexikon"].append(
                {
                    "title": page,
                    "id": id_dict[page],
                    "url": klexi_url + page,
                    "text": klexi_text,
                }
            )

    return corpus, page_names


def parse_wiki(page_names, id_dict, dis_dict):
    """Sends get requests to the German Wikipedia API and creates the formatted corpus"""

    corpus = {}
    corpus["wiki"] = []
    wiki_url = "https://de.wikipedia.org/wiki/"

    for i, page in enumerate(page_names):
        progbar(i, len(page_names))

        if page in dis_dict:
            page_ = dis_dict[page]
        else:
            page_ = page

        URL = "https://de.wikipedia.org/w/api.php"

        params = {
            "prop": "extracts",
            #'explaintext': True,
            "titles": page_,
            "exintro": "",
            "format": "json",
            "action": "query",
            "exsectionformat": "plain",
            "redirects": True,
            }

        response = requests.get(url = URL, params = params).json()
        page_id = list(response["query"]["pages"].keys())[0]
        try:
            clean_text = response["query"]["pages"][page_id]["extract"]
        except KeyError:
            page_names.remove(page)
            print("...removed: ", page, page_)
            continue

        # EoP marker
        with_eop = clean_text.replace("</p><p>", " * ")
        # Remove HTML
        html_removed = re.sub(r"<[^>]*>", "", with_eop)
        # Remove line break tags
        clean_text = html_removed.replace("\n", "")

        corpus["wiki"].append(
            {
                "title": page_,
                "id": id_dict[page],
                "url": wiki_url + page_,
                "text": clean_text,
            }
        )

    return corpus, page_names


def parse_miniklexi(page_names, id_dict):
    """Sends get requests to the MiniKlexikon API and creates the formatted corpus"""

    corpus = {}
    corpus["miniklexikon"] = []
    easy_url = "https://miniklexikon.zum.de/wiki/"

    for i, page in enumerate(page_names):
        progbar(i, len(page_names))

        URL = "https://miniklexikon.zum.de/api.php"
        params = {"action": "parse", "page": page, "format": "json", "prop": "wikitext"}

        response = requests.get(url=URL, params=params).json()

        text1 = response["parse"]["wikitext"]["*"]
        text2 = text1.replace("\n", "\\n")

        matches = re.finditer(
            r"\]\] ?\\n(?!\[\[Datei)(.*){{Artikel}}", text2, re.MULTILINE
        )

        for match in matches:
            new1 = match.group(1)  # + match.group(2)

        matches = re.finditer(r"(.*)?(<Gallery>|<gallery>).*", new1, re.MULTILINE)
        if matches:
            for match in matches:
                new1 = match.group(1)

        miniklexi_text = re.sub(r"\[\[([\w\-öäßü ]*)\]\]", r"\1", new1)
        miniklexi_text = re.sub(r"\[\[[\S\s]*?\|([\S\s]*?)\]\]", r"\1", miniklexi_text)
        miniklexi_text = miniklexi_text.replace("\\n\\n", "<eop>")
        miniklexi_text = miniklexi_text.replace("\\n", " ")
        miniklexi_text = miniklexi_text.replace("==", "")
        miniklexi_text = miniklexi_text.replace("  ", " ")
        miniklexi_text = miniklexi_text.replace("<br/>", "")

        corpus["miniklexikon"].append(
            {"title": page, "id": id_dict[page], "url": easy_url + page, "text": miniklexi_text}
        )

    return corpus


def write_to_file(file_name, corpus):

    with open(file_name, "w+") as output:
        json.dump(corpus, output, ensure_ascii=False)


def append_to_file(file_name, corpus):

    with open(file_name, encoding="utf-8") as existing_file:
        data = json.load(existing_file)

    corpus_key = list(data.keys())[0]
    temp = data[corpus_key]
    for p in corpus[corpus_key]:
        temp.append(p)

    return {corpus_key: temp}


def getTitles():
    """Sends a get-request to the MiniKlexicon API and retrieves all titles of the articles
    Adapted from: https://textmining.wp.hs-hannover.de/Terminologie.html"""

    titles = []
    URL = "https://miniklexikon.zum.de/api.php"
    params = {
        "action": "query",
        "cmtitle": "Kategorie:Alle Artikel",
        "cmlimit": "max",
        "list": "categorymembers",
        "format": "json",
        }
    response = requests.get(url = URL, params = params).json()

    # continue looking for titles as long as the "continue" parameter is passed on
    while(response):
        titles.extend( [t['title'] for t in response['query']['categorymembers']] )
        if 'continue' in response:
            cont = response['continue']['cmcontinue']
            params = {
                    "action": "query",
                    "cmtitle": "Kategorie:Alle Artikel",
                    "cmlimit": "max",
                    "cmcontinue": cont,
                    "list": "categorymembers",
                    "format": "json",
                }
            response = requests.get(url = URL, params = params).json()
        else:
            break

        if not cont:
            response = None

    return titles


def solveWikiDis(pagename, ref, ref_explanation):
    """Helps to solve disambiguation with user interaction
    Shows all possible Wikipedia references for one Klexicon article
    The user sees a small explanation and can choose which Wikipedia article should be taken as reference"""


    print(f"\n Für den Eintrag: {pagename} im Klexikon wurden folgende mögliche Einträge gefunden:")
    ref_dict = {}
    ref_exp = {}
    for i, name in enumerate(ref):
        ref_dict[i+1] = name
        ref_exp[i+1] = ref_explanation[i]
        print(str(i+1)+ ": " + ref_exp[i+1])

    error_text = f"Die Eingabe muss eine Zahl zwischen {str(list(ref_dict)[0])} und {str(list(ref_dict)[-1])} sein."
    print(error_text)
    while True:
        try:
            usr_input = int(input("Bitte geben Sie die Nummer an, welche zu diesem Artikel passt: "))
            if usr_input < int(list(ref_dict)[0]) or usr_input > int(list(ref_dict)[-1]):
                raise ValueError(error_text)
            break
        except ValueError:
            print(error_text)

    print(ref_dict[usr_input])

    return ref_dict[usr_input]

def progbar(curr, total):
    frac = curr/total
    filled_progbar = round(frac*20)
    print('\r', '#'*filled_progbar + '-'*(20-filled_progbar), '[{:>7.2%}]'.format(frac), end='')


if __name__ == "__main__":

     # If a new corpus should be created, one needs to pass the according argument
    if args.create_new_corpus:
        print("Warning: creating new corpus from scratch – this could take a while!")
        current_pages = []
        current_ids = [0]
    # Else the current corpus will be used for comparison
    else:
        current_pages, current_ids = check_corpus(args.miniklexi_file)

    # Create Session globally
    S = requests.Session()

    # Retrieve all titles of the online MiniKlexicon and compare them to the offline corpus
    page_names_miniklexi = []
    titles = getTitles()
    for title in titles:
        if title not in current_pages:
            page_names_miniklexi.append(title)

    if page_names_miniklexi == []:
        print("Corpus is already up to date!")
        sys.exit("Script has terminated as corpora are up to date")

    # Add ID numbers to pagenames
    id_dict = {}
    for i, name in enumerate(page_names_miniklexi):
        id_dict[name] = i + current_ids[-1]

    # Check that they exist in Klexikon, adjust page names list and create Klexikon corpus
    print("creating Klexikon corpus...")
    klexi_corp, pn_klexi = parse_klexikon(page_names_miniklexi, id_dict)

    # Use adjusted page names list to get Wiki pages, solve disambiguations
    dis, mis, red = [], [], []
    dis_d, dis_d_reverse = {}, {}
    for pn in pn_klexi:
        d, m, r = wiki_dis(pn)
        if d != None:
            dis.append((pn, d))
            dis_d[pn] = d
            dis_d_reverse[d] = pn
        if m != None:
            mis.append(m)
        if r != None:
            red.append(r)

    # Print disambiguations to output file to be manually checked
    with open("disambiguations.txt", "w") as output_file:
        for tup in dis:
            print(tup, file=output_file)

    # Create Wiki corpus
    print("...done. Creating Wiki corpus...")
    # Update page names
    klexikon_page_names = [p["title"] for p in klexi_corp["klexikon"]]
    # Delete missing pages
    wiki_page_names = [pn for pn in klexikon_page_names if pn not in mis]

    print("...removed: ", mis)
    wiki_corp, updated_page_names = parse_wiki(wiki_page_names, id_dict, dis_d)

    wiki_page_names_new = []
    for p in wiki_corp["wiki"]:
        try:
            wiki_page_names_new.append(dis_d_reverse[p["title"]])
        except KeyError:
            wiki_page_names_new.append(p["title"])

    # Create MiniKlexikon corpus
    print("...done. Creating MiniKlexikon corpus...")
    miniklexi_corp = parse_miniklexi(wiki_page_names_new, id_dict)

    updated_miniklexi_page_names = [p["title"] for p in miniklexi_corp["miniklexikon"]]

    # Remove missing pages from Klexikon
    to_delete = []
    for elem in klexi_corp["klexikon"]:
        if elem["title"] not in updated_miniklexi_page_names:
            to_delete.append(elem)

    for elem in to_delete:
        klexi_corp["klexikon"].remove(elem)

    # Remove duplicates, save to file

    wiki_corp = remove_duplicates(wiki_corp)
    klexi_corp = remove_duplicates(klexi_corp)
    miniklexi_corp = remove_duplicates(miniklexi_corp)

    if args.create_new_corpus:
        write_to_file(args.wiki_file, wiki_corp)
        write_to_file(args.miniklexi_file, miniklexi_corp)
        write_to_file(args.klexi_file, klexi_corp)

    else:
        updated_wiki = append_to_file(args.wiki_file, wiki_corp)
        write_to_file(args.wiki_file, updated_wiki)
        updated_mini = append_to_file(args.miniklexi_file, miniklexi_corp)
        write_to_file(args.miniklexi_file, updated_mini)
        updated_klexi = append_to_file(args.klexi_file, klexi_corp)
        write_to_file(args.klexi_file, updated_klexi)

    print("...done. All corpora saved to file, please check disambiguations")

    print(len(wiki_corp['wiki']))
    print(len(miniklexi_corp['miniklexikon']))
    print(len(klexi_corp['klexikon']))

    assert (
        len(wiki_corp["wiki"])
        == len(miniklexi_corp["miniklexikon"])
        == len(klexi_corp["klexikon"])
    )  
