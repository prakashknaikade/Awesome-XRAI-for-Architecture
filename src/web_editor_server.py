import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path
import yaml
from src.arxiv_integration import ArxivIntegration
from src.fix_date import YAMLUpdater

YAML_FILE = "awesome_xrai_architecture_papers.yaml"

def normalize_title(title):
    if not title:
        return ""
    return re.sub(r'[^a-z0-9]', '', title.lower())

def normalize_url(url):
    if not url:
        return ""
    url = url.lower().strip()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    url = url.rstrip('/')
    if url.endswith('.pdf'):
        url = url[:-4]
    return url

def is_hex_id(pid):
    return bool(re.match(r'^[0-9a-f]{8}$', pid.lower())) if pid else False

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except Exception:
        pass
    try:
        return datetime(int(date_str[:4]), 1, 1)
    except Exception:
        return None

def merge_papers(papers):
    if not papers:
        return None
    papers = sorted(papers, key=lambda p: (0 if not is_hex_id(p.get('id', '')) else 1, p.get('id', '')))
    merged = dict(papers[0])
    for other in papers[1:]:
        if is_hex_id(merged.get('id', '')) and not is_hex_id(other.get('id', '')):
            merged['id'] = other['id']
        for field in ['title', 'authors', 'year', 'abstract', 'primary_category', 'project_page', 'paper', 'code', 'video', 'thumbnail', 'date_source']:
            val_m = merged.get(field)
            val_o = other.get(field)
            str_m = str(val_m).strip() if val_m is not None else ""
            str_o = str(val_o).strip() if val_o is not None else ""
            if (not str_m or str_m == 'null' or str_m == 'None') and (str_o and str_o != 'null' and str_o != 'None'):
                merged[field] = other[field]
            elif str_o and len(str_o) > len(str_m) and str_m != 'null':
                merged[field] = other[field]
        
        tags_m = set(merged.get('tags', []) or [])
        tags_o = set(other.get('tags', []) or [])
        merged['tags'] = sorted(list(tags_m.union(tags_o)))
        
        date_m = parse_date(merged.get('added_date'))
        date_o = parse_date(other.get('added_date'))
        if date_m and date_o:
            if date_o < date_m:
                merged['added_date'] = other['added_date']
        elif date_o:
            merged['added_date'] = other['added_date']
            
        pub_m = parse_date(merged.get('publication_date'))
        pub_o = parse_date(other.get('publication_date'))
        if pub_m and pub_o:
            if pub_o < pub_m:
                merged['publication_date'] = other['publication_date']
        elif pub_o:
            merged['publication_date'] = other['publication_date']
    return merged

def deduplicate_papers(papers_list):
    if not papers_list:
        return []
    parent = list(range(len(papers_list)))
    
    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]
        
    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    id_map = {}
    title_map = {}
    url_map = {}

    for idx, entry in enumerate(papers_list):
        pid = (entry.get('id') or "").strip().lower()
        title = normalize_title(entry.get('title'))
        paper_url = normalize_url(entry.get('paper'))

        if pid:
            if pid in id_map:
                union(idx, id_map[pid])
            else:
                id_map[pid] = idx
        if title:
            if title in title_map:
                union(idx, title_map[title])
            else:
                title_map[title] = idx
        if paper_url:
            if paper_url in url_map:
                union(idx, url_map[paper_url])
            else:
                url_map[paper_url] = idx

    from collections import defaultdict
    groups = defaultdict(list)
    for idx, entry in enumerate(papers_list):
        root = find(idx)
        groups[root].append(entry)

    deduped_data = []
    for root, group_entries in groups.items():
        if len(group_entries) > 1:
            merged = merge_papers(group_entries)
            deduped_data.append(merged)
        else:
            deduped_data.append(group_entries[0])
    return deduped_data

class WebEditorHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence default terminal logs to keep output clean, unless warning/error
        pass

    def send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode("utf-8"))

    def send_file(self, filepath, content_type):
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(404, f"File not found: {e}")

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Serve static template files
        if path == "/" or path == "/editor.html":
            self.send_file("src/templates/editor.html", "text/html")
            return
        elif path == "/index.html":
            self.send_file("index.html", "text/html")
            return
        elif path == "/analytics.html":
            self.send_file("analytics.html", "text/html")
            return
        elif path.startswith("/src/static/"):
            # static scripts/css
            local_path = path.lstrip("/")
            if local_path.endswith(".css"):
                self.send_file(local_path, "text/css")
            elif local_path.endswith(".js"):
                self.send_file(local_path, "application/javascript")
            else:
                self.send_file(local_path, "application/octet-stream")
            return
        elif path.startswith("/assets/"):
            # asset thumbnails
            local_path = path.lstrip("/")
            if local_path.endswith(".jpg") or local_path.endswith(".jpeg"):
                self.send_file(local_path, "image/jpeg")
            elif local_path.endswith(".png"):
                self.send_file(local_path, "image/png")
            else:
                self.send_file(local_path, "application/octet-stream")
            return

        # API Endpoints
        elif path == "/api/papers":
            # Load YAML and return as JSON
            try:
                if os.path.exists(YAML_FILE):
                    with open(YAML_FILE, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or []
                else:
                    data = []
                self.send_json(data)
            except Exception as e:
                self.send_json({"error": f"Failed to load papers: {str(e)}"}, 500)
            return

        elif path == "/api/arxiv":
            # Fetch details from arXiv API
            q_list = query.get("q", [])
            if not q_list:
                self.send_json({"error": "Missing query parameter 'q'"}, 400)
                return
            
            q_val = q_list[0]
            try:
                arxiv_integration = ArxivIntegration()
                entry = arxiv_integration.get_paper(q_val)
                if entry:
                    # Enrich with publication date
                    arxiv_id = arxiv_integration.extract_arxiv_id(q_val)
                    if arxiv_id:
                        import arxiv as arxiv_lib
                        client = arxiv_lib.Client()
                        search = arxiv_lib.Search(id_list=[arxiv_id], max_results=1)
                        results = list(client.results(search))
                        if results:
                            entry["publication_date"] = results[0].published.isoformat()
                            entry["date_source"] = "arxiv"
                            
                    entry.setdefault("added_date", datetime.now().isoformat())
                    self.send_json(entry)
                else:
                    self.send_json({"error": "No paper found on arXiv"}, 404)
            except Exception as e:
                self.send_json({"error": f"arXiv API error: {str(e)}"}, 500)
            return

        # Fallback to standard 404
        self.send_error(404, "Page not found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/papers":
            # Read content length
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                papers_list = json.loads(post_data.decode('utf-8'))
                papers_list = deduplicate_papers(papers_list)
                
                # Format dates and validate each entry
                updater = YAMLUpdater()
                for entry in papers_list:
                    # Ensure added_date is set
                    if not entry.get("added_date"):
                        entry["added_date"] = datetime.now().isoformat()
                    # Ensure publication_date is set
                    if not entry.get("publication_date"):
                        updated_entry, ok = updater.process_paper(entry)
                        if ok:
                            entry.update(updated_entry)

                # Re-sort list like Python generator
                papers_list.sort(key=updater.safe_sort_key, reverse=True)

                # Save directly back to YAML file
                with open(YAML_FILE, "w", encoding="utf-8") as f:
                    yaml.dump(papers_list, f, sort_keys=False, allow_unicode=True)

                # Regenerate index.html and analytics.html
                print("Regenerating index.html & analytics.html...")
                subprocess.run(
                    [sys.executable, "src/generate.py", YAML_FILE, "index.html"],
                    check=True
                )

                # Regenerate README.md
                print("Regenerating README.md...")
                subprocess.run(
                    [sys.executable, "generate_readme.py"],
                    check=True
                )

                self.send_json({"status": "ok", "message": "Saved database and updated website assets."})
            except Exception as e:
                print(f"Error saving database: {e}")
                self.send_json({"error": f"Failed to save database: {str(e)}"}, 500)
            return

        self.send_error(404, "Endpoint not found")

    # Handle CORS preflight request
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def start_server(port=8000):
    handler = WebEditorHandler
    
    # Try finding a free port if port 8000 is occupied
    max_attempts = 10
    current_port = port
    
    for attempt in range(max_attempts):
        try:
            with socketserver.TCPServer(("", current_port), handler) as httpd:
                print(f"\n=========================================")
                print(f"  XRAI4AEC Web Database Editor is running  ")
                print(f"  Url: http://localhost:{current_port}     ")
                print(f"=========================================\n")
                
                # Automatically open in default browser
                webbrowser.open(f"http://localhost:{current_port}")
                
                print("Press Ctrl+C to stop the server.")
                httpd.serve_forever()
                break
        except OSError as e:
            if attempt < max_attempts - 1:
                print(f"Port {current_port} is busy. Trying port {current_port + 1}...")
                current_port += 1
            else:
                raise e


if __name__ == "__main__":
    start_server()
