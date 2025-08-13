import PyPDF2
from gtts import gTTS
import os
import re
import time  # Add this import

def extract_text_by_page_range(reader, start_page=None, end_page=None):
    text = ""
    total_pages = len(reader.pages)
    start = start_page if start_page is not None else 0
    end = end_page if end_page is not None else total_pages
    for page_num in range(start, min(end, total_pages)):
        page_text = reader.pages[page_num].extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def pdf_to_audio(pdf_path, output_dir="audio_sections", lang="en", start_page=None, end_page=None, delay=10):
    os.makedirs(output_dir, exist_ok=True)
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        outlines = [item for item in getattr(reader, "outline", []) if hasattr(item, 'title') and hasattr(item, 'page')]
        if outlines:
            # Use TOC/bookmarks
            section_starts = [reader.get_destination_page_number(item) for item in outlines]
            section_titles = [item.title for item in outlines]
            section_ends = section_starts[1:] + [len(reader.pages)]
            for idx, (title, start, end) in enumerate(zip(section_titles, section_starts, section_ends), start=1):
                section_text = ""
                for page_num in range(start, end):
                    page_text = reader.pages[page_num].extract_text()
                    if page_text:
                        section_text += page_text + "\n"
                if section_text.strip():
                    tts = gTTS(text=section_text, lang=lang)
                    safe_title = title.replace(" ", "_").replace("/", "_")
                    output_path = os.path.join(output_dir, f"{safe_title}.mp3")
                    tts.save(output_path)
                    print(f"Saved {output_path}")
                    time.sleep(delay)  # Delay between requests
        else:
            # No TOC: Extract all text (or page range) into one audio file
            text = extract_text_by_page_range(reader, start_page, end_page)
            if text.strip():
                tts = gTTS(text=text, lang=lang)
                output_path = os.path.join(output_dir, "full_document.mp3")
                tts.save(output_path)
                print(f"Saved {output_path}")

if __name__ == "__main__":
    import sys
    # Usage: python pdfreader.py <path_to_pdf> [output_dir] [start_page] [end_page] [delay]
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "audio_sections"
    start_page = int(sys.argv[3]) if len(sys.argv) > 3 else None
    end_page = int(sys.argv[4]) if len(sys.argv) > 4 else None
    delay = int(sys.argv[5]) if len(sys.argv) > 5 else 2

    if not pdf_path:
        print("Usage: python pdfreader.py <path_to_pdf> [output_dir] [start_page] [end_page] [delay]")
    else:
        pdf_to_audio(pdf_path, output_dir, start_page=start_page, end_page=end_page)