from pathlib import Path
from string import Template

class TemplateEngine:
    def __init__(self, template_path: Path):
        self.template_path = template_path
        self.text = template_path.read_text(encoding="utf-8")
        self.template = Template(self.text)

    def render(self, context: dict) -> str:
        # Ensure all context values are strings
        mapping = {k: ("" if v is None else str(v)) for k, v in context.items()}
        # Use safe_substitute to avoid crashes on $(
        return self.template.safe_substitute(mapping)