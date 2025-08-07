import os
import requests
import tempfile
import numpy as np
from io import BytesIO
from pdf2image import convert_from_bytes
<<<<<<< HEAD
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from prompt_construct import parsing_res_to_prompt  # adjust if needed
import easyocr
import pinecone
=======
from paddleocr import PaddleOCR, PPStructureV3
import numpy as np
from prompt_construct import parsing_res_to_prompt
import json

ocr1 = PPStructureV3(use_chart_recognition=False, use_formula_recognition=False, use_seal_recognition=False, use_textline_orientation=True)
# ocr2 = PaddleOCR()
>>>>>>> 50893fa16a40eb31294d918f88931423b5eedfa8

# Initialize FastAPI app
app = FastAPI()

# Initialize EasyOCR reader once at startup
# Set gpu=False if you don’t have a CUDA GPU available
reader = easyocr.Reader(['en'], gpu=False)

@app.post("/hackrx/run", response_class=HTMLResponse)
async def text_extraction_pipeline(request: Request):
    # Parse incoming JSON
    data = await request.json()
    url = data.get("url")
    if not url:
        return HTMLResponse("Error: 'url' field is required", status_code=400)

    try:
        # Fetch PDF from URL
        response = requests.get(url, timeout=30)
        response.raise_for_status()

<<<<<<< HEAD
        # Convert PDF to JPEG images in a temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_from_bytes(
                response.content,
                dpi=200,
                fmt="jpeg",
                output_folder=temp_dir,
                poppler_path=r"C:\\poppler-24.08.0\\Library\\bin"
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
        return HTMLResponse("<br><br>".join(all_page_data), status_code=200)

    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}", status_code=500)
=======
images = convert_from_bytes(response.content, first_page=1, last_page=1, poppler_path= r'C:\poppler-24.08.0\Library\bin')

# images[0].show()  # Show the first (or only) image

text = ocr1.predict(np.array(images[0]))
text[0].save_to_json('json_output.json')


with open('json_output.json', 'r', encoding='utf-8') as file:
    json_output = json.load(file)

prompt = parsing_res_to_prompt(json_output["parsing_res_list"])

print(prompt)

>>>>>>> 50893fa16a40eb31294d918f88931423b5eedfa8
