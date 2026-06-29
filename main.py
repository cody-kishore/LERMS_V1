"""
LERMS - Local Resource Management System
An offline educational app that creates a local server via mobile hotspot
to share PDFs and host an offline Python compiler.
"""

import os
import sys
import io
import socket
import shutil
import threading
import http.server
import socketserver
from contextlib import redirect_stdout

# ---------------------------------------------------------------------------
# KivyMD imports — guard so the module can be imported without a display
# ---------------------------------------------------------------------------
try:
    from kivymd.app import MDApp
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.label import MDLabel
    from kivymd.uix.switch import MDSwitch
    from kivymd.uix.toolbar import MDTopAppBar
    from kivy.clock import Clock
    from kivy.core.window import Window
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------
_ANDROID_PATH = "/storage/emulated/0/Documents/Classroom_Sync"
_LOCAL_FALLBACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Classroom_Sync")

BASE_PATH = _ANDROID_PATH if os.path.exists("/storage/emulated/0") else _LOCAL_FALLBACK

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
PORT = 8000

# ---------------------------------------------------------------------------
# FEATURE 1: Auto-initialization & file management
# ---------------------------------------------------------------------------

def ensure_base_path():
    """Create BASE_PATH if it does not exist and seed it with asset files."""
    os.makedirs(BASE_PATH, exist_ok=True)

    for asset_file in ("template.html", "compiler.html"):
        src = os.path.join(ASSETS_DIR, asset_file)
        dst = os.path.join(BASE_PATH, asset_file)
        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copy2(src, dst)

# ---------------------------------------------------------------------------
# FEATURE 2: HTML Generator — scan PDFs and build index.html
# ---------------------------------------------------------------------------

def build_library():
    """Scan BASE_PATH for PDFs and generate index.html from template.html."""
    ensure_base_path()

    template_path = os.path.join(BASE_PATH, "template.html")
    if not os.path.exists(template_path):
        # Copy from assets if not yet seeded
        src = os.path.join(ASSETS_DIR, "template.html")
        if os.path.exists(src):
            shutil.copy2(src, template_path)

    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    pdf_files = [
        fname for fname in os.listdir(BASE_PATH)
        if fname.lower().endswith(".pdf")
    ]

    cards_html = ""
    for pdf in sorted(pdf_files):
        encoded = pdf.replace(" ", "%20")
        cards_html += f"""
        <div class="card">
            <div class="card-title">{pdf}</div>
            <div class="card-actions">
                <a class="btn btn-view" href="{encoded}" target="_blank">VIEW</a>
                <a class="btn btn-save" href="{encoded}" download="{pdf}">SAVE</a>
            </div>
        </div>
"""

    if not cards_html:
        cards_html = '<p class="no-pdfs">No PDFs found in Classroom_Sync folder.</p>'

    output_html = template_html.replace("<!-- PDF_CARDS_PLACEHOLDER -->", cards_html)

    index_path = os.path.join(BASE_PATH, "index.html")
    tmp_path = index_path + ".tmp"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(output_html)
        os.replace(tmp_path, index_path)
    except Exception as e:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise e

    return len(pdf_files)

# ---------------------------------------------------------------------------
# FEATURE 3: Custom HTTP Server with /run_python endpoint
# ---------------------------------------------------------------------------

class LERMSHandler(http.server.SimpleHTTPRequestHandler):
    """Serve files from BASE_PATH and handle Python code execution."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_PATH, **kwargs)

    def log_message(self, format, *args):
        # Suppress default server logging to keep console clean
        pass

    def do_POST(self):
        if self.path == "/run_python":
            content_length = int(self.headers.get("Content-Length", 0))
            code = self.rfile.read(content_length).decode("utf-8", errors="replace")

            output_buffer = io.StringIO()
            try:
                with redirect_stdout(output_buffer):
                    exec(code, {"__builtins__": __builtins__})  # noqa: S102
                result = output_buffer.getvalue()
                if not result:
                    result = "(no output)"
            except Exception as exc:
                result = f"Error: {type(exc).__name__}: {exc}"

            encoded = result.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(encoded)
        else:
            self.send_response(405)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


_server_instance = None
_server_thread = None


def start_server():
    global _server_instance, _server_thread
    if _server_instance is not None:
        return

    _server_instance = ReusableTCPServer(("", PORT), LERMSHandler)
    _server_thread = threading.Thread(
        target=_server_instance.serve_forever,
        daemon=True
    )
    _server_thread.start()


def stop_server():
    global _server_instance, _server_thread
    if _server_instance:
        _server_instance.shutdown()
        _server_instance.server_close()
        _server_instance = None
        _server_thread = None


# ---------------------------------------------------------------------------
# Helper — get local IP address
# ---------------------------------------------------------------------------

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ---------------------------------------------------------------------------
# FEATURE 4: KivyMD UI
# ---------------------------------------------------------------------------

if KIVY_AVAILABLE:

    KV = """
