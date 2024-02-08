import os
from fpdf import FPDF
from PyPDF2 import PdfWriter, PdfReader
import requests
from typing import List, Optional, Iterable
from collections import deque


def gen_qr(url: str) -> str:
    """
    Generate a QR code URL for the given input URL.

    Args:
    url (str): The input URL for which to generate the QR code.

    Returns:
    str: The generated QR code URL.
    """
    base_url = "https://chart.googleapis.com/chart?cht=qr&choe=UTF-8&chs=100x100&chl="
    return base_url + url


def generate_qr_pdf(
    qr_code_urls: List[str],
    filename: Optional[str] = "qr_codes.pdf",
    num_cols: int = 6,
    num_rows: int = 8,
    descriptions: Optional[List[str]] = None,
):
    """
    Generate a PDF containing QR codes from the given list of QR code URLs.

    :param qr_code_urls: A list of URLs pointing to the QR codes.
    :return: None
    """
    pdf = FPDF()
    pdf.add_page()

    if not descriptions:
        descriptions = deque(qr_code_urls)
    else:
        assert len(descriptions) == len(
            qr_code_urls
        ), "Number of descriptions should match the number of QR codes"
        descriptions = deque(descriptions)

    def add_descriptions():
        """
        Add descriptions underneath each QR code in the PDF. Run once per page
        """
        for i in range(num_rows * num_cols):
            if not descriptions:
                return
            description = descriptions.popleft()
            # include the filename under each QR code
            row, col = divmod(i, num_cols)
            x_pos = 15 + col * 30
            y_pos = 44 + row * 30
            pdf.set_font("Arial", size=3)
            pdf.text(x_pos, y_pos, description)

    # arrange the QR codes in a grid
    row, col = 0, 0
    temp_files = []
    for i, url in enumerate(qr_code_urls):
        if i >= num_cols * num_rows:  # reset to new page
            add_descriptions()
            row, col = 0, 0
            pdf.add_page()
        row, col = divmod(i, num_cols)
        row %= num_rows
        x_pos = 10 + col * 30
        y_pos = 10 + row * 30
        response = requests.get(url)
        temp_file = f"temp_qr_{row}_{col}.png"
        with open(temp_file, "wb") as f:
            f.write(response.content)
        pdf.image(temp_file, x=x_pos, y=y_pos, w=40)

        temp_files.append(temp_file)

    # add descriptions under qr codes for the last page
    add_descriptions()

    # clean up temporary files
    for file in temp_files:
        try:
            os.remove(file)
        except FileNotFoundError as e:
            pass

    pdf.output(filename)
    print(f"QR codes generated and saved to {filename}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate PDF with QR codes")
    parser.add_argument(
        "--qr-code-urls", type=str, nargs="+", help="URLs for QR codes", required=True
    )
    parser.add_argument(
        "--filename",
        type=str,
        help="Filename for the PDF",
        required=False,
        default="qr_codes.pdf",
    )
    args = parser.parse_args()
    generate_qr_pdf(args.qr_code_urls, args.filename)


if __name__ == "__main__":
    main()
