import os
from fpdf import FPDF
import requests
from typing import List, Optional


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


def generate_qr_pdf(qr_code_urls: List[str], filename: Optional[str] = "qr_codes.pdf"):
    """
    Generate a PDF containing QR codes from the given list of QR code URLs.

    :param qr_code_urls: A list of URLs pointing to the QR codes.
    :return: None
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # arrange the QR codes in a grid of 8 rows x 6 columns
    row, col = 0, 0
    temp_files = []
    for url in qr_code_urls:
        if col == 6:
            col = 0
            row += 1
        x_pos = 10 + col * 30
        y_pos = 10 + row * 30
        print(url, col, row, x_pos, y_pos)
        response = requests.get(url)
        temp_file = f"temp_qr_{row}_{col}.png"
        with open(temp_file, "wb") as f:
            f.write(response.content)
        pdf.image(temp_file, x=x_pos, y=y_pos, w=40)
        temp_files.append(temp_file)
        col += 1

    # clean up temporary files
    for file in temp_files:
        os.remove(file)

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
