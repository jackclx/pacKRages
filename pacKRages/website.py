# from flask import Flask, request, redirect, url_for
# from werkzeug.utils import secure_filename
# import os

# app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# print(f"Upload folder is set to: {app.config['UPLOAD_FOLDER']}")
# print(f"Current working directory: {os.getcwd()}")

# upload_counter = 0  # Initialize the counter

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     global upload_counter  # Use the global counter variable
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             upload_counter += 1  # Increment the counter
#             if upload_counter == 6:  # Reset the counter if it reaches 6
#                 upload_counter = 1
#             return redirect(url_for('upload_file', filename=filename, counter=upload_counter))
#     return '''
#     <!doctype html>
#     <title>Upload new File</title>
#     <h1>Upload new File</h1>
#     <form method=post enctype=multipart/form-data>
#       <input type=file name=file>
#       <input type=submit value=Upload>
#     </form>
#     <p>Please put inside box: {}</p>  <!-- Display the current count -->
#     '''.format(upload_counter)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=4000, debug=True)

from flask import Flask, request, redirect, url_for, render_template  # Import render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print(f"Upload folder is set to: {app.config['UPLOAD_FOLDER']}")
print(f"Current working directory: {os.getcwd()}")

upload_counter = 0  # Initialize the counter

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global upload_counter  # Use the global counter variable
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'fileToUpload' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['fileToUpload']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            upload_counter += 1  # Increment the counter
            if upload_counter == 6:  # Reset the counter if it reaches 6
                upload_counter = 1
            return redirect(url_for('upload_file', counter=upload_counter))
    return render_template('home.html', counter=upload_counter)  # Render the template



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
