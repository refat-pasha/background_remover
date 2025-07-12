from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
from werkzeug.utils import secure_filename
from rembg import remove
from PIL import Image
import io



app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            # Read the file
            file_data = file.read()
            
            # Check file size
            if len(file_data) > MAX_FILE_SIZE:
                flash('File too large. Maximum size is 16MB.')
                return redirect(url_for('index'))
            
            # Process the image
            input_image = Image.open(io.BytesIO(file_data))
            
            # Remove background
            output_image = remove(input_image)
            
            # Save processed image
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            processed_filename = f"{name}_no_bg.png"
            processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
            
            output_image.save(processed_path)
            
            return render_template('result.html', filename=processed_filename)
            
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or BMP files.')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(PROCESSED_FOLDER, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
