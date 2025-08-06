import requests
from io import BytesIO
from pdf2image import convert_from_bytes

# Step 1: Download the PDF
# url = r'https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D'
url = "https://hackrx.blob.core.windows.net/assets/hackrx_6/policies/EDLHLGA23009V012223.pdf?sv=2023-01-03&st=2025-07-30T06%3A46%3A49Z&se=2025-09-01T06%3A46%3A00Z&sr=c&sp=rl&sig=9szykRKdGYj0BVm1skP%2BX8N9%2FRENEn2k7MQPUp33jyQ%3D"


response = requests.get(url)


images = convert_from_bytes(response.content, dpi=300, first_page=1, last_page=1, poppler_path= r'C:\poppler-24.08.0\Library\bin')

images[0].show()  # Show the first (or only) image