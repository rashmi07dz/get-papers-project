import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

# Base URL for PubMed E-utilities API
EUTILS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def fetch_pubmed_ids(query: str) -> List[str]:
    """
    Fetches PubMed IDs based on a given query using the ESearch utility.
    """
    esearch_url = f"{EUTILS_BASE_URL}esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": 100, # Limit the number of results for demonstration
        "retmode": "xml"
    }
    try:
        response = requests.get(esearch_url, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors
        root = ET.fromstring(response.content)
        ids = [id_elem.text for id_elem in root.findall(".//IdList/Id")]
        return ids
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PubMed IDs: {e}")
        return []
    except ET.ParseError as e:
        print(f"Error parsing ESearch XML: {e}")
        return []

def fetch_pubmed_details(pubmed_ids: List[str]) -> Optional[str]:
    """
    Fetches detailed XML data for a list of PubMed IDs using the EFetch utility.
    """
    if not pubmed_ids:
        return None

    efetch_url = f"{EUTILS_BASE_URL}efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml"
    }
    try:
        response = requests.get(efetch_url, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PubMed details: {e}")
        return None

def parse_pubmed_xml(xml_data: str) -> List[Dict[str, Any]]:
    """
    Parses PubMed XML data to extract paper details, including publication date
    and corresponding author email.
    """
    articles_data: List[Dict[str, Any]] = []
    if not xml_data:
        return articles_data

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"Error parsing PubMed XML data: {e}")
        return articles_data

    for article in root.findall(".//PubmedArticle"):
        pmid_element = article.find(".//PMID")
        pmid = pmid_element.text if pmid_element is not None else "N/A"

        title_element = article.find(".//ArticleTitle")
        title = title_element.text if title_element is not None else "N/A"

        # Extract Publication Date
        pub_date = "N/A"
        journal_issue = article.find(".//JournalIssue/PubDate")
        if journal_issue is not None:
            year = journal_issue.find("Year")
            month = journal_issue.find("Month")
            day = journal_issue.find("Day")
            medline_date = journal_issue.find("MedlineDate")

            if year is not None:
                pub_date = year.text
                if month is not None:
                    pub_date += f"-{month.text}"
                    if day is not None:
                        pub_date += f"-{day.text}"
            elif medline_date is not None:
                pub_date = medline_date.text # e.g., "2023 Fall"

        # Extract Authors and Affiliations
        authors_list: List[Dict[str, str]] = []
        all_affiliations: List[str] = []
        corresponding_author_email: str = "N/A"

        for author_elem in article.findall(".//AuthorList/Author"):
            last_name_elem = author_elem.find("LastName")
            fore_name_elem = author_elem.find("ForeName")
            
            author_name_parts = []
            if fore_name_elem is not None and fore_name_elem.text:
                author_name_parts.append(fore_name_elem.text)
            if last_name_elem is not None and last_name_elem.text:
                author_name_parts.append(last_name_elem.text)
            
            author_name = " ".join(author_name_parts) if author_name_parts else "N/A"

            author_affiliations = []
            for affiliation_info_elem in author_elem.findall(".//AffiliationInfo"):
                affiliation_elem = affiliation_info_elem.find("Affiliation")
                if affiliation_elem is not None and affiliation_elem.text:
                    author_affiliations.append(affiliation_elem.text)
                    all_affiliations.append(affiliation_elem.text)
                    
                    # Attempt to find email within affiliation text for corresponding author
                    if "@" in affiliation_elem.text and corresponding_author_email == "N/A":
                        # Simple regex to extract email, assuming it's part of the affiliation string
                        # This is a heuristic and might not catch all cases
                        import re
                        email_match = re.search(r'[\w\.-]+@[\w\.-]+', affiliation_elem.text)
                        if email_match:
                            corresponding_author_email = email_match.group(0)

            authors_list.append({
                "name": author_name,
                "affiliations": author_affiliations
            })

        articles_data.append({
            "PubmedID": pmid,
            "Title": title,
            "Publication Date": pub_date,
            "Authors": authors_list, # List of dicts {name, affiliations}
            "AllAffiliations": all_affiliations, # Flat list of all affiliations for filtering
            "Corresponding Author Email": corresponding_author_email
        })

    return articles_data