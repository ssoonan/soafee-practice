from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import time

from lane_detection_subscriber import LaneDetectionSubscriber
from lib.lane_detector import draw_lane_lines, fill_lane_area
from object_detection_subscriber import ObjectDetectionSubscriber
from video_publisher import send_frame, setup_fastdds_for_publisher
from video_subscriber import setup_fastdds_for_subscriber


app = Flask(__name__)
publisher_participant, datawriter = setup_fastdds_for_publisher()
subscriber_participant, datareader = setup_fastdds_for_subscriber()

lane_detection_subscriber = LaneDetectionSubscriber()
object_detection_subscriber = ObjectDetectionSubscriber()


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
        send_frame(datawriter, frame)
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
        processed_frame = process_frame(frame)
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


def process_frame(frame):
    frame = process_frame_for_lane_detection(frame)
    frame = process_frame_for_object_detection(frame)
    return frame


def process_frame_for_lane_detection(frame):
    lane_data = lane_detection_subscriber.get_latest_data()
    if lane_data is None:
        return frame
    # Draw the lane lines
    left_line = ((lane_data.left_lane().x1(), lane_data.left_lane().y1()),
                 (lane_data.left_lane().x2(), lane_data.left_lane().y2()))
    right_line = ((lane_data.right_lane().x1(), lane_data.right_lane().y1()),
                  (lane_data.right_lane().x2(), lane_data.right_lane().y2()))

    # Draw the detected lines on top of the filled frame
    filled_frame = fill_lane_area(frame, left_line, right_line)
    result_frame = draw_lane_lines(filled_frame, [left_line, right_line])
    return result_frame


def process_frame_for_object_detection(frame):
    """
    Process a frame with object detection data and overlay the results.

    :param frame: OpenCV frame
    :return: Processed frame with bounding boxes and class labels
    """
    # Get the latest object detection data
    object_detection_data = object_detection_subscriber.get_latest_data()
    if object_detection_data is None:
        return frame

    # Iterate over detected bounding boxes
    for box in object_detection_data.boxes():
        x = box.x()
        y = box.y()
        width = box.width()
        height = box.height()
        class_name = box.class_name()

        # Draw bounding box
        top_left = (x, y)
        bottom_right = (x + width, y + height)
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

        # Draw class label
        label_position = (x, y - 10)  # Slightly above the bounding box
        cv2.putText(frame, class_name, label_position, cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (36, 255, 12), 2)

    return frame


if __name__ == '__main__':
    app.run(debug=True)
