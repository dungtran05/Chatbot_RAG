import io

import fitz
from PIL import Image
from rapidocr_onnxruntime import RapidOCR


class PDFOCRService:
    def __init__(self):
        self.engine = RapidOCR()

    def extract_text(self, file_bytes: bytes) -> str:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        native_text = "\n".join(page.get_text("text") for page in doc)
        if len(native_text.strip()) > 200:
            return native_text

        pages_text: list[str] = []
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            result, _ = self.engine(image)
            if not result:
                continue
            page_text = "\n".join(item[1] for item in result)
            pages_text.append(page_text)
        return "\n\n".join(pages_text)


pdf_ocr_service = PDFOCRService()

