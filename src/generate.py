import yaml
import sys
from pathlib import Path
from typing import List, Dict, Any
from helper import (generate_year_options, generate_tag_filters, generate_paper_cards,
                    generate_category_options, compute_category_tags)
from utils import read_files, write_output
from template_engine import TemplateEngine
from datetime import datetime, date
import json

# Highlight set duplicated here for sorting consistency (keep in sync with helper.py, filters.js, state.js)
HIGHLIGHTED_CATEGORIES = {
    "Generative Design and Design Space Exploration",
    "Parametric, Computational and Algorithmic Design",
    "Performance-Driven Design",
    "3D Reconstruction",
    "Floor Plan Reconstruction and Parametrization",
    "Predictive Analytics and Performance Optimization",
    "Quality Control and Validation",
    "Digital Documentation and Archiving",
    "Predictive Conservation and Risk Assessment",
    "Virtual Reality Experiences and Education",
    "AI for Energy Performance Optimization",
    "Sustainable Buildings",
    "Smart Building Systems and IoT Integration",
    "AI-Powered Real Estate Valuation",
    "Virtual Property Tours and Marketing",
    "XRAI for AEC",
    "Occupant Behavior Analysis and Spatial Optimization",
    "Cross-Modal Intelligence and Multimodal Integration",
    "Review Paper", 
    "Dataset", 
    "Case Study", 
    "Tool/Library",
}

def _parse_date(entry: Dict[str, Any]) -> date:
    for key in ("publication_date", "pub_date", "date"):
        v = entry.get(key)
        if not v:
            continue
        fmts = ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%d-%m-%Y", "%Y-%m", "%Y")
        for f in fmts:
            try:
                return datetime.strptime(v, f).date()
            except Exception:
                continue
    # fallback to year
    y = entry.get("year")
    try:
        return date(int(y), 1, 1)
    except Exception:
        return date(1900, 1, 1)

def _authors_str(entry: Dict[str, Any]) -> str:
    a = entry.get("authors")
    if isinstance(a, list):
        return ", ".join(a)
    return a or ""

def sort_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Sorting: date (desc), year (desc implicit in date), authors asc, title asc
    def key(e):
        d = _parse_date(e)
        return (-d.toordinal(), _authors_str(e).lower(), e.get("title","").lower())
    return sorted(entries, key=key)

def generate_json_ld(entries: List[Dict[str, Any]]) -> str:
    """Generate Schema.org JSON-LD structured metadata for papers."""
    schema_list = []
    for entry in entries:
        authors = entry.get("authors", "")
        author_list = []
        if isinstance(authors, list):
            for a in authors:
                author_list.append({"@type": "Person", "name": a.strip()})
        elif isinstance(authors, str) and authors.strip():
            for a in authors.split(","):
                author_list.append({"@type": "Person", "name": a.strip()})
                
        pub_date = entry.get("publication_date")
        if pub_date:
            date_published = pub_date[:10]
        else:
            date_published = entry.get("year", "")
            
        desc = entry.get("abstract", "") or ""
        if len(desc) > 500:
            desc = desc[:500] + "..."
            
        article = {
            "@type": "ScholarlyArticle",
            "headline": entry.get("title", ""),
            "author": author_list,
            "datePublished": date_published,
            "description": desc,
            "url": entry.get("paper", "") or entry.get("paper_url", ""),
            "keywords": ", ".join(entry.get("tags", []))
        }
        schema_list.append(article)
        
    main_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "XRAI4AEC: Awesome XR & AI for AEC Research Papers Database",
        "description": "A curated collection of papers focused on XR+AI for AEC (XRAI4AEC) and related technologies such as BIM, (2D/3D) computer vision, computer graphics, LLMs, VLMS, GenAI, deep/machine learning and data science.",
        "url": "https://prakashknaikade.github.io/Awesome-XRAI-for-Architecture/",
        "about": schema_list
    }
    return json.dumps(main_schema, indent=2, ensure_ascii=False)

def generate_html(entries: List[Dict[str, Any]], output_file: str) -> None:
    """Generate optimized HTML page while preserving design."""
    base_dir = Path(__file__).parent

    # SORT entries before any downstream generation
    # entries = sort_entries(entries)

    css_files = ['static/css/base.css', 'static/css/components.css', 'static/css/responsive.css']
    js_files = [
        'static/js/state.js',
        'static/js/utils.js',
        'static/js/filters.js',
        'static/js/selection.js',
        'static/js/sharing.js',
        'static/js/navigation.js',
        'static/js/theme.js',
        'static/js/main.js'
    ]
    
    css_content = read_files(base_dir, css_files)
    js_content = read_files(base_dir, js_files)

    template = TemplateEngine(base_dir / 'templates/index.html')

    category_tags_map = compute_category_tags(entries)

    context = {
        'styles': '\n'.join(css_content),
        'scripts': '\n'.join(js_content),
        'year_options': generate_year_options(entries),
        # ensure category_options NOT duplicating All Categories (template holds the all option)
        'category_options': generate_category_options(entries),
        'tag_filters': '',  # initial tag filters populated client-side
        'paper_cards': generate_paper_cards(entries),
        'highlighted_tags_json': json.dumps(list(HIGHLIGHTED_CATEGORIES)),
        'category_tags_json': json.dumps(category_tags_map),
        'json_ld_schema': generate_json_ld(entries),
    }

    html = template.render(context)
    write_output(output_file, html)

def _safe_int(v):
    try:
        return int(str(v).strip())
    except Exception:
        return None

def _safe_list(v):
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return []

def _analytics_record(paper: dict) -> dict:
    return {
        "id": str(paper.get("id", "")).strip(),
        "title": str(paper.get("title", "")).strip(),
        "year": _safe_int(paper.get("year")),
        "primary_category": str(paper.get("primary_category", "Uncategorized")).strip() or "Uncategorized",
        "tags": _safe_list(paper.get("tags")),
        "authors": str(paper.get("authors", "")).strip(),
    }

def generate_analytics_html(entries: list[dict], output_file: str) -> None:
    base_dir = Path(__file__).resolve().parent
    template = TemplateEngine(base_dir / "templates" / "analytics.html")

    analytics_rows = [_analytics_record(e) for e in entries]

    context = {
        # embedded JS literal; no extra data file needed
        "analytics_data_json": json.dumps(analytics_rows, ensure_ascii=False),
    }

    html = template.render(context)
    write_output(output_file, html)

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate.py <input_yaml> <output_html>")
        sys.exit(1)

    try:
        input_yaml = Path(sys.argv[1])
        output_html = Path(sys.argv[2])

        with input_yaml.open('r', encoding='utf-8') as f:
            entries = yaml.safe_load(f) or []

        entries = sort_entries(entries)

        # index page
        generate_html(entries, str(output_html))
        print(f"Successfully generated {output_html}")

        # analytics page (same folder as index output)
        analytics_out = output_html.parent / "analytics.html"
        generate_analytics_html(entries, str(analytics_out))
        print(f"Generated: {analytics_out}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()