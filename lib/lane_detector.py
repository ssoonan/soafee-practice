import numpy as np
import cv2


def region_selection(image):
    """
    Determine and cut the region of interest in the input image.
    Parameters:
            image: we pass here the output from canny where we have 
            identified edges in the frame
    """
    # create an array of the same size as of the input image
    mask = np.zeros_like(image)
    # if you pass an image with more then one channel
    if len(image.shape) > 2:
        channel_count = image.shape[2]
        ignore_mask_color = (255,) * channel_count
    # our image only has one channel so it will go under "else"
    else:
        # color of the mask polygon (white)
        ignore_mask_color = 255
    # creating a polygon to focus only on the road in the picture
    # we have created this polygon in accordance to how the camera was placed
    rows, cols = image.shape[:2]
    bottom_left = [cols * 0.1, rows * 0.95]
    top_left = [cols * 0.4, rows * 0.6]
    bottom_right = [cols * 0.9, rows * 0.95]
    top_right = [cols * 0.6, rows * 0.6]
    vertices = np.array(
        [[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
    # filling the polygon with white color and generating the final mask
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    # performing Bitwise AND on the input image and mask to get only the edges on the road
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


def hough_transform(image):
    """
    Determine and cut the region of interest in the input image.
    Parameter:
            image: grayscale image which should be an output from the edge detector
    """
    # Distance resolution of the accumulator in pixels.
    rho = 1
    # Angle resolution of the accumulator in radians.
    theta = np.pi/180
    # Only lines that are greater than threshold will be returned.
    threshold = 20
    # Line segments shorter than that are rejected.
    minLineLength = 20
    # Maximum allowed gap between points on the same line to link them
    maxLineGap = 500
    # function returns an array containing dimensions of straight lines
    # appearing in the input image
    return cv2.HoughLinesP(image, rho=rho, theta=theta, threshold=threshold,
                           minLineLength=minLineLength, maxLineGap=maxLineGap)


def average_slope_intercept(lines):
    """
    Find the slope and intercept of the left and right lanes of each image.
    Parameters:
            lines: output from Hough Transform
    """
    left_lines = []  # (slope, intercept)
    left_weights = []  # (length,)
    right_lines = []  # (slope, intercept)
    right_weights = []  # (length,)

    for line in lines:
        for x1, y1, x2, y2 in line:
            if x1 == x2:
                continue
            # calculating slope of a line
            slope = (y2 - y1) / (x2 - x1)
            # calculating intercept of a line
            intercept = y1 - (slope * x1)
            # calculating length of a line
            length = np.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))
            # slope of left lane is negative and for right lane slope is positive
            if slope < 0:
                left_lines.append((slope, intercept))
                left_weights.append((length))
            else:
                right_lines.append((slope, intercept))
                right_weights.append((length))
    #
    left_lane = np.dot(left_weights, left_lines) / \
        np.sum(left_weights) if len(left_weights) > 0 else None
    right_lane = np.dot(right_weights, right_lines) / \
        np.sum(right_weights) if len(right_weights) > 0 else None
    return left_lane, right_lane


def pixel_points(y1, y2, line):
    """
    Converts the slope and intercept of each line into pixel points.
            Parameters:
                    y1: y-value of the line's starting point.
                    y2: y-value of the line's end point.
                    line: The slope and intercept of the line.
    """
    if line is None:
        return None
    slope, intercept = line
    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)
    y1 = int(y1)
    y2 = int(y2)
    return ((x1, y1), (x2, y2))


def lane_lines(image, lines):
    """
    Create full lenght lines from pixel points.
            Parameters:
                    image: The input test image.
                    lines: The output lines from Hough Transform.
    """
    left_lane, right_lane = average_slope_intercept(lines)
    y1 = image.shape[0]
    y2 = y1 * 0.6
    left_line = pixel_points(y1, y2, left_lane)
    right_line = pixel_points(y1, y2, right_lane)
    return left_line, right_line


def draw_lane_lines(image, lines, color=[255, 0, 0], thickness=12):
    """
    Draw lines onto the input image.
            Parameters:
                    image: The input test image (video frame in our case).
                    lines: The output lines from Hough Transform.
                    color (Default = red): Line color.
                    thickness (Default = 12): Line thickness. 
    """
    line_image = np.zeros_like(image)
    for line in lines:
        if line is not None:
            cv2.line(line_image, *line, color, thickness)
    return cv2.addWeighted(image, 1.0, line_image, 1.0, 0.0)


