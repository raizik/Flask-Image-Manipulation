from flask import Flask, request, render_template, send_from_directory
import os
import subprocess

MAGICK_EXE = 'C:\Program Files\ImageMagick-7.0.10-Q16-HDRI\magick.exe'

app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = 'static/images'


@app.route("/")
def main():
    app.debug = True
    return render_template('index.html')


# upload and forward to processing page
@app.route("/upload", methods=["POST"])
def upload():

    target = os.path.join(ROOT_DIR, IMAGES_DIR + '/')

    # create image directory if not found
    if not os.path.isdir(target):
        os.mkdir(target)

    # retrieve file from html file-picker
    upload_ = request.files.getlist("file")[0]
    print("File name: {}".format(upload_.filename))
    filename = upload_.filename
    # file support verification
    ext = os.path.splitext(filename)[1]
    if (ext == ".jpg") or (ext == ".png"):
        print("File accepted")
    else:
        return render_template("error.html", message="The selected file is not supported"), 400

    # save file
    destination = "/".join([target, filename])
    print("File saved to to:", destination)
    upload_.save(destination)

    # forward to processing page
    return render_template("processing.html", image_name=filename)


# flip image
@app.route("/flip", methods=["POST"])
def flip():
    if 'horizontal' in request.form['mode']:
        direction = 'flip'
    elif 'vertical' in request.form['mode']:
        direction = 'flop'
    else:
        return render_template("error.html", message="Mode not supported (vertical - horizontal)"), 400
    target = os.path.join(ROOT_DIR, IMAGES_DIR + '/')
    filename = request.form['image']
    src = "/".join([target, filename])

    subprocess.call([MAGICK_EXE, 'convert',  f'{src}', '-'f'{direction}', f'{src}'], shell=True)

    return send_image(filename)


# resize image by angle or pixels
@app.route("/resize", methods=["POST"])
def resize():
    filename = request.form['image']
    angle = request.form['angle']
    height = request.form['height']
    width = request.form['width']

    dir_path = os.path.join(ROOT_DIR, IMAGES_DIR + '/')
    src = "/".join([dir_path, filename])
    if angle is not None:
        subprocess.call([MAGICK_EXE, 'convert', f'{src}',
                         '-resize', f'{angle}''%', f'{src}'], shell=True)
    else:
        subprocess.call([MAGICK_EXE, 'convert', f'{src}',
                         '-resize', f'{height}''x'f'{width}''\!', f'{src}'], shell=True)

    return send_image(filename)


# convert image png <=> jpg
@app.route("/convert", methods=["POST"])
def convert():
    dir_path = os.path.join(ROOT_DIR, IMAGES_DIR + '/')
    filename_ext = request.form['image']

    filename, file_extension = os.path.splitext(filename_ext)

    dst_extension = '.jpg' if file_extension == '.png' else '.png'
    src = "/".join([dir_path, filename_ext])
    new_filename_ext = filename + dst_extension
    dst = "/".join([dir_path, new_filename_ext])
    subprocess.call([MAGICK_EXE, 'convert', f'{src}', f'{dst}'])
    if os.path.isfile(src):
        os.remove(src)
    converted_file = new_filename_ext

    # # fix for browser sometimes changing image's orientation
    # subprocess.call([MAGICK_EXE, 'convert', f'{dst}', '-auto-orient', f'{dst}'])

    # forward converted image to processing page
    return render_template("processing.html", image_name=converted_file)


# extract file from images directory
@app.route('/' + IMAGES_DIR + '/<filename>')
def send_image(filename):
    return send_from_directory(IMAGES_DIR, filename)


if __name__ == "__main__":
    app.run()

