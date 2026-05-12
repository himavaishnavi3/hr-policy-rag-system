import os
import json
import time
import pandas as pd

from docx import Document
from PyPDF2 import PdfReader

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ============================================
# PATHS
# ============================================

UPLOAD_FOLDER = "uploads"

JSON_FILE = "data/hr_policies.json"

# ============================================
# CREATE FOLDERS
# ============================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    "data",
    exist_ok=True
)

# ============================================
# LOAD EXISTING JSON
# ============================================

def load_json():

    if not os.path.exists(JSON_FILE):

        return []

    with open(
        JSON_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

# ============================================
# SAVE JSON
# ============================================

def save_json(data):

    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

# ============================================
# EXTRACT PDF TEXT
# ============================================

def read_pdf(filepath):

    text = ""

    reader = PdfReader(filepath)

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:

            text += extracted + "\n"

    return text

# ============================================
# EXTRACT DOCX TEXT
# ============================================

def read_docx(filepath):

    doc = Document(filepath)

    text = "\n".join([

        para.text

        for para in doc.paragraphs

    ])

    return text

# ============================================
# EXTRACT EXCEL TEXT
# ============================================

def read_excel(filepath):

    excel_data = pd.read_excel(
        filepath,
        sheet_name=None
    )

    full_text = ""

    for sheet_name, df in excel_data.items():

        full_text += f"\nSheet: {sheet_name}\n"

        full_text += df.to_string(index=False)

    return full_text

# ============================================
# PROCESS DOCUMENT
# ============================================

def process_document(filepath):

    print(f"[Processor] Reading {filepath}")

    filename = os.path.basename(filepath)

    title = os.path.splitext(filename)[0]

    text = ""

    # ========================================
    # READ FILE BASED ON TYPE
    # ========================================

    try:

        # PDF
        if filepath.endswith(".pdf"):

            text = read_pdf(filepath)

        # DOCX
        elif filepath.endswith(".docx"):

            text = read_docx(filepath)

        # EXCEL
        elif (
            filepath.endswith(".xlsx")
            or
            filepath.endswith(".xls")
        ):

            text = read_excel(filepath)

        # TXT
        elif filepath.endswith(".txt"):

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as f:

                text = f.read()

        else:

            print("[Processor] Unsupported file")

            return

    except Exception as e:

        print(f"[Processor] Error reading file: {e}")

        return

    # ========================================
    # EMPTY CHECK
    # ========================================

    if not text.strip():

        print("[Processor] Empty text")

        return

    # ========================================
    # LOAD EXISTING JSON
    # ========================================

    data = load_json()

    # ========================================
    # DUPLICATE CHECK
    # ========================================

    for item in data:

        if item["title"] == title:

            print("[Processor] Document already exists")

            return

    # ========================================
    # AUTO ID GENERATION
    # ========================================

    new_id = f"doc{len(data)+1}"

    # ========================================
    # CREATE JSON ENTRY
    # ========================================

    new_entry = {

        "id": new_id,

        "title": title,

        "content": text.strip()

    }

    # ========================================
    # APPEND TO JSON
    # ========================================

    data.append(new_entry)

    save_json(data)

    print(
        f"[Processor] Added to JSON as {new_id}"
    )

# ============================================
# WATCHDOG HANDLER
# ============================================

class DocumentHandler(
    FileSystemEventHandler
):

    def on_created(self, event):

        if event.is_directory:

            return

        filepath = event.src_path

        supported = (

            filepath.endswith(".pdf")
            or
            filepath.endswith(".docx")
            or
            filepath.endswith(".xlsx")
            or
            filepath.endswith(".xls")
            or
            filepath.endswith(".txt")
        )

        if supported:

            print(
                f"[Watcher] New file detected: {filepath}"
            )

            process_document(filepath)

# ============================================
# PROCESS EXISTING FILES
# ============================================

def process_existing_files():

    print(
        "[Startup] Checking existing files..."
    )

    for file in os.listdir(UPLOAD_FOLDER):

        filepath = os.path.join(
            UPLOAD_FOLDER,
            file
        )

        if (
            file.endswith(".pdf")
            or
            file.endswith(".docx")
            or
            file.endswith(".xlsx")
            or
            file.endswith(".xls")
            or
            file.endswith(".txt")
        ):

            process_document(filepath)

# ============================================
# START WATCHER
# ============================================

def start_watching():

    observer = Observer()

    observer.schedule(

        DocumentHandler(),

        UPLOAD_FOLDER,

        recursive=False
    )

    observer.start()

    print(
        "[Watcher] Monitoring uploads folder..."
    )

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        observer.stop()

    observer.join()

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":

    # ========================================
    # PROCESS OLD FILES
    # ========================================

    process_existing_files()

    # ========================================
    # START LIVE WATCHER
    # ========================================

    start_watching()