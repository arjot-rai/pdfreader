import PyPDF2
from gtts import gTTS
import os

def pdf_to_audio_by_toc(pdf_path, output_dir="audio_sections", lang="en"):
    os.makedirs(output_dir, exist_ok=True)
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        outlines = [item for item in reader.outline if hasattr(item, 'title') and hasattr(item, 'page')]
        # Get start pages for each section
        section_starts = [reader.get_destination_page_number(item) for item in outlines]
        section_titles = [item.title for item in outlines]
        section_ends = section_starts[1:] + [len(reader.pages)]  # End is start of next or end of doc

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

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pdfreader.py <path_to_pdf> [output_dir]")
    else:
        pdf_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "audio_sections"
        pdf_to_audio_by_toc(pdf_path, output_dir)