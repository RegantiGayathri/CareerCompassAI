from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF resume.

    Parameters:
        pdf_path: Path of the uploaded PDF file

    Returns:
        Extracted resume text
    """

    text = ""

    try:

        # Open the PDF
        reader = PdfReader(pdf_path)

        # Read every page
        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text
                text += "\n"

        # Remove unnecessary spaces
        return text.strip()

    except Exception as e:

        raise Exception(
            f"Unable to extract text from PDF: {e}"
        )