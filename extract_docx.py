import zipfile
import re
import sys
import os

def extract_text_from_docx(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as docx:
            xml_content = docx.read('word/document.xml').decode('utf-8')
            # Extract text from <w:t> tags
            text_parts = re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml_content)
            return "".join(text_parts)
    except Exception as e:
        return f"Error reading {docx_path}: {e}"

file_path = r"c:\Users\DELL\OneDrive\Desktop\High-Frequency-Limit-Order-Book-Dynamics-PERSONAL\project guide\GitHub_Contribution_Plan_4Days.docx"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    text = extract_text_from_docx(file_path)
    with open("extracted_plan.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Text extracted to extracted_plan.txt")
