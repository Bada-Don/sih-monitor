import requests
from bs4 import BeautifulSoup
import json

def debug_html_structure():
    """Debug the HTML structure to find our target problem statement"""
    print("🔍 Debugging HTML Structure...")
    
    # Fetch the page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get("https://sih.gov.in/sih2025PS", headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save HTML to file for inspection
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("✅ Saved full HTML to 'debug_page.html'")
        
        # Look for any mention of 25057
        print(f"\n🔍 Searching for '25057' in page...")
        if '25057' in response.text:
            print("✅ Found '25057' in the page!")
            
            # Find the context around 25057
            lines = response.text.split('\n')
            for i, line in enumerate(lines):
                if '25057' in line:
                    print(f"\nLine {i}: {line.strip()}")
                    # Show surrounding lines for context
                    for j in range(max(0, i-2), min(len(lines), i+3)):
                        if j != i:
                            print(f"Line {j}: {lines[j].strip()}")
        else:
            print("❌ '25057' not found in the page!")
            print("🔍 Let's look for problem statements...")
            
        # Analyze table structure
        print("\n📊 Analyzing table structure...")
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"\nTable {table_idx + 1}: {len(rows)} rows")
            
            # Look at first few rows to understand structure
            for row_idx, row in enumerate(rows[:5]):
                cells = row.find_all(['th', 'td'])
                cell_texts = [cell.get_text().strip()[:50] for cell in cells]
                print(f"  Row {row_idx}: {cell_texts}")
        
        # Look for SIH codes pattern
        print("\n🔍 Looking for SIH code patterns...")
        sih_codes = soup.find_all(text=lambda text: text and 'SIH' in text and text.strip().startswith('SIH'))
        print(f"Found {len(sih_codes)} SIH codes:")
        for code in sih_codes[:10]:  # Show first 10
            print(f"  - {code.strip()}")
        
        # Look for modals
        print("\n🔍 Looking for modals...")
        modals = soup.find_all('div', class_='modal')
        print(f"Found {len(modals)} modals")
        
        # Look for any number that might be our problem ID
        print("\n🔍 Looking for numbers that might be problem IDs...")
        import re
        numbers = re.findall(r'\b\d{5}\b', response.text)  # 5-digit numbers
        unique_numbers = list(set(numbers))[:20]  # First 20 unique numbers
        print(f"Found 5-digit numbers: {unique_numbers}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_specific_search_methods():
    """Test different ways to find problem statements"""
    print("\n🧪 Testing Different Search Methods...")
    
    try:
        with open('debug_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("❌ Run debug_html_structure() first!")
        return
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Method 1: Look for rows with submission counts
    print("\n1️⃣ Looking for rows with numeric submission counts...")
    rows = soup.find_all('tr')
    for i, row in enumerate(rows):
        cells = row.find_all('td')
        if len(cells) >= 6:
            # Check if last few cells contain numbers (submission counts)
            for j in range(-3, 0):  # Check last 3 cells
                try:
                    cell_text = cells[j].get_text().strip()
                    if cell_text.isdigit():
                        print(f"Row {i}: Found numeric cell '{cell_text}' in position {j}")
                        # Show the whole row
                        row_texts = [cell.get_text().strip()[:30] for cell in cells]
                        print(f"  Full row: {row_texts}")
                        break
                except:
                    continue
    
    # Method 2: Look for the specific title
    print("\n2️⃣ Looking for Legal Metrology title...")
    title_search = "Automated Compliance Checker for Legal Metrology"
    if title_search in html_content:
        print("✅ Found the title!")
        # Find the context
        soup_text = soup.get_text()
        if title_search in soup_text:
            # Find the element containing this text
            elements = soup.find_all(text=lambda text: text and title_search in text)
            for element in elements:
                parent = element.parent
                print(f"Found in: {parent.name}")
                # Try to find the row containing this
                row = parent.find_parent('tr')
                if row:
                    cells = row.find_all('td')
                    row_texts = [cell.get_text().strip()[:40] for cell in cells]
                    print(f"  Row data: {row_texts}")
    
    # Method 3: Search for any problem with submission count
    print("\n3️⃣ Finding ANY problem with submission data...")
    for i, row in enumerate(rows[:20]):  # Check first 20 rows
        cells = row.find_all('td')
        if len(cells) >= 5:
            row_texts = [cell.get_text().strip() for cell in cells]
            # Look for SIH codes
            sih_codes = [text for text in row_texts if text.startswith('SIH')]
            if sih_codes:
                print(f"Row {i}: {sih_codes[0]} -> {row_texts}")

def suggest_config_fix():
    """Suggest a fix for the config based on what we found"""
    print("\n💡 Suggested Fixes:")
    print("1. Check if the problem statement ID has changed")
    print("2. Maybe the format is different (like 'SIH25057' instead of '25057')")
    print("3. The problem might not be published yet")
    print("4. Try a different problem ID that exists on the page")
    
    # Try to suggest an alternative ID
    try:
        with open('debug_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        import re
        sih_codes = re.findall(r'SIH(\d{5})', html_content)
        if sih_codes:
            print(f"\n🎯 Found these problem IDs you could try instead:")
            for code in list(set(sih_codes))[:10]:
                print(f"  - {code}")
    except:
        pass

def main():
    print("🚀 SIH HTML Structure Debug Tool")
    print("=" * 50)
    
    # Step 1: Fetch and analyze HTML
    if debug_html_structure():
        # Step 2: Test different search methods
        test_specific_search_methods()
        
        # Step 3: Suggest fixes
        suggest_config_fix()
    
    print("\n📋 Next Steps:")
    print("1. Check 'debug_page.html' file for the full HTML")
    print("2. Update config.json with a valid problem ID from the suggestions above")
    print("3. Or run the script with a different target_problem_id")

if __name__ == "__main__":
    main()