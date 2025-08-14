import os
import time
import math
import queue
import signal
import threading
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed

# -----------------------------
# Configuration
# -----------------------------
MAX_WORKERS = 4
CHUNK_SIZE = 64 * 1024   # 64KB
RETRIES = 3
BACKOFF_BASE = 0.5       # seconds: 0.5, 1.0, 2.0
TIMEOUT = 20             # per request

URLS = [
    "https://picsum.photos/300/200",
    "https://placebear.com/400/250",
    "https://via.placeholder.com/600x400",
    "https://picsum.photos/600/400",
    "https://www.learningcontainer.com/wp-content/uploads/2020/04/sample-text-file.txt",
    "https://filesamples.com/samples/document/txt/sample1.txt",
    "https://httpbin.org/bytes/204800",  # ~200KB
    "https://httpbin.org/bytes/1024000", # ~1MB
    "https://loremflickr.com/640/360",
    "https://placekitten.com/500/300",
]

# -----------------------------
# Thread-safe message passing
# -----------------------------
ui_queue = queue.Queue()

def ui_log(msg):
    ui_queue.put(("log", msg))

def ui_progress(task_id, percent, text=None):
    ui_queue.put(("progress", task_id, percent, text))

def ui_status(task_id, text):
    ui_queue.put(("status", task_id, text))

# -----------------------------
# Helpers
# -----------------------------
def file_extension_from_content_type(content_type: str) -> str:
    if not content_type:
        return ".bin"
    ct = content_type.lower()
    if "image" in ct:
        if "png" in ct: return ".png"
        if "jpeg" in ct or "jpg" in ct: return ".jpg"
        if "gif" in ct: return ".gif"
        return ".img"
    if "text" in ct or "json" in ct: return ".txt"
    return ".bin"

def human_bytes(n: int):
    if n is None: 
        return "?"
    units = ["B", "KB", "MB", "GB"]
    i = 0
    x = float(n)
    while x >= 1024 and i < len(units) - 1:
        x /= 1024.0
        i += 1
    return f"{x:.1f}{units[i]}"

# -----------------------------
# Download worker with progress, retries, cancel
# -----------------------------
def download_worker(task_id, url, out_dir, cancel_event: threading.Event):
    headers = {"User-Agent": "Mozilla/5.0 (TechNexa-Demo)"}

    for attempt in range(1, RETRIES + 1):
        if cancel_event.is_set():
            ui_status(task_id, "Cancelled")
            return False

        try:
            ui_status(task_id, f"Connecting (attempt {attempt}/{RETRIES})")
            with requests.get(url, headers=headers, stream=True, timeout=TIMEOUT) as r:
                status = r.status_code
                if status != 200:
                    raise requests.RequestException(f"HTTP {status}")

                total = r.headers.get("Content-Length")
                total = int(total) if total is not None else None
                ct = r.headers.get("Content-Type", "")
                ext = file_extension_from_content_type(ct)
                filename = f"download_{task_id}{ext}"
                filepath = os.path.join(out_dir, filename)

                downloaded = 0
                started = time.perf_counter()
                ui_status(task_id, "Downloading")

                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(CHUNK_SIZE):
                        if cancel_event.is_set():
                            ui_status(task_id, "Cancelled")
                            # Clean up partial file
                            try:
                                f.close()
                                os.remove(filepath)
                            except Exception:
                                pass
                            return False
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = int((downloaded / total) * 100)
                        else:
                            # No content-length: estimate progress by chunks
                            pct = min(99, int((downloaded / (512 * 1024)) * 100))  # fake up to ~512KB
                        ui_progress(task_id, pct, f"{human_bytes(downloaded)} / {human_bytes(total)}")

                elapsed = time.perf_counter() - started
                ui_progress(task_id, 100, f"Done in {elapsed:.2f}s → {filename}")
                ui_log(f"[Task {task_id}] Saved: {filename} ({human_bytes(downloaded)}) in {elapsed:.2f}s")
                ui_status(task_id, "Completed")
                return True

        except Exception as e:
            if attempt < RETRIES:
                backoff = BACKOFF_BASE * (2 ** (attempt - 1))
                ui_status(task_id, f"Error: {e}. Retrying in {backoff:.1f}s")
                time.sleep(backoff)
            else:
                ui_status(task_id, f"Failed: {e}")
                ui_log(f"[Task {task_id}] Failed after {RETRIES} attempts: {e}")
                return False

