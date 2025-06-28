import csv
import re
from collections import defaultdict

def extract_year_from_title(title):
    """Extract year from paper title"""
    # Look for year patterns like (2024), 2024, or year at the end
    year_patterns = [
        r'\((\d{4})\)',  # (2024)
        r'\s(\d{4})\s*$',  # 2024 at the end
        r'\s(\d{4})\s',  # 2024 in the middle
        r'(\d{4})\.',  # 2024.
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, title)
        if match:
            return match.group(1)
    
    return None

def detect_conference_from_title(title):
    """Detect conference from paper title"""
    title_lower = title.lower()
    
    # Conference patterns
    conference_patterns = [
        (r'cvpr\s*(\d{4})', 'CVPR'),
        (r'iclr\s*(\d{4})', 'ICLR'),
        (r'neurips\s*(\d{4})', 'NeurIPS'),
        (r'nips\s*(\d{4})', 'NeurIPS'),
        (r'iccv\s*(\d{4})', 'ICCV'),
        (r'eccv\s*(\d{4})', 'ECCV'),
        (r'acm\s*(\d{4})', 'ACM'),
        (r'ieee\s*(\d{4})', 'IEEE'),
        (r'icml\s*(\d{4})', 'ICML'),
        (r'icip\s*(\d{4})', 'ICIP'),
        (r'pakdd\s*(\d{4})', 'PAKDD'),
        (r'asiancon\s*(\d{4})', 'ASIANCON'),
        (r'visigrapp\s*(\d{4})', 'VISIGRAPP'),
    ]
    
    for pattern, conf_name in conference_patterns:
        match = re.search(pattern, title_lower)
        if match:
            return f"{conf_name} {match.group(1)}"
    
    # Check for conference names without years
    if any(conf in title_lower for conf in ['cvpr', 'iccv', 'eccv']):
        return 'CVPR/ICCV/ECCV'
    elif 'iclr' in title_lower:
        return 'ICLR'
    elif 'neurips' in title_lower or 'nips' in title_lower:
        return 'NeurIPS'
    elif 'icml' in title_lower:
        return 'ICML'
    elif 'acm' in title_lower:
        return 'ACM'
    elif 'ieee' in title_lower:
        return 'IEEE'
    
    return 'arXiv/Unknown'

def analyze_papers_csv(filename):
    """Analyze papers from CSV file"""
    papers = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                title = row['paper'].strip()
                if title:
                    year = extract_year_from_title(title)
                    conference = detect_conference_from_title(title)
                    
                    papers.append({
                        'title': title,
                        'year': year,
                        'conference': conference
                    })
    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []
    
    return papers

def generate_summary(papers):
    """Generate summary by year and conference"""
    by_year = defaultdict(list)
    by_conference = defaultdict(list)
    
    for paper in papers:
        year = paper.get('year', 'Unknown')
        conference = paper.get('conference', 'Unknown')
        
        by_year[year].append(paper)
        by_conference[conference].append(paper)
    
    return {
        'total_papers': len(papers),
        'by_year': dict(by_year),
        'by_conference': dict(by_conference)
    }

def print_summary(summary):
    """Print the summary"""
    print("\n" + "="*80)
    print("PAPERS AND CONFERENCE ANALYSIS SUMMARY")
    print("="*80)
    
    print(f"\nTotal papers analyzed: {summary['total_papers']}")
    
    # By year
    print("\n" + "-"*50)
    print("BREAKDOWN BY YEAR")
    print("-"*50)
    
    # Sort years (put 'Unknown' and None at the end)
    def sort_key(x):
        if x is None or x == 'Unknown':
            return '9999'
        return x
    
    sorted_years = sorted(summary['by_year'].keys(), key=sort_key)
    
    for year in sorted_years:
        papers = summary['by_year'][year]
        year_display = year if year is not None else 'Unknown'
        print(f"\n{year_display} ({len(papers)} papers):")
        for paper in papers:
            print(f"  • {paper['title'][:80]}...")
            print(f"    Conference: {paper['conference']}")
    
    # By conference
    print("\n" + "-"*50)
    print("BREAKDOWN BY CONFERENCE")
    print("-"*50)
    
    # Sort conferences by number of papers (descending)
    sorted_conferences = sorted(summary['by_conference'].items(), 
                               key=lambda x: len(x[1]), reverse=True)
    
    for conference, papers in sorted_conferences:
        print(f"\n{conference} ({len(papers)} papers):")
        for paper in papers:
            year_display = paper.get('year', 'Unknown') if paper.get('year') is not None else 'Unknown'
            print(f"  • {paper['title'][:80]}...")
            print(f"    Year: {year_display}")

def main():
    filename = 'papersandconference.csv'
    
    print(f"Analyzing papers from {filename}...")
    papers = analyze_papers_csv(filename)
    
    if papers:
        summary = generate_summary(papers)
        print_summary(summary)
        
        # Save results to JSON
        import json
        with open('papers_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'papers': papers,
                'summary': summary
            }, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed results saved to papers_analysis_results.json")
    else:
        print("No papers found or error occurred.")

if __name__ == "__main__":
    main() 