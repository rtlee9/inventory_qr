from functools import lru_cache
import os
from fpdf import FPDF
import requests
from typing import List, Optional
from collections import deque


cache_get = lru_cache(requests.get)


def gen_qr(url: str, chs: int = 100) -> str:
    """
    Generate a QR code URL for the given input URL.

    Args:
    url (str): The input URL for which to generate the QR code.
    chs (int): The size of the QR code. Defaults to "100x100".

    Returns:
    str: The generated QR code URL.
    """
    base_url = f"https://quickchart.io/qr?size={chs}&text="
    return base_url + url


def generate_qr_pdf(
    qr_code_urls: List[str],
    filename: Optional[str] = "qr_codes.pdf",
    num_cols: int = 6,
    num_rows: int = 8,
    descriptions: Optional[List[str]] = None,
    col_offset: Optional[int] = 31.7,
    row_offset: Optional[int] = 31.7,
    col_start: Optional[int] = 14.8,
    row_start: Optional[int] = 14.8,
    size: Optional[int] = 30,
):
    """
    Generate a PDF containing QR codes from the given list of QR code URLs.

    :param qr_code_urls: A list of URLs pointing to the QR codes.
    :return: None
    """
    from tqdm import trange

    pdf = FPDF(format="letter")
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
            x_pos = col_start + 5 + col * col_offset
            y_pos = row_start + 31 + row * row_offset
            pdf.set_font("Arial", size=8)
            pdf.text(x_pos, y_pos, description)

    # arrange the QR codes in a grid
    row, col = 0, 0
    temp_files = []
    for i in trange(len(qr_code_urls)):
        url = qr_code_urls[i]
        if i >= num_cols * num_rows:  # reset to new page
            add_descriptions()
            row, col = 0, 0
            pdf.add_page()
        row, col = divmod(i, num_cols)
        row %= num_rows
        x_pos = col_start + col * col_offset
        y_pos = row_start + row * row_offset
        response = cache_get(url)
        temp_file = f"temp_qr_{row}_{col}.png"
        with open(temp_file, "wb") as f:
            f.write(response.content)
        pdf.image(temp_file, x=x_pos, y=y_pos, w=size)

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


def gen_qr_range(
    base_shortned_url: str,
    idx_start: int,
    num_codes: int,
    filename: Optional[str],
    is_test: Optional[bool] = False,
    **position_kwargs,
):
    # https://quickchart.io/documentation/qr-codes/
    base_qr_url = "https://quickchart.io/qr?text="
    postfix_range = range(idx_start, idx_start + num_codes)
    base_shortened_urls = [
        f"{base_qr_url}{base_shortned_url}{100 if is_test else i}"
        for i in postfix_range
    ]
    descriptions = (
        [str(i) for i in postfix_range]
        if base_shortned_url.startswith("aws3.link/llqrv")
        else None
    )
    generate_qr_pdf(
        base_shortened_urls,
        filename,
        descriptions=descriptions,
        **{kwarg: val for kwarg, val in position_kwargs.items() if val is not None},
    )


def cli_qr_list():
    import argparse

    parser = argparse.ArgumentParser(description="Generate PDF with QR codes")
    parser.add_argument(
        "-q",
        "--qr-code-urls",
        type=str,
        nargs="+",
        help="URLs for QR codes",
        required=True,
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


def cli_range():
    """
    Generate QR codes for a range of URLs.
    Args:
        base_shortned_url (str): Base URL for the shortened URLs
        idx_start (int): Starting index for the range
        num_codes (int): Number of codes to generate
        filename (str): Filename for the PDF
        ol_offset (int): Offset for the OL
        row_offset (int): Offset for the row
        col_start (int): Starting column index
        row_start (int): Starting row index
        size (int): Size of the QR codes
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate QR codes for a range of URLs."
    )
    parser.add_argument(
        "base_shortned_url", type=str, help="Base URL for the shortened URLs"
    )
    parser.add_argument("idx_start", type=int, help="Starting index for the range")
    parser.add_argument("num_codes", type=int, help="Number of codes to generate")
    parser.add_argument(
        "--filename",
        type=str,
        help="Filename for the PDF",
        required=False,
        default="qr_codes.pdf",
    )
    parser.add_argument(
        "--col_offset", type=float, help="Offset for the OL", required=False
    )
    parser.add_argument(
        "--row_offset", type=float, help="Offset for the row", required=False
    )
    parser.add_argument(
        "--col_start", type=float, help="Starting column index", required=False
    )
    parser.add_argument(
        "--row_start", type=float, help="Starting row index", required=False
    )
    parser.add_argument("--size", type=int, help="Size of the QR codes", required=False)
    parser.add_argument(
        "--test",
        action="store_true",
        help="Flag to indicate if this is a test run",
        required=False,
    )
    args = parser.parse_args()

    gen_qr_range(
        args.base_shortned_url,
        args.idx_start,
        args.num_codes,
        args.filename,
        is_test=args.test,
        col_offset=args.col_offset,
        row_offset=args.row_offset,
        col_start=args.col_start,
        row_start=args.row_start,
        size=args.size,
    )


if __name__ == "__main__":
    cli_range()
