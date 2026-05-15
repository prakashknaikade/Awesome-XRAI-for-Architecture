import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import yaml
import webbrowser
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit, QScrollArea, QListWidget,
    QGridLayout, QDialog, QComboBox, QSizePolicy, QSplitter
)

from src.fix_date import YAMLUpdater
from src.components.widgets import TagButton, URLWidget
from src.components.dialogs import ArxivAddDialog


YAML_FILE = "awesome_xrai_architecture_papers.yaml"


class YAMLEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.yaml_updater = YAMLUpdater()
        self.setWindowTitle("XRAI Architecture Papers Editor")
        self.setMinimumSize(900, 650)
        self.resize(1200, 800) #reasonable size

        # Data/state
        self.yaml_path = Path(YAML_FILE)
        self.data: List[dict] = []
        self.current_index = 0
        self.search_results: List[int] = []

        # Widget registries
        self.fields: Dict[str, QWidget] = {}
        self.url_widgets: Dict[str, URLWidget] = {}
        self.tag_buttons: Dict[str, TagButton] = {}

        # Primary categories
        self.primary_categories = [
            "AI-Driven Design and Generative Architecture",
            "Reality Capture and Digital Twins",
            "Computational BIM and Intelligent Operations",
            "Heritage Conservation and Cultural Preservation",
            "Sustainability and Environmental Performance",
            "Sustainable Real Estate Valuation and Economics",
            "Human-Computer Interaction and Human-Building Interaction",
        
        ]

        # Tags list (grouped, headers are Title Case strings)
        self.available_tags = [
            #"AI-Driven Design and Generative Architecture"
            "Generative Design and Design Space Exploration",
            "geometry generation", "Form Finding", "design automation", "GANs", "VAE", 
            "diffusion models", "RL", "procedural modeling", "text-to-3D",
            "image-to-3D", "conditional generation",  
            "design space optimization", "multi-objective optimization", "search-based design",

            "Parametric, Computational and Algorithmic Design",
            "rule-based modeling", "structural optimization", 
            "Grasshopper", "Rhino", "Houdini",

            "Performance-Driven Design",
            "energy modeling", "energy optimization", "thermal simulation", "daylight optimization",
            "structural efficiency", "AI performance feedback",
            "environmental simulation", "multi-criteria optimization",

            #"Digital Twins and 3D Reconstruction"
            "3D Reconstruction",
            "point clouds", "LiDAR", "photogrammetry", "SLAM", "NeRF", "3DGS", "SfM",
            "indoor scene reconstruction", "outdoor scene reconstruction", "scene understanding", "scene editing", "scene interaction",

            "Floor Plan Reconstruction and Parametrization",
            "digital twins", "BIM", "parametric BIM", "mesh-to-BIM", "scan-to-BIM", "point-cloud-to-plan", "image-to-plan",
            "2D floor plan", "3D floor plan", "layout recovery", "room segmentation",
            "object detection", "semantic segmentation", "structural element detection", "Revit automation",

            #"Computational BIM and Intelligent Modeling"
            "Predictive Analytics and Performance Optimization",
            "predictive analytics", "building energy forecasting",
            "time-series analysis", "anomaly detection",
            
            "Quality Control and Validation",
            "BIM validation", "model checking", "clash detection", "data quality", "geometric validation",
            "automated compliance checking", "QA/QC in BIM",

            #"Heritage Conservation & Cultural Preservation"
            "Digital Documentation and Archiving",
            "heritage digitization", "digital archives", "3D scanning",
            "Heritage BIM", "documentation workflows",

            "Predictive Conservation and Risk Assessment",
            "conservation AI", "risk modeling", "structural health monitoring", "predictive maintenance",
            "damage detection", "material degradation prediction",

            "Virtual Reality Experiences and Education",
            "cultural heritage VR", "museum VR", "AR cultural experiences",
            "heritage XR visualization", "immersive education", "XR storytelling", 

            #"Sustainability & Environmental Performance"
            "AI for Energy Performance Optimization",
            "building energy simulation", "AI HVAC optimization",
            "energy-efficient design", "smart grids",

            "Sustainable Buildings",
            "lifecycle assessment", "sustainable materials", "embodied carbon", "material simulation",
            "AI material selection", "circular economy", "material passports", 
            "sustainable construction", "sustainable disassembly",

            "Smart Building Systems and IoT Integration",
            "intelligent environments", "AI building automation", "adaptive control", "real-time monitoring", 
            "human-centric IoT", "sensor data integration", "building performance dashboard", 
            "big data in buildings","blockchain for AEC", "data templates for circularity",

            #"Sustainable Real Estate Valuation and Economics"
            "AI-Powered Real Estate Valuation",
            "predictive pricing", "ML for sustainable real estate", "real estate analytics",
            "AI in asset management", "predictive investment", "asset performance",
             
            "Virtual Property Tours and Marketing",
            "XR immersive walkthroughs", "real estate visualization", "virtual staging",

            #"Human-Computer Interaction and Human-Building Interaction"
            "XRAI for AEC",
            "immersive design", "collaborative VR co-design", "XR design review",  
            "XRAI inclusive design", "XRAI automated accessibility",
            "AR/VR/XR visualization", "Interactive Visualization",
            "AR/VR interfaces", "VR dashboards", "adaptive environments", "metaverse for AEC",
            "Unity", "Unreal Engine",
            
            "Occupant Behavior Analysis and Spatial Optimization",
            "HCI-HBI", "occupant behavior", "spatial analytics", "movement analysis", "space utilization",
            "sensor-driven design", "AI occupancy modeling", "behavior modeling",

            #"Misc / Emerging"
            "Cross-Modal Intelligence and Multimodal Integration",
            "Vision-Language Models for AEC","LLMs for AEC","Multimodal Design Assistance", 
            "Context-Aware Spatial Intelligence", "Agent-based Modeling", 
            
            "Review Paper", "Dataset", "Case Study", "Tool/Library",
            
        ]

        # Category headers to highlight in yellow
        self.highlighted_categories = {
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
            "Portfolio Management and Investment Analysis",
            "Virtual Property Tours and Marketing",
            "XRAI for AEC",
            "Occupant Behavior Analysis and Spatial Optimization",
            "Cross-Modal Intelligence and Multimodal Integration",
            "Review Paper", "Dataset", "Case Study", "Tool/Library",
            
        }
        
        # misc category headers in bold
        
        self.misc_highlighted_categories = {
            "Cross-Modal Intelligence and Multimodal Integration",
            "Vision-Language Models for Architecture", 
            "LLMs for Architecture", 
            "Multimodal Design Assistance",
            "Context-Aware Spatial Intelligence", "Agent-based Modeling",
            "Review Paper", "Dataset", "Case Study", "Tool/Library",
        }

        # Load data/UI
        self.load_yaml()
        self.setup_ui()
        self.setup_status_bar()
        self.show_current_entry()

    # ---------------- Data ----------------
    def safe_sort_key(self, x: Dict[str, Any]) -> tuple:
        pub_date = x.get("publication_date", "9999")
        pub_date = pub_date if isinstance(pub_date, str) else "9999"
        authors = x.get("authors", "")
        if isinstance(authors, str) and authors.strip():
            try:
                first_author = authors.split(",")[0].strip()
                last = first_author.split()[-1].lower() if first_author else "z"
            except Exception:
                last = "z"
        else:
            last = "z"
        title = x.get("title", "")
        title = title.lower() if isinstance(title, str) else "z"
        src = x.get("date_source", "unknown")
        prio = {"arxiv": 0, "estimated": 1, "unknown": 2}.get(src, 2)
        return (pub_date, prio, last, title)

    def load_yaml(self):
        try:
            if self.yaml_path.exists():
                with self.yaml_path.open("r", encoding="utf-8") as f:
                    self.data = yaml.safe_load(f) or []
                if not isinstance(self.data, list):
                    raise ValueError("Top-level YAML must be a list.")
                self.data.sort(key=self.safe_sort_key, reverse=True)
            else:
                self.data = []
            if not self.data:
                self.data = [self._blank_entry()]
            self.current_index = 0
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load YAML: {e}")
            self.data = [self._blank_entry()]
            self.current_index = 0

    def _blank_entry(self) -> dict:
        return {
            "id": "",
            "title": "",
            "authors": "",
            "year": "",
            "publication_date": "",
            "primary_category": self.primary_categories[0],
            "project_page": "",
            "paper": "",
            "code": "",
            "video": "",
            "abstract": "",
            "tags": [],
            "date_source": "manual",
        }

    def save_yaml(self) -> bool:
        try:
            with self.yaml_path.open("w", encoding="utf-8") as f:
                yaml.dump(self.data, f, sort_keys=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False

    # ---------------- Status bar ----------------
    def setup_status_bar(self):
        self.statusBar().showMessage("")
        self.save_indicator = QLabel("")
        self.statusBar().addPermanentWidget(self.save_indicator)

    def show_save_feedback(self, success=True):
        if success:
            self.save_indicator.setText("✓ Changes saved")
            self.save_indicator.setStyleSheet("color:#4CAF50; font-weight:bold;")
        else:
            self.save_indicator.setText("⚠ Save failed")
            self.save_indicator.setStyleSheet("color:#f44336; font-weight:bold;")
        QTimer.singleShot(1500, self.clear_save_indicator)

    def clear_save_indicator(self):
        self.save_indicator.setText("")
        self.save_indicator.setStyleSheet("")

    # ---------------- UI ----------------
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)

        self.create_nav_bar(main)
        self.create_main_content(main)

    def create_nav_bar(self, parent: QVBoxLayout):
        # Keep a reference like yaml_editor.py so add_* can add to it if needed
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(8, 6, 8, 6)
        self.nav_layout.setSpacing(10)

        # Actions group (left)
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(8)
        actions.addWidget(self.add_manual_button())
        actions.addWidget(self.add_arxiv_button())

        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.prev_button.clicked.connect(self.prev_entry)
        self.next_button.clicked.connect(self.next_entry)
        actions.addWidget(self.prev_button)
        actions.addWidget(self.next_button)

        delete_btn = QPushButton("Delete Entry")
        delete_btn.setStyleSheet(
            "QPushButton{background:#dc3545;color:#fff;border:none;padding:5px 10px;border-radius:5px}"
            "QPushButton:hover{background:#c82333}"
        )
        delete_btn.clicked.connect(self.delete_current_entry)
        actions.addWidget(delete_btn)

        self.entry_counter = QLabel("")
        actions.addWidget(self.entry_counter)

        # Compact "Go to" group (no gap between label and input)
        goto_widget = QWidget()
        goto = QHBoxLayout(goto_widget)
        goto.setContentsMargins(0, 0, 0, 0)
        goto.setSpacing(0)  # removed extra space
        goto.addWidget(QLabel("Go to:"))
        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(70)
        self.page_input.returnPressed.connect(self.go_to_page)
        goto.addWidget(self.page_input)

        # Compact "Search" group pinned to the far right (no gap between label and input)
        search_widget = QWidget()
        search = QHBoxLayout(search_widget)
        search.setContentsMargins(0, 0, 0, 0)
        search.setSpacing(0)  # removed extra space
        search.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title or authors...")
        self.search_input.returnPressed.connect(self.search_entry)
        self.search_input.setMinimumWidth(180)
        self.search_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        search.addWidget(self.search_input)

        # Compose bar
        self.nav_layout.addLayout(actions)
        self.nav_layout.addWidget(goto_widget)
        self.nav_layout.addStretch(1)
        self.nav_layout.addWidget(search_widget, 0, Qt.AlignmentFlag.AlignRight)
        
        search_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        parent.addLayout(self.nav_layout)

    def create_main_content(self, parent: QVBoxLayout):
        # Use a splitter so panes are resizable and adapt cross-platform
        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)

        # Left pane
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(8, 8, 8, 8)
        form_layout.setSpacing(8)

        self.create_basic_fields(form_layout)
        self.create_primary_category(form_layout)
        self.create_url_fields(form_layout)
        self.create_abstract(form_layout)
        self.create_current_tags(form_layout)

        form_scroll = QScrollArea()
        form_scroll.setWidget(form_container)
        form_scroll.setWidgetResizable(True)
        form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Let it be flexible: no hard max width, no Fixed policy
        form_scroll.setMinimumWidth(420)
        form_scroll.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        # Right pane (existing)
        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.create_tags_widget(right_layout)

        # Add to splitter
        splitter.addWidget(form_scroll)
        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 0)  # left can grow a bit
        splitter.setStretchFactor(1, 1)  # right gets remaining space

        # Reasonable initial sizes (left ~500px)
        splitter.setSizes([500, 700])

        parent.addWidget(splitter)

    def create_basic_fields(self, parent: QVBoxLayout):
        for name in ["id", "title", "authors", "year", "publication_date"]:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(8)
            lbl = QLabel(name.replace("_", " ").title() + ":")
            lbl.setMinimumWidth(160)  # slightly wider labels for clarity
            lbl.setStyleSheet("font-weight:bold;")
            edit = QLineEdit()
            if name == "id":
                # Prevent accidental edits that could cause mismatches and “replacement”
                edit.setReadOnly(True)
                edit.setStyleSheet("background:#2b2b2b;color:#bdbdbd;")
            elif name == "publication_date":
                edit.setReadOnly(True)
                edit.setStyleSheet("background:#2b2b2b;color:#bdbdbd;")
            else:
                edit.textChanged.connect(self.auto_save)
            self.fields[name] = edit
            row.addWidget(lbl)
            row.addWidget(edit)
            parent.addLayout(row)

    def create_primary_category(self, parent: QVBoxLayout):
        row = QHBoxLayout()
        lbl = QLabel("Primary Category:")
        lbl.setMinimumWidth(150)
        lbl.setStyleSheet("font-weight:bold; color:#2196F3;")
        self.primary_category_combo = QComboBox()
        self.primary_category_combo.addItems(self.primary_categories)
        self.primary_category_combo.currentTextChanged.connect(self.auto_save)
        row.addWidget(lbl)
        row.addWidget(self.primary_category_combo)
        parent.addLayout(row)

    def create_url_fields(self, parent: QVBoxLayout):
        for field in ["project_page", "paper", "code", "video"]:
            widget = URLWidget(field.replace("_", " ").title() + ":")
            widget.open_button.clicked.connect(lambda _=False, f=field: self.open_url(f))
            widget.url_input.textChanged.connect(self.handle_url_change)
            self.url_widgets[field] = widget
            parent.addWidget(widget)

    def create_abstract(self, parent: QVBoxLayout):
        lbl = QLabel("Abstract:")
        lbl.setStyleSheet("font-weight:bold;")
        edit = QTextEdit()
        edit.setAcceptRichText(False)
        edit.setTabChangesFocus(False)
        edit.setMinimumHeight(150)
        edit.textChanged.connect(self.auto_save)
        self.fields["abstract"] = edit
        parent.addWidget(lbl)
        parent.addWidget(edit)

    def create_current_tags(self, parent: QVBoxLayout):
        lbl = QLabel("Current Tags:")
        lbl.setStyleSheet("font-weight:bold;")
        self.current_tags_list = QListWidget()
        self.current_tags_list.setMinimumHeight(180)
        self.current_tags_list.setStyleSheet(
            "QListWidget{background:#1e1e1e;border:1px solid #3a3a3a;border-radius:4px;color:#ddd;}"
        )
        parent.addWidget(lbl)
        parent.addWidget(self.current_tags_list)

    def create_tags_widget(self, parent_layout: QHBoxLayout):
        self.tags_scroll = QScrollArea()
        self.tags_scroll.setWidgetResizable(True)
        self.tags_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tags_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # self.tags_scroll.setMinimumWidth(600)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(4)
        grid.setContentsMargins(8, 8, 8, 8)

        cols = 4
        total_tags = len(self.available_tags)
        rows_per_col = (total_tags + cols - 1) // cols

        for i, tag in enumerate(self.available_tags):
            btn = TagButton(tag)
            btn.clicked.connect(self.update_tags)
            self.style_tag_button(btn, tag)
            self.tag_buttons[tag] = btn

            col = i // rows_per_col
            row = i % rows_per_col
            grid.addWidget(btn, row, col)

        for c in range(cols):
            grid.setColumnStretch(c, 1)

        self.tags_scroll.setWidget(container)
        parent_layout.addWidget(self.tags_scroll)

    # ---------------- Styling ----------------
    def style_tag_button(self, btn: TagButton, tag: str):
        if tag in self.highlighted_categories:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c2c2c;
                    color: #FFD700;                  /* yellow */
                    border: 1px solid #757575;
                    padding: 6px 10px;
                    border-radius: 5px;
                    text-align: left;
                    font-weight: bold;
                    min-height: 22px;
                }
                QPushButton:hover { background:#3a3a3a; color:#FFEB66; }
                QPushButton:checked { background:#4CAF50; color:white; border-color:#4CAF50; }
            """)
        elif tag in self.misc_highlighted_categories:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c2c2c;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 6px 10px;
                    border-radius: 5px;
                    text-align: left;
                    font-weight: bold;
                    min-height: 22px;
                }
                QPushButton:hover { background:#3a3a3a; }
                QPushButton:checked { background:#4CAF50; color:white; }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c2c2c;
                    color: #cccccc;
                    border: 1px solid #555555;
                    padding: 4px 8px;
                    border-radius: 4px;
                    text-align: left;
                    min-height: 20px;
                }
                QPushButton:hover { background:#3a3a3a; color:white; }
                QPushButton:checked { background:#4CAF50; color:white; border-color:#4CAF50; }
            """)


    # ---------------- Actions ----------------
    def auto_save(self):
        if not self.data:
            return
        entry = self.data[self.current_index]

        # Fields
        for name, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                entry[name] = widget.text().strip()
            elif isinstance(widget, QTextEdit):
                entry[name] = widget.toPlainText().strip()

        # Primary category
        entry["primary_category"] = self.primary_category_combo.currentText()

        # URLs
        for field, widget in self.url_widgets.items():
            entry[field] = widget.url_input.text().strip()

        # Tags
        entry["tags"] = sorted([t for t, b in self.tag_buttons.items() if b.isChecked()])

        # Fill publication_date if missing
        if not entry.get("publication_date"):
            updated, ok = self.yaml_updater.process_paper(entry)
            if ok:
                entry.update(updated)

        # Keep focus stable after resort
        current_id = entry.get("id")

        # Sort and save
        self.data.sort(key=self.safe_sort_key, reverse=True)

        # Re-find current index by id (if present)
        if current_id:
            try:
                self.current_index = next(i for i, e in enumerate(self.data) if e.get("id") == current_id)
            except StopIteration:
                self.current_index = min(self.current_index, len(self.data) - 1)

        ok = self.save_yaml()
        self.show_save_feedback(ok)
        self.update_entry_counter()

    def handle_url_change(self):
        self.auto_save()

    def update_tags(self):
        current = [t for t, b in self.tag_buttons.items() if b.isChecked()]
        self.current_tags_list.clear()
        self.current_tags_list.addItems(sorted(current))
        self.auto_save()

    # ---------------- Navigation ----------------
    def show_current_entry(self):
        if not self.data:
            return
        entry = self.data[self.current_index]

        # Fields (cast to string to avoid TypeError for ints like year)
        for name, widget in self.fields.items():
            val = entry.get(name, "")
            if isinstance(widget, QLineEdit):
                widget.blockSignals(True)
                widget.setText(str(val) if val is not None else "")
                widget.blockSignals(False)
            elif isinstance(widget, QTextEdit):
                widget.blockSignals(True)
                widget.setPlainText(str(val) if val is not None else "")
                widget.blockSignals(False)

        # Primary category
        cat = entry.get("primary_category", self.primary_categories[0])
        self.primary_category_combo.blockSignals(True)
        if cat in self.primary_categories:
            self.primary_category_combo.setCurrentText(cat)
        else:
            self.primary_category_combo.setCurrentIndex(0)
        self.primary_category_combo.blockSignals(False)

        # URLs
        for field, widget in self.url_widgets.items():
            widget.url_input.blockSignals(True)
            widget.url_input.setText(entry.get(field, "") or "")
            widget.url_input.blockSignals(False)

        # Tags
        selected = set(entry.get("tags", []))
        for t, b in self.tag_buttons.items():
            b.blockSignals(True)
            b.setChecked(t in selected)
            b.blockSignals(False)

        self.current_tags_list.clear()
        self.current_tags_list.addItems(sorted(selected))
        self.update_entry_counter()

    def update_entry_counter(self):
        self.entry_counter.setText(f"Entry {self.current_index + 1} of {len(self.data)}")

    def prev_entry(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.search_results.clear()
            self.show_current_entry()

    def next_entry(self):
        if self.current_index < len(self.data) - 1:
            self.current_index += 1
            self.search_results.clear()
            self.show_current_entry()

    def go_to_page(self):
        try:
            page = int(self.page_input.text()) - 1
            if 0 <= page < len(self.data):
                self.current_index = page
                self.search_results.clear()
                self.show_current_entry()
        except ValueError:
            pass
        finally:
            self.page_input.clear()

    def search_entry(self):
        term = self.search_input.text().lower().strip()
        if not term:
            return
        for i, e in enumerate(self.data):
            title = (e.get("title") or "").lower()
            authors = (e.get("authors") or "").lower()
            if term in title or term in authors:
                self.current_index = i
                self.show_current_entry()
                self.statusBar().showMessage(f"Found: {e.get('title', 'Untitled')}")
                return
        QMessageBox.information(self, "Search", "No matching entries found")

    def open_url(self, field: str):
        url = self.url_widgets[field].url_input.text().strip()
        if url:
            webbrowser.open(url)

    def delete_current_entry(self):
        if not self.data:
            return
        title = self.data[self.current_index].get("title", "Untitled")
        reply = QMessageBox.question(
            self, "Delete Entry",
            f"Are you sure you want to delete this entry?\n\n{title}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.data[self.current_index]
            if not self.data:
                self.data = [self._blank_entry()]
            self.current_index = min(self.current_index, len(self.data) - 1)
            self.save_yaml()
            self.show_current_entry()

    # ---------------- Add entries ----------------
    def add_arxiv_button(self):
        # usable by nav bar builder
        if hasattr(self, "arxiv_button"):
            return self.arxiv_button
        self.arxiv_button = QPushButton("Add from arXiv")
        self.arxiv_button.clicked.connect(self.show_arxiv_dialog)
        return self.arxiv_button

    def add_manual_button(self):
        if hasattr(self, "manual_button"):
            return self.manual_button
        self.manual_button = QPushButton("Add Manually")
        self.manual_button.clicked.connect(self.add_manual_entry)
        return self.manual_button

    def add_manual_entry(self):
        """Add a new empty entry manually with guaranteed-unique ID and proper focus."""
        try:
            # Generate unique ID; retry if collision (very unlikely, but safe).
            existing_ids = {e.get("id") for e in self.data if isinstance(e, dict)}
            new_id = str(uuid.uuid4())[:8]
            while new_id in existing_ids:
                new_id = str(uuid.uuid4())[:8]

            new_entry = {
                "id": new_id,
                "title": "",
                "authors": "",
                "year": str(datetime.now().year),   # keep as string to avoid setText(int) issues later
                "abstract": "",
                "primary_category": self.primary_categories[0],
                "project_page": None,
                "paper": None,
                "code": None,
                "video": None,
                "tags": [],
                "publication_date": None,
                "date_source": "manual",
                "added_date": datetime.now().isoformat(),
            }

            # Append and persist
            self.data.append(new_entry)
            self.data.sort(key=self.safe_sort_key, reverse=True)

            # Focus the new entry by id after sorting
            try:
                self.current_index = next(i for i, e in enumerate(self.data) if e.get("id") == new_id)
            except StopIteration:
                self.current_index = len(self.data) - 1

            self.save_yaml()
            self.show_current_entry()
            self.search_results.clear()
            self.update_entry_counter()
            self.show_save_feedback(True)

        except Exception as e:
            print(f"Error adding manual entry: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add manual entry: {str(e)}")

    def show_arxiv_dialog(self):
        """Open the arXiv dialog and reliably focus the truly new entry."""
        before_ids = {e.get("id") for e in self.data if isinstance(e, dict) and e.get("id")}
        dialog = ArxivAddDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reload and detect new entry
            self.load_yaml()
            after_ids = {e.get("id") for e in self.data if isinstance(e, dict) and e.get("id")}
            new_ids = list(after_ids - before_ids)

            # Default: keep current index stable
            target_id = None
            if new_ids:
                target_id = new_ids[0]

            # If we have a single new entry, enrich and re-sort
            if target_id:
                try:
                    idx = next(i for i, e in enumerate(self.data) if e.get("id") == target_id)
                    entry = self.data[idx]

                    # Ensure defaults
                    entry.setdefault("primary_category", self.primary_categories[0])
                    entry.setdefault("added_date", datetime.now().isoformat())

                    # Populate publication_date
                    updated, ok = self.yaml_updater.process_paper(entry)
                    if ok:
                        self.data[idx] = updated

                    # Re-sort and re-find index by id
                    self.data.sort(key=self.safe_sort_key, reverse=True)
                    idx = next(i for i, e in enumerate(self.data) if e.get("id") == target_id)
                    self.current_index = idx

                    # Persist
                    self.save_yaml()
                except StopIteration:
                    self.current_index = min(self.current_index, len(self.data) - 1)
            else:
                self.current_index = min(self.current_index, len(self.data) - 1)

            self.show_current_entry()
            self.search_results.clear()
            self.update_entry_counter()
            self.show_save_feedback(True)


def main():
    app = QApplication(sys.argv)
    editor = YAMLEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()