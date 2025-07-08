import argparse
import pandas as pd
import sys
from typing import List, Dict, Any

# Assuming these are in the same package structure
from get_papers_project.fetcher import fetch_pubmed_ids, fetch_pubmed_details, parse_pubmed_xml
from get_papers_project.filter import is_non_academic # Assuming this function exists

def main():
    parser = argparse.ArgumentParser(
        description="PubMed Paper Filter CLI Tool. Fetches and filters papers by non-academic author affiliation."
    )
    parser.add_argument(
        "query",
        type=str,
        help="The search term to query PubMed (e.g., 'artificial intelligence in medicine')."
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Specify the name of the CSV file to save the results. If not provided, output to console."
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug output, showing fetched IDs and parsed data snippets."
    )

    args = parser.parse_args()

    if args.debug:
        print(f"Debug: Starting search for query: '{args.query}'")

    # Step 1: Fetch PubMed IDs
    ids = fetch_pubmed_ids(args.query)
    if not ids:
        print("No PubMed IDs found for the given query. Exiting.")
        return

    if args.debug:
        print(f"Debug: Fetched {len(ids)} PubMed IDs: {ids[:5]}...") # Show first 5 IDs

    # Step 2: Fetch detailed XML data
    xml_data = fetch_pubmed_details(ids)
    if not xml_data:
        print("Failed to fetch detailed PubMed XML data. Exiting.")
        return

    if args.debug:
        print(f"Debug: Fetched XML data. Preview (first 500 chars):\n{xml_data[:500]}...")

    # Step 3: Parse XML data
    parsed_articles = parse_pubmed_xml(xml_data)
    if not parsed_articles:
        print("No articles could be parsed from the XML data. Exiting.")
        return

    if args.debug:
        print(f"Debug: Parsed {len(parsed_articles)} articles.")

    # Prepare data for DataFrame with required columns
    output_records: List[Dict[str, Any]] = []

    for article in parsed_articles:
        # Check if any author has a non-academic affiliation
        has_non_academic_author = False
        non_academic_authors_names: List[str] = []
        company_affiliations: List[str] = []

        # Iterate through each author and their affiliations
        for author in article.get("Authors", []):
            author_name = author.get("name", "N/A")
            for affiliation_text in author.get("affiliations", []):
                if is_non_academic(affiliation_text):
                    has_non_academic_author = True
                    # Add author name if not already added to avoid duplicates
                    if author_name not in non_academic_authors_names and author_name != "N/A":
                        non_academic_authors_names.append(author_name)
                    
                    # Extract company names (heuristic: often the first part before a comma/city)
                    # This is a basic heuristic, more advanced NLP could be used
                    company_name = affiliation_text.split(',')[0].strip()
                    if any(term in company_name.lower() for term in ['inc.', 'ltd.', 'corp', 'pharma', 'biotech', 'company', 'industry', 'private']) and \
                       company_name not in company_affiliations:
                        company_affiliations.append(company_name)


        if has_non_academic_author:
            output_records.append({
                "PubmedID": article.get("PubmedID"),
                "Title": article.get("Title"),
                "Publication Date": article.get("Publication Date"),
                "Non-academic Author(s)": "; ".join(non_academic_authors_names) if non_academic_authors_names else "N/A",
                "Company Affiliation(s)": "; ".join(company_affiliations) if company_affiliations else "N/A",
                "Corresponding Author Email": article.get("Corresponding Author Email", "N/A")
            })
    
    if not output_records:
        print("No papers found with non-academic authors based on the filtering heuristics.")
        return

    df = pd.DataFrame(output_records)

    # Step 4: Output results
    if args.file:
        try:
            df.to_csv(args.file, index=False)
            print(f"Results saved to {args.file}")
        except IOError as e:
            print(f"Error saving file {args.file}: {e}", file=sys.stderr)
            # Fallback to printing to console if file save fails
            print("\n--- Results (could not save to file) ---")
            print(df.to_string())
    else:
        print("\n--- Results ---")
        print(df.to_string()) # Using to_string() for better console formatting than print(df)

if __name__ == "__main__":
    main()