<LERMSLayout>:
    orientation: "vertical"
    md_bg_color: app.theme_cls.backgroundColor

    MDTopAppBar:
        title: "LERMS Engine"
        md_bg_color: app.theme_cls.primaryColor
        specific_text_color: 1, 1, 1, 1
        elevation: 4

    MDBoxLayout:
        orientation: "vertical"
        padding: "24dp"
        spacing: "16dp"
        adaptive_height: True

        MDLabel:
            text: "Local Resource Management System"
            halign: "center"
            font_style: "Body1"
            theme_text_color: "Secondary"
            adaptive_height: True

        MDBoxLayout:
            orientation: "horizontal"
            adaptive_height: True
            spacing: "12dp"

            MDLabel:
                text: "Host Mode"
                font_style: "H6"
                theme_text_color: "Primary"
                adaptive_height: True

            MDSwitch:
                id: host_switch
                on_active: app.on_host_toggle(self, self.active)

        MDLabel:
            id: ip_label
            text: "IP: detecting..."
            halign: "left"
            font_style: "Body1"
            theme_text_color: "Primary"
            adaptive_height: True

        MDLabel:
            id: status_label
            text: "Status: Ready"
            halign: "left"
            font_style: "Body2"
            theme_text_color: "Secondary"
            adaptive_height: True

        MDLabel:
            id: log_label
            text: ""
            halign: "left"
            font_style: "Caption"
            theme_text_color: "Hint"
            adaptive_height: True
"""

    from kivy.lang import Builder

    class LERMSLayout(MDBoxLayout):
        pass

    class LERMSApp(MDApp):
        def build(self):
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Blue"
            Builder.load_string(KV)
            self.layout = LERMSLayout()
            return self.layout

        def on_start(self):
            ensure_base_path()
            ip = get_local_ip()
            self.layout.ids.ip_label.text = f"Local IP: {ip}"
            self.layout.ids.status_label.text = "Status: Ready — flip Host Mode to start"

        def on_host_toggle(self, switch, is_active):
            if is_active:
                self._start_hosting()
            else:
                self._stop_hosting()

        def _start_hosting(self):
            try:
                self.layout.ids.status_label.text = "Status: Building library..."
                self.layout.ids.log_label.text = ""

                def _run(_dt):
                    try:
                        pdf_count = build_library()
                        start_server()
                        ip = get_local_ip()
                        self.layout.ids.status_label.text = (
                            f"Status: Found {pdf_count} PDF(s). "
                            f"Server live at {ip}:{PORT}"
                        )
                        self.layout.ids.log_label.text = (
                            f"Open http://{ip}:{PORT} on any device connected to this hotspot."
                        )
                    except Exception as exc:
                        self.layout.ids.status_label.text = "Status: Crash!"
                        self.layout.ids.log_label.text = f"Crash Log: {exc}"

                Clock.schedule_once(_run, 0.1)

            except Exception as exc:
                self.layout.ids.status_label.text = "Status: Error"
                self.layout.ids.log_label.text = f"Error: {exc}"

        def _stop_hosting(self):
            try:
                stop_server()
                self.layout.ids.status_label.text = "Status: Server stopped"
                self.layout.ids.log_label.text = ""
            except Exception as exc:
                self.layout.ids.log_label.text = f"Stop error: {exc}"


def main():
    if KIVY_AVAILABLE:
        LERMSApp().run()
    else:
        print("Kivy/KivyMD not installed. Running in headless/server-only mode.")
        ensure_base_path()
        count = build_library()
        print(f"Built library with {count} PDF(s) at: {BASE_PATH}")
        ip = get_local_ip()
        print(f"Starting server on {ip}:{PORT} ...")
        start_server()
        print(f"Server running. Open http://{ip}:{PORT} in a browser.")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            stop_server()
            print("Server stopped."
            
if __name__ == "__main__":
    main()