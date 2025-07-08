import re

def is_non_academic(affiliation: str) -> bool:
    # Temporary test: Let's say we consider anything with 'University' as non-academic for testing
    # (THIS IS NOT THE REAL LOGIC, JUST FOR DEMO)
    # if "University" in affiliation:
    #     print(f"DEBUG: Found 'University' in '{affiliation}' - marking as non-academic for test")
    #     return True

    # ORIGINAL LOGIC:
    non_academic_keywords = ["company", "industry", "pharma", "inc.", "corp.", "llc", "ltd.", "private", "biotech"]
    # Convert affiliation to lowercase for case-insensitive matching
    affiliation_lower = affiliation.lower()

    for keyword in non_academic_keywords:
        # Use regex word boundary to match whole words or common abbreviations
        if re.search(r'\b' + re.escape(keyword) + r'\b', affiliation_lower):
            return True
    return False
