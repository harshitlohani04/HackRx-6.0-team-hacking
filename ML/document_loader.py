import os
import requests
import tempfile
import numpy as np
from pdf2image import convert_from_bytes
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from prompt_construct import parsing_res_to_prompt  # adjust if needed
import easyocr
from vector_db import generate_response
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("API_KEY")
# Initialize FastAPI app
app = FastAPI()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if not auth_header or auth_header != f"Bearer {API_TOKEN}":
            return JSONResponse(
                content={"error": "Unauthorized"},
                status_code=401
            )
        return await call_next(request)

# Add middleware
app.add_middleware(AuthMiddleware)

reader = easyocr.Reader(['en'], gpu=False)

@app.post("/hackrx/run", response_class=HTMLResponse)
async def text_extraction_pipeline(request: Request):
    # Parse incoming JSON
    data = await request.json()
    url = data.get("url")
    questions = data.get("questions")
    if not url:
        return HTMLResponse("Error: 'url' field is required", status_code=400)

    try:
        # Fetch PDF from URL
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        # Convert PDF to JPEG images in a temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_from_bytes(
                response.content,
                dpi=200,
                fmt="jpeg",
                output_folder=temp_dir,
                poppler_path="./bin"
            )

            all_page_data = []
            for page_num, image in enumerate(images, start=1):
                # Convert PIL Image to numpy array (RGB)
                img_array = np.array(image)

                # Perform OCR with EasyOCR
                ocr_results = reader.readtext(img_array)

                # Extract text segments and combine
                texts = [res[1] for res in ocr_results]
                page_text = "\n".join(texts) if texts else "[No text detected]"

                try:
                    prompt = parsing_res_to_prompt({"text": page_text})
                except Exception:
                    prompt = page_text

                all_page_data.append(f"-- Page {page_num} --\n{prompt}")

        # Join all pages into one HTML response
        pdfData = "<br><br>".join(all_page_data)
        llm_response = generate_response(pdfData, questions)
        llm_response_dict = {"answers": llm_response}
        return JSONResponse(content=llm_response_dict, status_code=200)

    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}", status_code=500)

