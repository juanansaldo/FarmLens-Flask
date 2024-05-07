from flask import Flask, request, send_from_directory, jsonify, abort
import os

from inference.core.interfaces.stream.sinks import VideoFileSink
from inference import InferencePipeline

app = Flask(__name__)

# Folder setup for storing and serving video files
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

def ensure_directories_exist():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

ensure_directories_exist()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit

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
        file.save(filepath)
        process_video(filepath)  # Synchronously process the video
        return jsonify({"message": "File successfully uploaded", "filepath": filepath}), 200

    return jsonify({"error": "File upload failed"}), 500

def process_video(video_path):
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

@app.route('/download/<filename>', methods=['GET'])
def download_video(filename):
    filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.isfile(filepath):
        return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)
    else:
        return abort(404, description="File not found")

@app.route('/delete_files', methods=['GET'])
def delete_files():
    files_deleted = []
    paths_to_check = [app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER']]
    for path in paths_to_check:
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                files_deleted.append(file_path)

    if files_deleted:
        return jsonify({"message": "Files deleted", "deleted_files": files_deleted})
    else:
        return jsonify({"message": "No files found to delete"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
