from flask import Flask, render_template, request, send_file
from img2table.document import Image
from img2table.ocr import PaddleOCR
import cv2
import numpy as np
import io

app = Flask(__name__)
paddle_ocr = PaddleOCR(lang="en", kw={"use_dilation": True})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    cropped_image = request.files['cropped_image']
    # Convert the cropped image data to bytes
    image_bytes = cropped_image.read()
    
    # Convert to grayscale
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Convert back to bytes
    _, img_encoded = cv2.imencode('.jpg', gray_img)
    gray_image_bytes = img_encoded.tobytes()
    
    # Process the grayscale image and generate the Excel file
    image = Image(src=io.BytesIO(gray_image_bytes))
    image.to_xlsx(dest="table.xlsx",
                   ocr=paddle_ocr,
                   implicit_rows=False,
                   borderless_tables=True,
                   min_confidence=50)
    
    # Send back the Excel file
    print("Done")
    return send_file('table.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
