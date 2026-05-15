import datetime
from dataclasses import fields
from typing import List, Dict, Any
from pathlib import Path
from paper_schema import Paper
from paper_generator import PaperCardGenerator
from collections import defaultdict

card_generator = PaperCardGenerator(Path(__file__).parent / 'templates')

# Added highlighted tag set (keep sync with filters.js & state.js (and generate_test.py if needed))
HIGHLIGHTED_TAGS = {
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

PRIMARY_CATEGORY_ORDER = [
    "AI-Driven Design and Generative Architecture",
    "Reality Capture and Digital Twins",
    "Computational BIM and Intelligent Operations",
    "Heritage Conservation and Cultural Preservation",
    "Sustainability and Environmental Performance",
    "Sustainable Real Estate Valuation and Economics",
    "Human-Computer Interaction and Human-Building Interaction",
]

def generate_year_options(entries: List[Dict[str, Any]]) -> str:
    """Generate HTML for year filter options."""
    years = sorted({str(e.get("year", "")) for e in entries if e.get("year")}, reverse=True)
    return "\n".join(f'<option value="{y}">{y}</option>' for y in years)

def generate_tag_filters(entries: List[Dict[str, Any]]) -> str:
    """Generate HTML for tag filters with highlight class."""
    all_tags = sorted(set(tag for entry in entries for tag in entry["tags"]))
    filtered_tags = [t for t in all_tags if not t.startswith("Year ")]
    def is_highlight(t: str) -> bool:
        # normalize & vs 'and'
        norm = t.replace("&", "and")
        return t in HIGHLIGHTED_TAGS or norm in {h.replace("&","and") for h in HIGHLIGHTED_TAGS}
    ordered = sorted(filtered_tags, key=lambda x: (0 if is_highlight(x) else 1, x.lower()))
    return "\n".join(
        f'<div class="tag-filter{" highlighted" if is_highlight(t) else ""}" data-tag="{t}">{t}</div>'
        for t in ordered
    )

def format_publication_date(date_str: str, date_source: str) -> str:
    """Format publication date for display."""
    if not date_str:
        return ""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        formatted_date = date.strftime("%B %d, %Y")
        source_indicator = " (est.)" if date_source == 'estimated' else ""
        return f"{formatted_date}{source_indicator}"
    except ValueError:
        return date_str
    

def generate_category_options(entries: List[Dict[str, Any]]) -> str:
    """Return only the real categories as <option> list.
       The template already includes the 'All Categories' option."""
    seen = {}
    for e in entries:
        cat = e.get("primary_category")
        if cat:
            seen.setdefault(cat, 0)
            seen[cat] += 1

    ordered = [c for c in PRIMARY_CATEGORY_ORDER if c in seen]
    ordered += sorted(cat for cat in seen if cat not in PRIMARY_CATEGORY_ORDER)

    return "\n".join(
        f'<option value="{cat}">{cat}</option>'
        for cat in ordered
    )

def generate_paper_cards(entries: List[Dict[str, Any]]) -> str:
    """Generate HTML for paper cards using the Paper model and card generator."""
    cards = []
    allowed = {f.name for f in fields(Paper)}
    for e in entries:
        clean = {k: v for k, v in e.items() if k in allowed}
        # Ensure primary_category is present for filtering
        if not clean.get("primary_category"):
            clean["primary_category"] = "Uncategorized"
        # Authors normalization
        if isinstance(clean.get("authors"), str):
            clean["authors"] = [a.strip() for a in clean["authors"].split(",") if a.strip()]
        p = Paper(**clean)
        cards.append(card_generator.generate_card(p, highlighted_tags=HIGHLIGHTED_TAGS))
    return "\n".join(cards)

def compute_category_tags(entries: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Build mapping of category -> tags (and 'all') for fast client rebuild."""
    from collections import defaultdict
    mapping = defaultdict(set)
    for e in entries:
        cat = (e.get("primary_category") or "Uncategorized").strip()
        for t in (e.get("tags") or []):
            mapping["all"].add(t)
            mapping[cat].add(t)
    return {k: sorted(v) for k,v in mapping.items()}