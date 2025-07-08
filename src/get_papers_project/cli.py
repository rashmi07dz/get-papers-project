import argparse
import pandas as pd
from get_papers_project.fetcher import fetch_pubmed_ids, fetch_pubmed_details, parse_pubmed_xml
from get_papers_project.filter import is_non_academic

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed papers with non-academic authors.")
    parser.add_argument("query", type=str, help="PubMed search query")
    parser.add_argument("-f", "--file", type=str, help="CSV file to save results")
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug info")
    args = parser.parse_args()

    ids = fetch_pubmed_ids(args.query)
    if args.debug:
        print("Fetched IDs:", ids)

    xml_data = fetch_pubmed_details(ids)
    
    # Check if XML data is valid before parsing
    if not xml_data or "PubmedArticleSet" not in xml_data:
        print("No valid PubMed XML data received or no articles found.")
        return # This return is inside the main() function

    articles_parsed_data = parse_pubmed_xml(xml_data)

    if args.debug:
        print("Parsed Data (first 2 articles):")
        for i, article in enumerate(articles_parsed_data):
            if i >= 2: break
            print(article)

    # --- Filtering Logic ---
    filtered_articles = []
    for article in articles_parsed_data:
        # Check if any part of the affiliations string indicates non-academic
        # Split affiliations by '; ' and check each one
        affiliations = [aff.strip() for aff in article.get("Affiliations", "").split(';') if aff.strip()]
        
        has_non_academic_author = False
        for affil in affiliations:
            if is_non_academic(affil):
                has_non_academic_author = True
                break # Found one, no need to check further for this article
        
        if has_non_academic_author:
            filtered_articles.append(article)
    
    if args.debug:
        print(f"\nTotal articles fetched: {len(articles_parsed_data)}")
        print(f"Articles with non-academic authors: {len(filtered_articles)}")

    # --- CSV Writing Logic ---
    if not filtered_articles:
        print("No articles found with non-academic authors to save.")
        return # This return is also inside the main() function

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(filtered_articles)

    output_filename = args.file if args.file else "pubmed_non_academic_papers.csv"
    
    # Save to CSV
    try:
        df.to_csv(output_filename, index=False, encoding='utf-8')
        print(f"\nSuccessfully saved {len(filtered_articles)} articles to {output_filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    main()