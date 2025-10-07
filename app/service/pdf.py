import os
import subprocess
import tempfile
from http import HTTPStatus
from io import BytesIO
from pathlib import Path
from typing import List

import img2pdf
import pymupdf
from PIL import Image
from fastapi import HTTPException
from pypdf import PdfWriter, PdfReader


def extract_cover_from_pdf(pdf_bytes):
    doc = pymupdf.open(stream=pdf_bytes)
    page = doc[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(1, 1))
    result = pix.tobytes()

    return result


def convert_image_to_pdf(img_byte: bytes):
    img = Image.open(BytesIO(img_byte))
    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])  # usa o alpha como máscara
        img = background
    else:
        img = img.convert("RGB")  # garante que é RGB
    writer = PdfWriter()
    output = BytesIO()
    img.save(output, format="JPEG")
    img_byte = output.getvalue()
    with Image.open(BytesIO(img_byte)) as img:
        width, height = img.size
        if width > height:
            layout_fun = img2pdf.get_layout_fun(
                (img2pdf.mm_to_pt(297), img2pdf.mm_to_pt(210))
            )
        else:
            layout_fun = img2pdf.get_layout_fun(
                (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
            )

        writer.append(BytesIO(img2pdf.convert(img_byte, layout_fun=layout_fun)))
        output_buffer = BytesIO()
        writer.write(output_buffer)
        return output_buffer.getvalue()


def convert_doc_to_pdf(pdf_bytes, file_extension):
    with tempfile.TemporaryDirectory() as tmpdir:
        document_path = os.path.join(tmpdir, f'document.{file_extension}')
        with open(document_path, 'wb') as f:
            f.write(pdf_bytes)
        args = ['soffice', '--headless', '--convert-to', 'pdf', '--outdir', tmpdir, document_path]
        try:
            subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
            pdf_path = os.path.join(tmpdir, f'document.pdf')
            return Path(pdf_path).read_bytes()
        except Exception as e:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail='Could not convert file to pdf')


def merge_pdfs(pdfs: List[bytes]) -> bytes:
    pdf_writer = PdfWriter()
    for pdf in pdfs:
        if not pdf:
            raise Exception('PDF is empty')
        pdf_reader = PdfReader(BytesIO(pdf))
        pdf_writer.append(pdf_reader)
    out_buffer = BytesIO()
    pdf_writer.write(out_buffer)
    bytes_pdf = out_buffer.getvalue()
    out_buffer.close()
    return bytes_pdf
