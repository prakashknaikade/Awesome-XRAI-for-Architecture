from pathlib import Path
from typing import List
from datetime import datetime, date
import json

from paper_schema import Paper
from template_engine import TemplateEngine

class PaperCardGenerator:
    """Generates HTML for paper cards using templates."""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.template = TemplateEngine(templates_dir / 'paper_card.html')
        self.fallback_url = "None"

    def _generate_link(self, url: str, icon: str, text: str, emoji: str = "") -> str:
        """Generate HTML for a paper link with icon and emoji."""
        if not url or str(url).lower() == 'none':
            return ""
        return (f'<a href="{url}" class="paper-link" target="_blank" rel="noopener">'
                f'{emoji} {text}</a>')

    def _generate_links(self, paper: Paper) -> str:
        """Generate HTML for all paper links in specified order."""
        links = []
        if getattr(paper, "paper", None) and paper.paper.lower() != 'none':
            links.append(self._generate_link(paper.paper, "file-alt", "Paper", "📄"))
        if getattr(paper, "project_page", None) and paper.project_page.lower() != 'none':
            links.append(self._generate_link(paper.project_page, "globe", "Project", "🌐"))
        if getattr(paper, "code", None) and paper.code.lower() != 'none':
            links.append(self._generate_link(paper.code, "code", "Code", "💻"))
        if getattr(paper, "video", None) and paper.video.lower() != 'none':
            links.append(self._generate_link(paper.video, "video", "Video", "🎥"))
        if getattr(paper, "abstract", None) and paper.abstract and paper.abstract.lower() != 'none':
            links.append('<button class="abstract-toggle" onclick="toggleAbstract(this)">📖 Show Abstract</button>')
        if getattr(paper, "id", None):
            links.append(f'<button class="share-paper-btn" onclick="copyPaperLink(event, \'{paper.id}\')" title="Copy direct link to clipboard">🔗 Share</button>')
        if getattr(paper, "abstract", None) and paper.abstract and paper.abstract.lower() != 'none':
            links.append(f'<div class="paper-abstract">{paper.abstract}</div>')
        return "\n".join(links)

    # Back-compat alias used by older code
    _build_links_html = _generate_links

    def _parse_date(self, paper: Paper) -> date:
        for attr in ("publication_date", "pub_date", "date"):
            v = getattr(paper, attr, None)
            if not v:
                continue
            for fmt in ("%Y-%m-%d","%Y/%m/%d","%Y.%m.%d","%d-%m-%Y","%Y-%m","%Y"):
                try:
                    return datetime.strptime(v, fmt).date()
                except Exception:
                    continue
        try:
            return date(int(getattr(paper, "year", 0)), 1, 1)
        except Exception:
            return date(1900,1,1)

    def _authors_str(self, paper: Paper) -> str:
        a = getattr(paper, "authors", "")
        if isinstance(a, list):
            return ", ".join(a)
        return a or ""

    def _replace_placeholders(self, html: str, mapping: dict) -> str:
        """Replace both $key and ${key} placeholders in the per-card template."""
        for k, v in mapping.items():
            html = html.replace(f"${k}", v)
            html = html.replace(f"${{{k}}}", v)
        return html

    def generate_card(self, paper: Paper, highlighted_tags=None) -> str:
        highlighted_tags = highlighted_tags or set()
        norm_highlight = {h.replace("&","and") for h in highlighted_tags}

        tag_spans = []
        for t in getattr(paper, "tags", []):
            is_h = (t in highlighted_tags) or (t.replace("&","and") in norm_highlight)
            tag_spans.append(f'<span class="paper-tag{" highlighted" if is_h else ""}">{t}</span>')
        tags_html = "".join(tag_spans)

        tpl_path = self.templates_dir / "paper_card.html"
        content = tpl_path.read_text(encoding="utf-8")

        authors_render = self._authors_str(paper)
        pub_date = (getattr(paper, "publication_date", "") or
                    getattr(paper, "pub_date", "") or
                    getattr(paper, "date", ""))

        mapping = {
            "id": getattr(paper, "id", ""),
            "title": getattr(paper, "title", ""),
            "authors": authors_render,
            "year": str(getattr(paper, "year", "")),
            "primary_category": getattr(paper, "primary_category", None) or "Uncategorized",
            "tags_json": json.dumps(getattr(paper, "tags", [])),
            "tags_html": tags_html,
            "links_html": self._generate_links(paper),
            "thumbnail": getattr(paper, "thumbnail", None) or "assets/thumbnails/placeholder.jpg",
            "fallback_url": getattr(paper, "thumbnail_fallback", None) or "None",
            "pub_date": pub_date,
        }
        return self._replace_placeholders(content, mapping)

    def generate_cards(self, papers: List[Paper]) -> str:
        """Generate HTML for all paper cards (sorted newest first)."""
        def sort_key(p: Paper):
            d = self._parse_date(p)
            return (-d.toordinal(), self._authors_str(p).lower(), getattr(p, "title", "").lower())
        return "\n".join(self.generate_card(p) for p in sorted(papers, key=sort_key))