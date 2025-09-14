# Required package: PyPDF2
# pip install PyPDF2

import argparse
import PyPDF2
import sys
import os

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding="utf-8")

def extract_text(pdf_file, output_txt):
    if not os.path.exists(pdf_file):
        print(f"❌ Error: Input file {pdf_file} does not exist.")
        return

    try:
        reader = PyPDF2.PdfReader(pdf_file)
    except Exception as e:
        print(f"❌ Failed to open PDF: {e}")
        return

    text = ""
    total_pages = len(reader.pages)
    print(f"📚 Starting extraction: {total_pages} pages found")

    for i, page in enumerate(reader.pages, 1):
        try:
            text_chunk = page.extract_text()
            if text_chunk:
                text += text_chunk + "\n"
            print(f"✅ Extracted page {i}/{total_pages}")
        except Exception as e:
            print(f"⚠️ Skipping page {i}: {e}")

    if not text.strip():
        print("❌ No text could be extracted from this PDF.")
        return

    try:
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n🎉 Success! PDF text extracted and saved as {output_txt}")
        print(f"📊 Total characters extracted: {len(text)}")
    except Exception as e:
        print(f"❌ Failed to save text: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from a PDF file")
    parser.add_argument("--input", required=True, help="Path to input PDF")
    parser.add_argument("--output", required=True, help="Path to output TXT file")
    args = parser.parse_args()

    extract_text(args.input, args.output)
