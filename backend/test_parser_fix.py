import requests
from bs4 import BeautifulSoup

def test_fixed_parser():
    """Test the fixed parser with the actual HTML"""
    target_id = "25057"
    
    # Fetch the page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get("https://sih.gov.in/sih2025PS", headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all table rows
    rows = soup.find_all('tr')
    print(f"Total rows found: {len(rows)}")
    
    for i, row in enumerate(rows):
        cells = row.find_all('td')
        
        if len(cells) >= 15:
            try:
                # Check SIH code column (position 14)
                sih_code_cell = cells[14] if len(cells) > 14 else None
                if sih_code_cell and f"SIH{target_id}" in sih_code_cell.get_text().strip():
                    submission_count = cells[15].get_text().strip()
                    print(f"✅ Found SIH{target_id} in row {i}")
                    print(f"✅ Submission count: {submission_count}")
                    print(f"✅ Row has {len(cells)} columns")
                    
                    # Show the relevant columns
                    print(f"Column 14 (SIH Code): '{cells[14].get_text().strip()}'")
                    print(f"Column 15 (Submissions): '{cells[15].get_text().strip()}'")
                    
                    try:
                        count_int = int(submission_count)
                        print(f"✅ Successfully converted to integer: {count_int}")
                        return count_int
                    except ValueError as e:
                        print(f"❌ Could not convert '{submission_count}' to integer: {e}")
                        
            except (IndexError, AttributeError) as e:
                continue
    
    print(f"❌ Could not find SIH{target_id}")
    return None

if __name__ == "__main__":
    test_fixed_parser()