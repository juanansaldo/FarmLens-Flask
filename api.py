from flask import Flask, request, send_from_directory, jsonify, abort, after_this_request
from flask_executor import Executor
import time
import cv2
import os

from inference.core.interfaces.stream.sinks import VideoFileSink
from inference import InferencePipeline

import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
executor = Executor(app)

# Folder setup for storing and serving video files
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit

def resize_and_change_framerate(input_path, output_path, width=600, height=600, new_fps=24, writer_type="mp4v"):
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*writer_type)
    out = cv2.VideoWriter(output_path, fourcc, new_fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, (width, height))
        out.write(resized_frame)

    cap.release()
    out.release()

def ensure_directories_exist():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

ensure_directories_exist()

@app.route('/')
def home():
    return "Flask heroku app."

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "processed.mp4")
        file.save(filepath)

        output_filepath = os.path.join(app.config['PROCESSED_FOLDER'], "output.avi")

        if os.path.isfile(output_filepath):
            try:
                os.remove(output_filepath)
                print(f"File {output_filepath} removed successfully.")
            except Exception as e:
                print(f"Error removing file {output_filepath}: {e}")

        resize_and_change_framerate(filepath, processed_filepath)

        executor.submit(process_video, processed_filepath)  # Process video asynchronously
        return jsonify({"message": "File successfully uploaded", "filepath": processed_filepath}), 200

    return jsonify({"error": "File upload failed"}), 500

def process_video(video_path):
    try:
        output_file_name = os.path.join(app.config['PROCESSED_FOLDER'], 'output.avi')
        video_sink = VideoFileSink.init(video_file_name=output_file_name)
        pipeline = InferencePipeline.init(
            api_key=os.getenv('ROBOFLOW_API_KEY'),
            model_id=os.getenv('ROBOFLOW_MODEL_ID'),
            video_reference=video_path,
            on_prediction=video_sink.on_prediction
        )

        pipeline.start()
        pipeline.join()
        video_sink.release()
    except Exception as e:
        print("Error during video processing:", str(e))

@app.route('/download/<filename>', methods=['GET'])
def download_video(filename):
    output_filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    upload_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "capture.mp4")
    processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "processed.mp4")

    @after_this_request
    def remove_file(response):
        try:
            os.remove(upload_filepath)
            os.remove(processed_filepath)
        except Exception as error:
            app.logger.error("Error removing files", exc_info=error)
        return response

    if os.path.isfile(output_filepath):
        return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)
    else:
        return abort(404, description="File not found")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
