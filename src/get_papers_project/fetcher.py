import requests
from typing import List, Dict
import xml.etree.ElementTree as ET # Make sure this import is at the top

def fetch_pubmed_ids(query: str) -> List[str]:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": 20,
        "retmode": "json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data["esearchresult"]["idlist"]

def fetch_pubmed_details(id_list: List[str]) -> str:
    ids = ",".join(id_list)
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ids,
        "retmode": "xml"
    }
    response = requests.get(url, params=params)
    return response.text

# This function should be at the same indentation level as the other two functions
def parse_pubmed_xml(xml_string: str) -> List[Dict]:
    articles_data = []
    root = ET.fromstring(xml_string)

    # Iterate through each PubmedArticle
    for article_elem in root.findall(".//PubmedArticle"):
        pmid_elem = article_elem.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None else "N/A"

        title_elem = article_elem.find(".//ArticleTitle")
        title = title_elem.text if title_elem is not None else "N/A"

        authors = []
        affiliations = []
        for author_elem in article_elem.findall(".//AuthorList/Author"):
            last_name_elem = author_elem.find("LastName")
            fore_name_elem = author_elem.find("ForeName")
            initials_elem = author_elem.find("Initials")
            
            name_parts = []
            if fore_name_elem is not None:
                name_parts.append(fore_name_elem.text)
            if initials_elem is not None:
                name_parts.append(initials_elem.text)
            if last_name_elem is not None:
                name_parts.append(last_name_elem.text)
            
            author_name = " ".join(filter(None, name_parts)) # Join non-None parts
            if not author_name:
                author_name = "N/A"

            authors.append(author_name)

            # Collect affiliations for all authors
            for affil_elem in author_elem.findall(".//AffiliationInfo/Affiliation"):
                if affil_elem.text:
                    affiliations.append(affil_elem.text)
        
        # Combine authors and affiliations into a single list of strings for easier processing later
        # This will create duplicates if an affiliation is shared by multiple authors,
        # but it ensures all affiliations are captured for checking
        unique_affiliations = list(set(affiliations)) # Get unique affiliations

        articles_data.append({
            "PMID": pmid,
            "Title": title,
            "Authors": "; ".join(authors), # Join authors for single cell
            "Affiliations": "; ".join(unique_affiliations) # Join unique affiliations
        })
    return articles_data