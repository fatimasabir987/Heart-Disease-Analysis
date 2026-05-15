import numpy as np
from PIL import Image
import struct
import os

try:
    import tflite_runtime.interpreter as tflite
    Interpreter = tflite.Interpreter
except ImportError:
    try:
        import tensorflow as tf
        Interpreter = tf.lite.Interpreter
    except ImportError:
        Interpreter = None

interpreter = Interpreter(model_path="heart_disease_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def preprocess_image(image_file):
    img = Image.open(image_file).convert("RGB")
    img = img.resize((224, 224))
    img = np.array(img).astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)
    return img

def predict_image(image_file):
    img = preprocess_image(image_file)
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    return float(output[0][0])