def frame_processor(image):
    """
    Process the input frame to detect lane lines.
    Parameters:
            image: image of a road where one wants to detect lane lines
            (we will be passing frames of video to this function)
    """
    # convert the RGB image to Gray scale
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # applying gaussian Blur which removes noise from the image
    # and focuses on our region of interest
    # size of gaussian kernel
    kernel_size = 5
    # Applying gaussian blur to remove noise from the frames
    blur = cv2.GaussianBlur(grayscale, (kernel_size, kernel_size), 0)
    # first threshold for the hysteresis procedure
    low_t = 50
    # second threshold for the hysteresis procedure
    high_t = 150
    # applying canny edge detection and save edges in a variable
    edges = cv2.Canny(blur, low_t, high_t)
    # since we are getting too many edges from our image, we apply
    # a mask polygon to only focus on the road
    # Will explain Region selection in detail in further steps
    region = region_selection(edges)
    # Applying hough transform to get straight lines from our image
    # and find the lane lines
    # Will explain Hough Transform in detail in further steps
    hough = hough_transform(region)
    # lastly we draw the lines on our resulting frame and return it as output
    result = draw_lane_lines(image, lane_lines(image, hough))
    return result


def process_frame_for_coordinates(frame):
    """
    Process a single frame to extract lane line points.
    Parameters:
        frame: Input video frame (OpenCV image).
    Returns:
        List of lane line points (left and right lanes).
    """
    # Convert the frame to grayscale and apply Gaussian blur
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kernel_size = 5
    blur = cv2.GaussianBlur(grayscale, (kernel_size, kernel_size), 0)

    # Apply Canny edge detection
    low_t = 50
    high_t = 150
    edges = cv2.Canny(blur, low_t, high_t)

    # Apply region selection to focus on the road
    region = region_selection(edges)

    # Use Hough Transform to detect lines
    hough = hough_transform(region)

    # Extract lane lines and their coordinates
    lines = lane_lines(frame, hough)
    left_line, right_line = lines

    # Return the pixel points for both lanes
    return left_line, right_line


def process_frame_for_display_with_fill(frame):
    """
    Process a single frame to detect and draw lane lines, filling the area between them.
    Parameters:
        frame: Input video frame (OpenCV image).
    Returns:
        Processed frame with lane lines and filled area.
    """
    # Convert the frame to grayscale and apply Gaussian blur
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kernel_size = 5
    blur = cv2.GaussianBlur(grayscale, (kernel_size, kernel_size), 0)

    # Apply Canny edge detection
    low_t = 50
    high_t = 150
    edges = cv2.Canny(blur, low_t, high_t)

    # Apply region selection to focus on the road
    region = region_selection(edges)

    # Use Hough Transform to detect lines
    hough = hough_transform(region)

    # Extract lane lines
    left_line, right_line = lane_lines(frame, hough)

    # Draw and fill the lane area
    filled_frame = fill_lane_area(frame, left_line, right_line)

    # Draw the detected lines on top of the filled frame
    result_frame = draw_lane_lines(filled_frame, [left_line, right_line])

    return result_frame


def fill_lane_area(image, left_line, right_line, color=(0, 255, 0)):
    """
    Fill the area between the detected left and right lane lines with the specified color.
    Parameters:
        image: The input frame (OpenCV image).
        left_line: Coordinates of the left lane line [(x1, y1), (x2, y2)].
        right_line: Coordinates of the right lane line [(x1, y1), (x2, y2)].
        color: Color to fill the lane area (Default: Green (0, 255, 0)).
    Returns:
        Image with the lane area filled.
    """
    if left_line is None or right_line is None:
        return image

    # Combine the left and right lane points to form a polygon
    lane_polygon = np.array([
        [left_line[0], left_line[1], right_line[1], right_line[0]]
    ], dtype=np.int32)

    # Create a blank image to draw the polygon
    overlay = np.zeros_like(image, dtype=np.uint8)
    cv2.fillPoly(overlay, lane_polygon, color)

    # Blend the original image with the overlay
    filled_image = cv2.addWeighted(image, 1, overlay, 0.3, 0)
    return filled_image


def process_subscriber_frame(frame, output_coordinates=True):
    """
    Process a frame received from a subscriber and either return lane points or display the result.
    Parameters:
        frame: Input frame from Subscriber.
        output_coordinates: If True, return lane points. If False, show the processed frame.
    """
    if output_coordinates:
        # Extract lane points
        left_line, right_line = process_frame_for_coordinates(frame)
        print("Left Lane:", left_line)
        print("Right Lane:", right_line)
        return left_line, right_line
    else:
        # Display the processed frame
        processed_frame = process_frame_for_display_with_fill(frame)
        cv2.imshow('Lane Detection', processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            raise KeyboardInterrupt


# Example usage in a subscriber loop
# Assume `frame` is being received from the subscriber
# try:
#     while True:
#         # Replace this with the actual frame from the subscriber
#         # Placeholder for subscriber frame
#         frame = cv2.imread("example_frame.jpg")

#         # Process the frame for coordinates
#         process_subscriber_frame(frame, output_coordinates=True)

#         # Alternatively, display the processed frame
#         # process_subscriber_frame(frame, output_coordinates=False)

# except KeyboardInterrupt:
#     print("Exiting...")
# finally:
#     cv2.destroyAllWindows()
