from pypdf import PdfReader
import re

def extract_pdf_titles(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            # Split by common patterns that indicate paper entries
            # Look for patterns like: "Title 20xx" or "Title https://"
            patterns = [
                r'([A-Z][^.]*?)\s+(19|20)\d{2}',  # Title followed by year
                r'([A-Z][^.]*?)\s+https?://',     # Title followed by URL
                r'([A-Z][^.]*?)\s+\(20\d{2}\)',   # Title followed by (year)
            ]
            
            titles = []
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if isinstance(match, tuple):
                        title = match[0].strip()
                    else:
                        title = match.strip()
                    
                    # Clean up the title
                    title = re.sub(r'\s+', ' ', title)  # Remove extra spaces
                    title = title.strip()
                    
                    # Filter out very short titles and common non-titles
                    if (len(title.split()) >= 3 and 
                        not title.lower().startswith('paper online-link') and
                        not title.lower().startswith('peer reviewed') and
                        not title.lower().startswith('ieee') and
                        not title.lower().startswith('cvpr') and
                        not title.lower().startswith('iclr') and
                        not title.lower().startswith('neurips') and
                        not title.lower().startswith('acm') and
                        not title.lower().startswith('icml') and
                        not title.lower().startswith('eccv') and
                        not title.lower().startswith('icip') and
                        not title.lower().startswith('pakdd') and
                        not title.lower().startswith('asiancon') and
                        not title.lower().startswith('visigrapp')):
                        titles.append(title)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_titles = []
            for title in titles:
                if title not in seen:
                    seen.add(title)
                    unique_titles.append(title)
            
            return unique_titles
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return []

if __name__ == "__main__":
    pdf_path = "Video-generation - papers.pdf"
    titles = extract_pdf_titles(pdf_path)
    if titles:
        with open("conference.txt", "w") as f:
            for title in titles:
                f.write(title + "\n")
        print(f"Extracted {len(titles)} paper titles to conference.txt")
        print("First 10 titles:")
        for i, title in enumerate(titles[:10]):
            print(f"{i+1}: {title}")
    else:
        print("No titles extracted from PDF") 