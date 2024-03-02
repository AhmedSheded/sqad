from flask import Flask, request, jsonify, render_template, send_file
from squad import process_video
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER


@app.route('/upload/', methods=['POST'])
def videoAPI():
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part"})

        file = request.files['file']

        # If the user does not select a file, the browser also
        # submits an empty file without a filename
        if file.filename == '':
            return jsonify({"error": "No selected file"})

        if file:
            # Save the uploaded video to the uploads folder
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(video_path)

            # Process the video with the model
            processed_video_path = process_video(video_path)

            # Save the processed video to the results folder
            result_filename = f"{os.path.splitext(file.filename)[0]}_result.mp4"
            result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)

            os.rename(processed_video_path, result_path)

            return jsonify({"download_link": f"/download/{result_filename}"})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/download/<filename>')
def download_file(filename):
    result_path = os.path.join(app.config['RESULT_FOLDER'], filename)
    return send_file(result_path, as_attachment=True)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    app.run(debug=True)

