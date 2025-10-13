# Import the necessary libraries.
import os  # Used for interacting with the operating system, like creating directories and file paths.

# From the flask library, import the main Flask class, and functions for handling requests, rendering templates, etc.
from flask import Flask, request, render_template, redirect, url_for, send_from_directory

# From werkzeug (a library Flask uses), import a function to secure filenames.
from werkzeug.utils import secure_filename

# --- Configuration ---

# Define the path where uploaded files will be stored. 'static/uploads/' is a common convention.
UPLOAD_FOLDER = 'static/uploads/'

# Define a set of allowed file extensions for security.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create an instance of the Flask class. '__name__' is a special variable that gets the name of the current Python module.
app = Flask(__name__)

# Configure the Flask app with the upload folder path.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set the maximum file size for uploads to 16 megabytes. This prevents users from uploading overly large files.
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# --- Helper Function ---

# Define a function to check if a filename has an allowed extension.
def allowed_file(filename):
    """Checks if the file extension is allowed."""
    # Return True if a '.' is in the filename AND the part after the last '.' (the extension) is in our set of allowed extensions.
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Image Processing Placeholder ---

# Define the function that will eventually contain your image processing logic.
def process_image(filepath):
    """
    This is where your neural network will go.
    It should return the image path, a text message, and a boolean for the result.
    """
    # --- TODO: Replace this simulation with your actual NN model ---
    # For example:
    # prediction = my_fire_detection_model.predict(filepath)
    # fire_detected = prediction > 0.5 # Assuming the model outputs a probability
    
    # --- Simulation Logic ---
    # We'll simulate the result based on the uploaded filename for testing.
    filename = os.path.basename(filepath).lower()
    if 'fire' in filename:
        fire_detected = True
        text_result = "Warning: Fire Detected!"
    else:
        fire_detected = False
        text_result = "All Clear: No Fire Detected."
    # --- End of Simulation Logic ---
        
    processed_image_path = filepath # For now, we show the original image
    
    # Return THREE values now: the path, the text, and the boolean result
    return processed_image_path, text_result, fire_detected

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # ... (keep the file checking and saving logic exactly the same) ...
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the image and get all THREE return values
            processed_image_path, result_text, fire_detected = process_image(filepath)
            
            processed_filename = os.path.basename(processed_image_path)
            
            # Pass the new 'fire_detected' boolean to the template
            return render_template(
                'result.html', 
                image_name=processed_filename, 
                result_text=result_text,
                fire_detected=fire_detected  # <-- NEW
            )
            
    return render_template('index.html')

# ... (keep the rest of the file the same) ...

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
# This block checks if the script is being run directly (not imported as a module).
if __name__ == '__main__':
    # Check if the upload directory exists.
    if not os.path.exists(UPLOAD_FOLDER):
        # If it doesn't exist, create it.
        os.makedirs(UPLOAD_FOLDER)
    # Start the Flask development server with debug enabled so errors are shown (use False in production).
    app.run(debug=True, port=5000)