# -----------------------------
# Tkinter App
# -----------------------------
class DownloadApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tech Nexa - Live Download Monitor (Enhanced)")
        self.geometry("840x580")
        self.resizable(False, False)

        self.cancel_event = threading.Event()
        self.pool = None
        self.tasks_widgets = {}  # task_id -> {'frame','label','bar'}
        self.running = False
        self.out_dir = os.path.abspath("./downloads")
        os.makedirs(self.out_dir, exist_ok=True)

        self.build_ui()
        self.after(100, self.pump_ui_queue)

    def build_ui(self):
        header = tk.Label(self, text="Threaded Downloads with Progress, Retries, and Cancel",
                          font=("Segoe UI", 14, "bold"))
        header.pack(pady=8)

        # Controls
        ctrl = tk.Frame(self)
        ctrl.pack(pady=4)
        self.start_btn = tk.Button(ctrl, text="Start Downloads", width=18, command=self.start_downloads)
        self.stop_btn = tk.Button(ctrl, text="Stop", width=10, command=self.stop_downloads, state="disabled")
        self.start_btn.grid(row=0, column=0, padx=6)
        self.stop_btn.grid(row=0, column=1, padx=6)

        # Tasks area (scrollable)
        self.tasks_frame = tk.Frame(self, bd=1, relief="sunken")
        self.tasks_frame.pack(padx=10, pady=8, fill="both", expand=False)

        canvas = tk.Canvas(self.tasks_frame, width=800, height=350)
        scrollbar = ttk.Scrollbar(self.tasks_frame, orient="vertical", command=canvas.yview)
        self.inner = tk.Frame(canvas)
        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Log area
        tk.Label(self, text="Logs:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10)
        self.log_area = tk.Text(self, width=108, height=8, state="disabled", bg="#111", fg="#ddd")
        self.log_area.pack(padx=10, pady=6)

        # Prepare task rows
        self.populate_tasks(URLS)

    def populate_tasks(self, urls):
        # Clear if any
        for w in self.inner.winfo_children():
            w.destroy()
        self.tasks_widgets.clear()

        for idx, url in enumerate(urls, start=1):
            frame = tk.Frame(self.inner, bd=0, padx=6, pady=4)
            frame.pack(fill="x")

            label = tk.Label(frame, text=f"Task {idx}: {url}", anchor="w", justify="left")
            label.pack(fill="x")

            bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=760)
            bar["value"] = 0
            bar.pack(pady=2)

            status = tk.Label(frame, text="Pending", anchor="w", fg="#999")
            status.pack(anchor="w")

            self.tasks_widgets[idx] = {"frame": frame, "label": label, "bar": bar, "status": status}

    def append_log(self, text):
        self.log_area.config(state="normal")
        self.log_area.insert("end", text + "\n")
        self.log_area.config(state="disabled")
        self.log_area.see("end")

    def start_downloads(self):
        if self.running:
            return
        self.running = True
        self.cancel_event.clear()
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        self.append_log(f"Starting downloads to: {self.out_dir}")
        t0 = time.perf_counter()
        self.run_start_time = t0

        # Submit tasks
        def submit_all():
            try:
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
                    self.pool = pool
                    futures = []
                    for idx, url in enumerate(URLS, start=1):
                        ui_status(idx, "Queued")
                        futures.append(pool.submit(download_worker, idx, url, self.out_dir, self.cancel_event))

                    # Wait for completion to summarize
                    done_count = 0
                    fail_count = 0
                    for fut in as_completed(futures):
                        ok = fut.result()
                        if ok:
                            done_count += 1
                        else:
                            fail_count += 1

                    elapsed = time.perf_counter() - self.run_start_time
                    ui_log(f"All tasks finished. Success={done_count}, Failed={fail_count}, Time={elapsed:.2f}s")
            finally:
                self.pool = None
                self.running = False
                self.cancel_event.clear()
                ui_queue.put(("run_end",))

        threading.Thread(target=submit_all, daemon=True).start()

    def stop_downloads(self):
        if not self.running:
            return
        if messagebox.askyesno("Stop", "Stop current downloads?"):
            self.cancel_event.set()
            self.append_log("Cancellation requested. Waiting for running tasks...")
            self.stop_btn.config(state="disabled")

    def pump_ui_queue(self):
        try:
            while True:
                item = ui_queue.get_nowait()
                kind = item[0]

                if kind == "log":
                    _, msg = item
                    self.append_log(msg)

                elif kind == "progress":
                    _, task_id, pct, text = item
                    w = self.tasks_widgets.get(task_id)
                    if w:
                        w["bar"]["value"] = pct
                        if text:
                            w["status"].config(text=text, fg="#ddd")

                elif kind == "status":
                    _, task_id, text = item
                    w = self.tasks_widgets.get(task_id)
                    if w:
                        w["status"].config(text=text, fg="#9cf" if "Completed" in text else "#ddd")

                elif kind == "run_end":
                    self.start_btn.config(state="normal")
                    self.stop_btn.config(state="disabled")

        except queue.Empty:
            pass

        # Poll again
        self.after(100, self.pump_ui_queue)

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    # Graceful Ctrl+C in console
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = DownloadApp()
    app.mainloop()
