import os
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    send_from_directory,
)
from werkzeug.utils import secure_filename
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, Sequential
from tensorflow.keras.preprocessing import image

UPLOAD_FOLDER = "static/uploads/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def create_fire_model():
    """Creates the MobileNetV2 model structure."""
    base_model = MobileNetV2(
        input_shape=(224, 224, 3), include_top=False, weights="imagenet"
    )
    base_model.trainable = False

    model = Sequential(
        [
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model


def load_trained_model():
    weights_path = "final_corrected_model.weights.h5"

    if not os.path.exists(weights_path):
        print(f" No se encuentra: {weights_path}")

        print(" Archivos disponibles:")

        for file in os.listdir("."):
            print(f"   - {file}")

        return None

    try:
        model = create_fire_model()

        print(" Cargando pesos entrenados...")

        model.load_weights(weights_path)

        print(" Modelo cargado exitosamente!")

        return model

    except Exception as e:
        print(f" Error cargando el modelo: {e}")

        return None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def process_image(filepath, model, threshold=0.6):
    try:
        if not os.path.exists(filepath):
            print(f"Error: Image file not found at {filepath}")
            return filepath, "Error: Image file not found.", False

        img = image.load_img(filepath, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        prediction = model.predict(img_array, verbose=0)
        confidence = float(prediction[0][0])

        if confidence > threshold:
            fire_detected = True
            text_result = f"Warning: Fire Detected! (Confidence: {confidence:.2%})"
        else:
            fire_detected = False
            confidence_nofire = 1 - confidence
            text_result = (
                f"All Clear: No Fire Detected. (Confidence: {confidence_nofire:.2%})"
            )

        processed_image_path = filepath

        return processed_image_path, text_result, fire_detected

    except Exception as e:
        print(f"Error processing image {filepath}: {e}")
        return filepath, f"Error: Could not process image. {e}", False


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                os.makedirs(app.config["UPLOAD_FOLDER"])
            file.save(filepath)
            processed_image_path, result_text, fire_detected = process_image(
                filepath, fire_model
            )
            processed_filename = os.path.basename(processed_image_path)
            return render_template(
                "result.html",
                image_name=processed_filename,
                result_text=result_text,
                fire_detected=fire_detected,
            )
    return render_template("index.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


fire_model = load_trained_model()

if __name__ == "__main__":
    if fire_model is None:
        print("Could not load model. Exiting.")
        exit()

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=False, port=5000, host="0.0.0.0")