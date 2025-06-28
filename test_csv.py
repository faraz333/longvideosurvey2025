from paper_analyzer import PaperAnalyzer

def test_csv_reading():
    analyzer = PaperAnalyzer()
    
    print("Testing CSV file reading...")
    results = analyzer.analyze_papers_from_file('sample_papers.csv', title_column='Title')
    
    if results:
        summary = analyzer.generate_summary()
        analyzer.print_summary(summary)
        analyzer.save_results('csv_analysis_results.json')
    else:
        print("No papers were successfully analyzed from CSV.")

if __name__ == "__main__":
    test_csv_reading() 