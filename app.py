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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    This is where your neural network and classical image processing will go.
    For now, it just returns the original image's path and a simple message.
    """
    # TODO: Replace this placeholder logic with your actual image processing code.
    # For example, you would load the image, run it through your model, save the new image, and generate text.

    # As a placeholder, we'll say the processed image is the same as the original one.
    processed_image_path = filepath

    # As a placeholder, create a simple text result.
    text_result = "Image processed successfully! (This is a placeholder)"

    # Return the path to the resulting image and the text description.
    return processed_image_path, text_result

# --- Routes ---

# Define the main route for the web page, which supports both GET (viewing the page) and POST (submitting the form) methods.
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # Check if the request method is POST, which means the user has submitted the form.
    if request.method == 'POST':
        # Check if the 'file' key exists in the files part of the request.
        if 'file' not in request.files:
            # If no file part, redirect the user back to the upload page.
            return redirect(request.url)

        # Get the file object from the request.
        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file part with no filename.
        if file.filename == '':
            # If the filename is empty, redirect the user back to the upload page.
            return redirect(request.url)

        # If a file exists and its extension is allowed...
        if file and allowed_file(file.filename):
            # Make the filename safe by removing any dangerous characters (like '..', '/', etc.).
            filename = secure_filename(file.filename)

            # Create the full path to save the file by joining the upload folder path and the secure filename.
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Save the uploaded file to the filesystem at the specified path.
            file.save(filepath)

            # Call our placeholder function to "process" the image.
            processed_image_path, result_text = process_image(filepath)

            # Get just the filename (without the folder path) from the processed image path.
            processed_filename = os.path.basename(processed_image_path)

            # Render the 'result.html' template, passing the processed filename and result text to it.
            return render_template('result.html', image_name=processed_filename, result_text=result_text)

    # If the request method is GET (the user is just visiting the page), render the main index.html template.
    return render_template('index.html')

# Define a route to serve the images from the upload folder.
# This allows the HTML <img src="..."> tag to access the files.
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Send the requested file from the UPLOAD_FOLDER directory.
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# This block checks if the script is being run directly (not imported as a module).
if __name__ == '__main__':
    # Check if the upload directory exists.
    if not os.path.exists(UPLOAD_FOLDER):
        # If it doesn't exist, create it.
        os.makedirs(UPLOAD_FOLDER)
    # Start the Flask development server with debug enabled so errors are shown (use False in production).
    app.run(debug=True, port=5000)