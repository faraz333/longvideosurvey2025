import requests
import time
import json
import re
import csv
from collections import defaultdict
from urllib.parse import quote_plus
import os

class PaperAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.results = []
        
    def search_paper_info(self, paper_title):
        """Search for paper information using Google Scholar or arXiv"""
        try:
            # Try arXiv first
            arxiv_result = self.search_arxiv(paper_title)
            if arxiv_result:
                return arxiv_result
            
            # Try Google Scholar
            scholar_result = self.search_google_scholar(paper_title)
            if scholar_result:
                return scholar_result
            
            return None
        except Exception as e:
            print(f"Error searching for '{paper_title}': {e}")
            return None
    
    def search_arxiv(self, paper_title):
        """Search arXiv for the paper"""
        try:
            # Clean title for search
            search_query = re.sub(r'[^\w\s]', '', paper_title.lower())
            search_query = ' '.join(search_query.split()[:10])  # Use first 10 words
            
            # arXiv API endpoint
            url = f"http://export.arxiv.org/api/query?search_query=all:{quote_plus(search_query)}&start=0&max_results=5"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # Parse XML response (simplified)
                content = response.text.lower()
                
                # Look for year and conference info
                year_match = re.search(r'(\d{4})', content)
                year = year_match.group(1) if year_match else None
                
                # Look for common conference patterns
                conferences = []
                conference_patterns = [
                    r'cvpr\s*(\d{4})', r'iclr\s*(\d{4})', r'neurips\s*(\d{4})', 
                    r'iccv\s*(\d{4})', r'eccv\s*(\d{4})', r'acm\s*(\d{4})',
                    r'ieee\s*(\d{4})', r'icml\s*(\d{4})'
                ]
                
                for pattern in conference_patterns:
                    match = re.search(pattern, content)
                    if match:
                        conferences.append(match.group(0).upper())
                
                if year or conferences:
                    return {
                        'title': paper_title,
                        'year': year,
                        'conference': conferences[0] if conferences else 'arXiv',
                        'url': f"https://arxiv.org/search/?query={quote_plus(search_query)}",
                        'source': 'arXiv'
                    }
            
            return None
        except Exception as e:
            print(f"Error searching arXiv for '{paper_title}': {e}")
            return None
    
    def search_google_scholar(self, paper_title):
        """Search Google Scholar for the paper (simplified)"""
        try:
            # This is a simplified version - in practice you'd need to parse HTML
            # For now, we'll extract year from title and make educated guesses
            year_match = re.search(r'(\d{4})', paper_title)
            year = year_match.group(1) if year_match else None
            
            # Look for conference indicators in title
            title_lower = paper_title.lower()
            conference = None
            
            if any(conf in title_lower for conf in ['cvpr', 'iccv', 'eccv']):
                conference = 'CVPR/ICCV/ECCV'
            elif 'iclr' in title_lower:
                conference = 'ICLR'
            elif 'neurips' in title_lower or 'nips' in title_lower:
                conference = 'NeurIPS'
            elif 'icml' in title_lower:
                conference = 'ICML'
            elif 'acm' in title_lower:
                conference = 'ACM'
            elif 'ieee' in title_lower:
                conference = 'IEEE'
            
            if year or conference:
                return {
                    'title': paper_title,
                    'year': year,
                    'conference': conference or 'Unknown',
                    'url': f"https://scholar.google.com/scholar?q={quote_plus(paper_title)}",
                    'source': 'Google Scholar'
                }
            
            return None
        except Exception as e:
            print(f"Error searching Google Scholar for '{paper_title}': {e}")
            return None
    
    def read_text_file(self, filename):
        """Read paper names from a text file"""
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    
    def read_csv_file(self, filename, title_column=None):
        """Read paper names from a CSV file"""
        paper_titles = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # If title_column is specified, use it
                if title_column and reader.fieldnames and title_column in reader.fieldnames:
                    for row in reader:
                        if row[title_column].strip():
                            paper_titles.append(row[title_column].strip())
                else:
                    # Try to find a column that might contain titles
                    # Look for common column names
                    possible_title_columns = ['title', 'paper', 'name', 'paper_title', 'Title', 'Paper', 'Name']
                    
                    title_col = None
                    if reader.fieldnames:
                        for col in possible_title_columns:
                            if col in reader.fieldnames:
                                title_col = col
                                break
                    
                    # If no common name found, use the first column
                    if not title_col and reader.fieldnames:
                        title_col = reader.fieldnames[0]
                    
                    if title_col:
                        for row in reader:
                            if row[title_col].strip():
                                paper_titles.append(row[title_col].strip())
                    else:
                        print("No suitable column found for paper titles")
                        return []
                        
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []
        
        return paper_titles
    
    def detect_file_type(self, filename):
        """Detect if file is CSV or text based on extension and content"""
        if filename.lower().endswith('.csv'):
            return 'csv'
        elif filename.lower().endswith('.txt'):
            return 'text'
        else:
            # Try to detect by reading first few lines
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if ',' in first_line and len(first_line.split(',')) > 1:
                        return 'csv'
                    else:
                        return 'text'
            except:
                return 'text'  # Default to text
    
    def analyze_papers_from_file(self, filename, title_column=None):
        """Read paper names from file (CSV or text) and analyze them"""
        if not os.path.exists(filename):
            print(f"File {filename} not found!")
            return
        
        file_type = self.detect_file_type(filename)
        print(f"Detected file type: {file_type}")
        
        if file_type == 'csv':
            paper_titles = self.read_csv_file(filename, title_column)
        else:
            paper_titles = self.read_text_file(filename)
        
        print(f"Found {len(paper_titles)} papers to analyze...")
        
        for i, title in enumerate(paper_titles, 1):
            print(f"Analyzing {i}/{len(paper_titles)}: {title[:50]}...")
            
            result = self.search_paper_info(title)
            if result:
                self.results.append(result)
            
            # Be nice to the servers
            time.sleep(1)
        
        return self.results
    
    def generate_summary(self):
        """Generate summary by year and conference"""
        if not self.results:
            print("No results to summarize!")
            return
        
        # Group by year
        by_year = defaultdict(list)
        for paper in self.results:
            year = paper.get('year', 'Unknown')
            by_year[year].append(paper)
        
        # Group by conference
        by_conference = defaultdict(list)
        for paper in self.results:
            conference = paper.get('conference', 'Unknown')
            by_conference[conference].append(paper)
        
        # Generate summary
        summary = {
            'total_papers': len(self.results),
            'by_year': dict(by_year),
            'by_conference': dict(by_conference)
        }
        
        return summary
    
    def print_summary(self, summary):
        """Print the summary in a readable format"""
        print("\n" + "="*60)
        print("PAPER ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\nTotal papers analyzed: {summary['total_papers']}")
        
        # By year
        print("\n" + "-"*40)
        print("BREAKDOWN BY YEAR")
        print("-"*40)
        for year in sorted(summary['by_year'].keys(), key=lambda x: x if x != 'Unknown' else '9999'):
            papers = summary['by_year'][year]
            print(f"\n{year} ({len(papers)} papers):")
            for paper in papers:
                print(f"  • {paper['title']}")
                print(f"    Conference: {paper['conference']} | Source: {paper['source']}")
        
        # By conference
        print("\n" + "-"*40)
        print("BREAKDOWN BY CONFERENCE")
        print("-"*40)
        for conference in sorted(summary['by_conference'].keys()):
            papers = summary['by_conference'][conference]
            print(f"\n{conference} ({len(papers)} papers):")
            for paper in papers:
                print(f"  • {paper['title']}")
                print(f"    Year: {paper.get('year', 'Unknown')} | Source: {paper['source']}")
    
    def save_results(self, filename='paper_analysis_results.json'):
        """Save results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {filename}")

def main():
    analyzer = PaperAnalyzer()
    
    # Analyze papers from conference.txt (or any file)
    # You can specify a title column for CSV files like this:
    # results = analyzer.analyze_papers_from_file('papers.csv', title_column='Title')
    results = analyzer.analyze_papers_from_file('conference.txt')
    
    if results:
        summary = analyzer.generate_summary()
        analyzer.print_summary(summary)
        analyzer.save_results()
    else:
        print("No papers were successfully analyzed.")

if __name__ == "__main__":
    main() 