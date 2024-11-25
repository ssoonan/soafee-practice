import cv2
import numpy as np


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

    # Check for invalid slope values (vertical or near-infinite slopes)
    if slope == 0 or np.isinf(slope) or np.isnan(slope):
        return None

    try:
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        y1 = int(y1)
        y2 = int(y2)
        return ((x1, y1), (x2, y2))
    except Exception as e:
        # Handle exceptions (e.g., division by zero)
        print(f"Error in pixel_points: {e}")
        return None


def lane_lines(image, lines):
    """
    Create full length lines from pixel points.
            Parameters:
                    image: The input test image.
                    lines: The output lines from Hough Transform.
    """
    left_lane, right_lane = average_slope_intercept(lines)
    y1 = image.shape[0]
    y2 = y1 * 0.6

    # Get pixel points for left and right lanes
    left_line = pixel_points(y1, y2, left_lane)
    right_line = pixel_points(y1, y2, right_lane)
    return left_line, right_line


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


def enhanced_lane_detection(image):
    """
    Enhanced lane detection using color filtering and optimized Hough Transform.
    Parameters:
        image: Input image (BGR)
    Returns:
        Processed image with detected lane lines
    """
    # Convert to HSV for color filtering
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define white color mask
    white_lower = np.array([0, 0, 200], dtype=np.uint8)
    white_upper = np.array([255, 30, 255], dtype=np.uint8)
    white_mask = cv2.inRange(hsv, white_lower, white_upper)

    # Define yellow color mask
    yellow_lower = np.array([18, 94, 140], dtype=np.uint8)
    yellow_upper = np.array([48, 255, 255], dtype=np.uint8)
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)

    # Combine masks
    combined_mask = cv2.bitwise_or(white_mask, yellow_mask)
    masked_image = cv2.bitwise_and(image, image, mask=combined_mask)

    # Convert to grayscale
    gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blur, 50, 150)

    # Define region of interest (ROI)
    def region_of_interest(img):
        height, width = img.shape[:2]
        polygons = np.array([[
            (width * 0.1, height),
            (width * 0.4, height * 0.6),
            (width * 0.6, height * 0.6),
            (width * 0.9, height)
        ]], dtype=np.int32)
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, polygons, 255)
        return cv2.bitwise_and(img, mask)

    roi = region_of_interest(edges)

    # Apply Hough Transform
    lines = cv2.HoughLinesP(roi, rho=1, theta=np.pi / 180, threshold=20,
                            minLineLength=30, maxLineGap=150)

    left_line, right_line = lane_lines(image, lines)

    # Draw and fill the lane area
    filled_frame = fill_lane_area(image, left_line, right_line)

    # Draw the detected lines on top of the filled frame
    result_frame = draw_lane_lines(filled_frame, [left_line, right_line])

    return result_frame


# # Load the uploaded image
# image_path = "/home/rtos-ubuntu/Downloads/1.png"
# input_image = cv2.imread(image_path)

# # Process the image
# processed_image = enhanced_lane_detection(input_image)

# # Show the result using cv2.imshow
# cv2.imshow("Enhanced Lane Detection", processed_image)

# # Wait for user to press 'q' to close the window
# while True:
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release resources
# cv2.destroyAllWindows()
