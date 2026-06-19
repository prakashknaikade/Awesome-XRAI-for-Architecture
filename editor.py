import sys

def main():
    # If --desktop or --gui is requested, run PyQt6 Desktop App
    if "--desktop" in sys.argv or "--gui" in sys.argv:
        try:
            from src.yaml_editor import main as desktop_main
            print("Launching PyQt6 Desktop Editor...")
            desktop_main()
        except ImportError as e:
            print(f"Error: PyQt6 is not installed or display server is missing: {e}")
            print("Falling back to web-based database editor...")
            from src.web_editor_server import start_server
            start_server()
    else:
        # Default mode: Web-based GUI Editor
        try:
            from src.web_editor_server import start_server
            start_server()
        except Exception as e:
            print(f"Error starting web server: {e}")
            # If web server fails, try desktop fallback
            try:
                from src.yaml_editor import main as desktop_main
                desktop_main()
            except ImportError:
                print("Error: Both web server and desktop GUI modes failed to start.")

if __name__ == '__main__':
    main()
