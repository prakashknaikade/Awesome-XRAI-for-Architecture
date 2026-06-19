import yaml
from datetime import datetime, timedelta
from collections import defaultdict
import re

PRIMARY_CATEGORY_ORDER = [
    "AI-Driven Design and Generative Architecture",
    "Reality Capture and Digital Twins",
    "Computational BIM and Intelligent Operations",
    "Heritage Conservation and Cultural Preservation",
    "Sustainability and Environmental Performance",
    "Sustainable Real Estate Valuation and Economics",
    "Human-Computer Interaction and Human-Building Interaction",
]

class ReadmeGenerator:
    def __init__(self, yaml_file='awesome_xrai_architecture_papers.yaml', readme_file='README.md'):
        self.yaml_file = yaml_file
        self.readme_file = readme_file
        
    def load_papers(self):
        """Load papers from YAML file - handle both flat list and categories structure"""
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Handle different YAML structures
            if isinstance(data, list):
                # Flat list structure (current YAML editor format)
                return data
            elif isinstance(data, dict) and 'categories' in data:
                # Categories structure
                all_papers = []
                for category in data.get('categories', []):
                    papers = category.get('papers', [])
                    all_papers.extend(papers)
                return all_papers
            else:
                return []
                
        except FileNotFoundError:
            print(f"YAML file {self.yaml_file} not found!")
            return []
    
    def organize_papers_by_category_and_year(self, papers):
        """Organize papers by primary category and year"""
        organized = defaultdict(lambda: defaultdict(list))
        
        for paper in papers:
            # Get primary category (fallback to a default if not specified)
            primary_category = paper.get('primary_category', 'XR in Architectural Design')
            year = paper.get('year', 'Unknown Year')
            
            organized[primary_category][year].append(paper)
        
        return organized
    
    def format_links(self, paper):
        """Generate formatted links for a paper"""
        links = []
        
        # Handle different paper URL field names
        if paper.get('paper'):
            if paper['paper'].startswith('http'):
                links.append(f"[📄 Paper]({paper['paper']})")
            else:
                links.append(f"[📄 Paper](https://arxiv.org/abs/{paper['paper']})")
        elif paper.get('arxiv'):
            if paper['arxiv'].startswith('http'):
                links.append(f"[📄 Paper]({paper['arxiv']})")
            else:
                links.append(f"[📄 Paper](https://arxiv.org/abs/{paper['arxiv']})")
        elif paper.get('paper_url'):
            links.append(f"[📄 Paper]({paper['paper_url']})")
        
        if paper.get('project_page'):
            links.append(f"[🌐 Project Page]({paper['project_page']})")
        elif paper.get('project'):
            links.append(f"[🌐 Project Page]({paper['project']})")
        
        if paper.get('code'):
            if paper['code'].startswith('http'):
                links.append(f"[💻 Code]({paper['code']})")
            else:
                links.append(f"[💻 Code](https://github.com/{paper['code']})")
        elif paper.get('github'):
            if paper['github'].startswith('http'):
                links.append(f"[💻 Code]({paper['github']})")
            else:
                links.append(f"[💻 Code](https://github.com/{paper['github']})")
        
        if paper.get('video'):
            links.append(f"[🎥 Video]({paper['video']})")
        
        if paper.get('demo'):
            links.append(f"[🔗 Demo]({paper['demo']})")
        
        return " | ".join(links) if links else ""
    
    def format_paper_entry(self, paper, index):
        """Format a single paper entry with proper spacing"""
        title = paper.get('title', 'Unknown Title')
        authors = paper.get('authors', 'Unknown Authors')
        venue = paper.get('venue', '')
        abstract = paper.get('abstract', 'No abstract available.')
        
        # Handle authors - convert list to string if needed
        if isinstance(authors, list):
            authors = ", ".join(authors)
        
        # Add venue to title if available
        if venue:
            title_with_venue = f"[{venue}] {title}"
        else:
            title_with_venue = title
        
        # Format the entry with proper spacing
        entry = f"### {index}. {title_with_venue}\n\n"
        entry += f"**Authors**: {authors}\n\n"
        entry += "<details>\n"
        entry += "<summary><b>Abstract</b></summary>\n\n"
        entry += f"{abstract.strip()}\n\n"  # Fixed: Added proper newlines
        entry += "</details>\n\n"
        
        # Add links with proper spacing
        links = self.format_links(paper)
        if links:
            entry += f"**Links**: {links}\n\n"
        
        return entry
    
    def generate_papers_section(self):
        """Generate the papers section of README with proper formatting"""
        papers = self.load_papers()
        if not papers:
            return "# List of Papers\n\n*No papers found.*\n\n"
        
        organized = self.organize_papers_by_category_and_year(papers)
        
        papers_section = "# List of Papers\n\n"
        
        # Sort categories alphabetically
        for category in PRIMARY_CATEGORY_ORDER:
            if category not in organized:
                print(f"⚠️ Warning: Category '{category}' not found in papers data. Skipping this category.")
                continue
            papers_section += f"## {category}\n\n"
            
            # Sort years in descending order (newest first)
            years = sorted(organized[category].keys(), reverse=True)
            
            for year in years:
                papers_section += f"### {year}\n\n"
                
                # Sort papers by title for consistency
                papers_in_year = sorted(organized[category][year], key=lambda p: p.get('title', ''))
                
                for i, paper in enumerate(papers_in_year, 1):
                    papers_section += self.format_paper_entry(paper, i)
        
        return papers_section
    
    def generate_changelog(self):
        """Generate changelog with proper formatting"""
        papers = self.load_papers()
        if not papers:
            return "## Changelog\n\n*No papers found.*\n\n"
        
        changelog = "## Changelog\n\n"
        
        # Group papers by date they were added
        papers_by_date = defaultdict(list)
        
        for paper in papers:
            # Try to get the date when the paper was added
            added_date = None
            
            # Check different date fields that might indicate when paper was added
            if paper.get('added_date'):
                # If there's an explicit added_date field
                try:
                    added_date = datetime.fromisoformat(paper['added_date'].replace('Z', '+00:00')).date()
                except:
                    pass
            elif paper.get('publication_date'):
                # Use publication date as fallback
                try:
                    pub_date = paper['publication_date']
                    if isinstance(pub_date, str):
                        # Handle different date formats
                        if 'T' in pub_date:
                            added_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00')).date()
                        else:
                            added_date = datetime.strptime(pub_date, '%Y-%m-%d').date()
                    elif isinstance(pub_date, datetime):
                        added_date = pub_date.date()
                except:
                    pass
            
            # If no date found, use current date (for very recent additions)
            if not added_date:
                added_date = datetime.now().date()
            
            papers_by_date[added_date].append(paper)
        
        # Sort dates in descending order (newest first)
        sorted_dates = sorted(papers_by_date.keys(), reverse=True)
        
        # Only show papers from last 60 days
        cutoff_date = datetime.now().date() - timedelta(days=60)
        recent_dates = [date for date in sorted_dates if date >= cutoff_date]
        
        if recent_dates:
            changelog += "*Recent additions (last 60 days):*\n\n"
            
            for date in recent_dates:
                papers_on_date = papers_by_date[date]
                
                # Format date
                formatted_date = date.strftime("%B %d, %Y")  # e.g., "January 15, 2025"
                changelog += f"**{formatted_date}**\n\n"
                
                # Group papers by primary category for this date
                papers_by_category = defaultdict(list)
                for paper in papers_on_date:
                    primary_category = paper.get('primary_category', 'Uncategorized')
                    papers_by_category[primary_category].append(paper)
                
                # List papers by category
                for category, category_papers in papers_by_category.items():
                    for paper in category_papers:
                        title = paper.get('title', 'Unknown Title')
                        # Skip empty titles (from manual entries not yet filled)
                        if title and title.strip() and title != 'Unknown Title':
                            changelog += f"- {title} → *{category}*\n"
                
                changelog += "\n"
        else:
            changelog += "*No recent additions in the last 60 days.*\n\n"

        return changelog
    
    def extract_readme_sections(self):
        """Extract different sections of the existing README, properly handling Credits"""
        try:
            with open(self.readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"README file {self.readme_file} not found!")
            return "", ""
        
        # Find section boundaries
        changelog_start = content.find('## Changelog')
        papers_start = content.find('# List of Papers')
        
        # Find the FIRST occurrence of Credits (there might be duplicates)
        credits_matches = []
        start_pos = 0
        while True:
            credits_pos = content.find('## Credits', start_pos)
            if credits_pos == -1:
                break
            credits_matches.append(credits_pos)
            start_pos = credits_pos + 1
        
        # Use the first Credits section found
        credits_start = credits_matches[0] if credits_matches else -1
        
        # Extract header section (everything before changelog)
        if changelog_start != -1:
            header_content = content[:changelog_start].rstrip() + "\n\n"
        elif papers_start != -1:
            header_content = content[:papers_start].rstrip() + "\n\n"
        elif credits_start != -1:
            header_content = content[:credits_start].rstrip() + "\n\n"
        else:
            header_content = content
        
        # Extract credits section (everything from first Credits to end, removing any duplicates)
        if credits_start != -1:
            credits_section = content[credits_start:]
            
            # If there are multiple Credits sections, only take the first one
            if len(credits_matches) > 1:
                next_credits = credits_section.find('## Credits', 1)
                if next_credits != -1:
                    credits_section = credits_section[:next_credits]
            
            # Clean up the credits section
            credits_content = "\n\n## Credits\n\n" + credits_section.split('## Credits', 1)[1].strip() + "\n"
        else:
            # Default credits section if not found
            credits_content = "\n\n## Credits\n\nMost of the idea and code is adopted from MrNeRF's [awesome-3D-gaussian-splatting](https://github.com/MrNeRF/awesome-3D-gaussian-splatting) repo.\n"
        
        return header_content, credits_content
    
    def generate_full_readme(self):
        """Generate complete README preserving header and credits sections"""
        # Extract existing sections
        header_content, credits_content = self.extract_readme_sections()
        
        # Generate new dynamic content
        changelog = self.generate_changelog()
        papers_section = self.generate_papers_section()
        
        # Combine everything with proper spacing
        full_readme = (
            header_content +
            changelog +
            papers_section.rstrip() + 
            credits_content
        )
        
        return full_readme
    
    def save_readme(self):
        """Save the generated README"""
        readme_content = self.generate_full_readme()
        
        with open(self.readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        papers = self.load_papers()
        total_papers = len(papers)
        categories = set(paper.get('primary_category', 'Unknown') for paper in papers)
        
        print(f"✅ README.md updated successfully!")
        print(f"📊 Statistics:")
        print(f"   - Total papers: {total_papers}")
        print(f"   - Categories: {len(categories)}")
        print(f"   - Categories list: {', '.join(sorted(categories))}")
       
def main():
    generator = ReadmeGenerator()
    generator.save_readme()

if __name__ == "__main__":
    main()