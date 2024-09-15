from flask import Flask, request, jsonify, send_file
import fitz  # PyMuPDF
import os
import threading

app = Flask(__name__)

def remove_watermarks(input_pdf, output_pdf):
    pdf_document = fitz.open(input_pdf)
    
    try:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page.clean_contents()  # Removes watermarks and non-primary content
            
            images = page.get_images(full=True)
            for img in images:
                xref = img[0]
                page.delete_image(xref)

        pdf_document.save(output_pdf)
    finally:
        pdf_document.close()

@app.route('/remove-watermark', methods=['POST'])
def remove_watermark_api():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    input_file = request.files['file']
    output_filename = "no_watermark_" + input_file.filename
    
    temp_dir = "temp_files"
    os.makedirs(temp_dir, exist_ok=True)
    
    input_path = os.path.join(temp_dir, input_file.filename)
    output_path = os.path.join(temp_dir, output_filename)
    
    input_file.save(input_path)
    
    try:
        remove_watermarks(input_path, output_path)
        response = send_file(output_path, as_attachment=True, download_name=output_filename)
        # Removed the thread that deletes the files after serving
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='192.168.2.4', port=5000, debug=True)
