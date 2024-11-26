from flask import Flask, render_template, Response, request, redirect, url_for
import cv2

app = Flask(__name__)


@app.route('/')
def index():
    # Render the upload page
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    # Get the uploaded file
    file = request.files['file']
    if file:
        # Save the file to the server
        filename = 'uploaded_video.mp4'
        file.save(filename)
        # Redirect to the play page
        return redirect(url_for('play'))
    else:
        return 'No file uploaded', 400


@app.route('/play')
def play():
    # Render the play page
    return render_template('play.html')


@app.route('/video_feed_original')
def video_feed_original():
    # Create a new generator for each request
    return Response(generate_original_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_processed')
def video_feed_processed():
    # Create a new generator for each request
    return Response(generate_processed_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_original_frames():
    cap = cv2.VideoCapture('uploaded_video.mp4')
    while True:
        success, frame = cap.read()
        if not success:
            # When video ends, break the loop
            break
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        # Yield frame in bytes
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()


def generate_processed_frames():
    cap = cv2.VideoCapture('uploaded_video.mp4')
    while True:
        success, frame = cap.read()
        if not success:
            # When video ends, break the loop
            break
        # Process the frame (insert your OpenCV processing code here)
        processed_frame = process_frame(frame)
        # Encode processed frame as JPEG
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame = buffer.tobytes()
        # Yield processed frame in bytes
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()


def process_frame(frame):
    # Example processing: convert to grayscale
    processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # You can insert your own processing code here
    return processed_frame


if __name__ == '__main__':
    app.run(debug=True)
