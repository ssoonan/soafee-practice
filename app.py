from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import time

from video_publisher import send_frame, setup_fastdds_for_publisher
from video_subscriber import read_frame, setup_fastdds_for_subscriber


app = Flask(__name__)
publisher_participant, datawriter = setup_fastdds_for_publisher()
subscriber_participant, datareader = setup_fastdds_for_subscriber()



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
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 25  # Default FPS if not available
    frame_delay = 1 / fps  # Delay between frames in seconds

    while True:
        success, frame = cap.read()
        if not success:
            # When video ends, break the loop
            break
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        send_frame(datawriter, buffer)
        frame = buffer.tobytes()
        # Yield frame in bytes
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # Delay to match original frame rate
        time.sleep(frame_delay)
    cap.release()


def generate_processed_frames():
    cap = cv2.VideoCapture('uploaded_video.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 25  # Default FPS if not available
    frame_delay = 1 / fps  # Delay between frames in seconds

    while True:
        start_time = time.time()
        success, frame = cap.read()
        if not success:
            # When video ends, break the loop
            break
        # Process the frame (insert your OpenCV processing code here)
        processed_frame = process_frame()
        # Encode processed frame as JPEG
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame = buffer.tobytes()
        # Yield processed frame in bytes
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # Calculate elapsed time and adjust delay
        elapsed_time = time.time() - start_time
        time_to_wait = frame_delay - elapsed_time
        if time_to_wait > 0:
            time.sleep(time_to_wait)
    cap.release()


def process_frame():
    frame = read_frame(datareader)


def process_frame_for_lane_detection(frame):
    # Example processing: convert to grayscale
    processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Convert back to BGR if needed for encoding
    processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
    # You can insert your own processing code here
    return processed_frame


def process_frame_for_object_detection(frame):
    # Example processing: convert to grayscale
    processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Convert back to BGR if needed for encoding
    processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
    # You can insert your own processing code here
    return processed_frame


if __name__ == '__main__':
    app.run(debug=True)
