import os
import re
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import json

# ---------------------- Helper Functions ----------------------

def ocr_pdf(file_path):
    """Convert PDF pages to images and extract text using OCR."""
    text = ""
    pages = convert_from_path(file_path)
    for page_image in pages:
        page_text = pytesseract.image_to_string(page_image)
        if page_text.strip():
            text += page_text + "\n"
    return text

def split_numbered_clauses(text):
    """
    Split OCR text into sections with sub-clauses.
    Each section heading (e.g., 13-63-101 Definitions.) becomes a chunk,
    including all subsequent clauses until the next section heading.
    """
    clauses = []
    current_section_text = ""
    current_heading = None
    section_heading_pattern = re.compile(r"^\d{2,3}-\d{2,3}-\d{3}.*\.$", re.MULTILINE)

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if section_heading_pattern.match(line):
            if current_section_text:
                clauses.append((current_section_text.strip(), current_heading))
            current_heading = line
            current_section_text = ""
        else:
            current_section_text += " " + line if current_section_text else line

    if current_section_text:
        clauses.append((current_section_text.strip(), current_heading))

    return clauses

def split_paragraphs(text, max_chunk_size=800):
    """Regular paragraph splitting with optional max chunk size."""
    lines = text.split("\n")
    paragraphs = []
    current_para = []

    for line in lines:
        line = line.strip()
        if not line:
            if current_para:
                paragraph_text = " ".join(current_para)
                paragraphs.extend(split_long_paragraph(paragraph_text, max_chunk_size))
                current_para = []
        else:
            current_para.append(line)

    if current_para:
        paragraph_text = " ".join(current_para)
        paragraphs.extend(split_long_paragraph(paragraph_text, max_chunk_size))

    return paragraphs

def split_long_paragraph(paragraph, max_chunk_size):
    if len(paragraph) <= max_chunk_size:
        return [paragraph]
    sentences = re.split(r'(?<=[.;])\s+', paragraph)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def assign_metadata(paragraphs_or_clauses, source_file, numbered=False):
    """Assign metadata to each paragraph or clause."""
    enriched = []

    for text, heading in paragraphs_or_clauses:
        metadata = {"source_file": source_file}
        if numbered and heading:
            metadata["section_heading"] = heading
            sec_match = re.match(r"(\d{2,3}-\d{2,3}-\d{3})", heading)
            if sec_match:
                metadata["section_number"] = sec_match.group(1)
        enriched.append((text, metadata))

    return enriched

# ---------------------- Main Loop ----------------------

file_path = "/Users/zerongpeh/Desktop/Y4S1/hackathon_documents"
output_file = "chunks_output.json"
all_chunks = []

for filename in os.listdir(file_path):
    if filename.endswith(".pdf"):
        file_full_path = os.path.join(file_path, filename)
        print(f"\nProcessing {filename} ...")

        if filename.lower() == "utah_regulation_act.pdf":
            # OCR + numbered clause splitting
            text = ocr_pdf(file_full_path)
            chunks = split_numbered_clauses(text)
            enriched_chunks = assign_metadata(chunks, filename, numbered=True)
        else:
            # Regular PDF extraction + paragraph splitting
            doc = fitz.open(file_full_path)
            text = ""
            for page in doc:
                text += page.get_text("text")
            paragraphs = [(p, None) for p in split_paragraphs(text)]
            enriched_chunks = assign_metadata(paragraphs, filename, numbered=False)
            all_chunks.extend(enriched_chunks)

        # print(f"Total chunks: {len(enriched_chunks)}")
        # # Inspect first few chunks
        # for i, (chunk_text, meta) in enumerate(enriched_chunks[:5], 1):
        #     print(f"\n--- Chunk {i} ---")
        #     print(chunk_text[:1000], "...")
        #     print("Metadata:", meta)

# Save all chunks to a JSON file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2, ensure_ascii=False)