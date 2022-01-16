import os
from flask import Flask, render_template, request, abort, url_for, send_from_directory, send_file
from werkzeug.utils import secure_filename
from main import AlphaMiner

app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.xes', '.jpeg']
app.config['UPLOAD_PATH'] = 'uploads'   # uploads is the directory name, UPLOAD_PATH is the variable
app.config['DOWNLOAD_PATH'] = 'graph-output'


@app.route('/', methods=['get', 'post'])
def index():
    if request.method=='POST':
        file = request.files['filename']
        filename = secure_filename(file.filename)

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            # if file uploaded doesn't have a valid format
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                return render_template('invalid_upload.html')
            file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            print(f"filename: {filename}")  # ex. L1.xes

            # create al_miner object to process the file uploaded.
            file_path = f"uploads/{filename}" # e.x: uploads/L1.xes
            al_miner = AlphaMiner(file_path)
            # al_miner draws the model and output it to a file.
            al_miner.draw_diagram()
            model_file_path = app.config['DOWNLOAD_PATH'] + f"/{al_miner.filename_without_extension}.png"

            return render_template('upload_state_and_download.html', file_path = model_file_path)
    return render_template('index.html')

@app.route('/display/<path:filepath>')
def display(filepath):
    return send_file(filepath)


@app.route('/download/<path:filepath>')
def download(filepath):
    return send_file(filepath, as_attachment=True)

@app.route('/upload_state_and_download')
def upload_state_and_download():
    return render_template('upload_state_and_download.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact_us.html')


if __name__ == "__main__":
    app.run(debug=True, port=9999)