from LaneDetection import LaneDetectionResult, LaneDetectionResultPubSubType
from build.fastdds_python.src.swig.fastdds import DomainParticipantFactory
from lib.lane_detector import enhanced_lane_detection
from video_subscriber import read_frame, setup_fastdds_for_subscriber
from video_publisher import setup_fastdds_for_publisher

import cv2


def publish_lane_detection_results(left_line, right_line):
    lane_participant, datawriter = setup_fastdds_for_publisher("LaneDetection")

    # Register the type
    lane_detection_type = LaneDetectionResultPubSubType()
    participant.register_type(lane_detection_type)

    # Create the Publisher
    publisher = participant.create_publisher()

    # Create the Topic
    topic = participant.create_topic(
        "LaneDetectionTopic", lane_detection_type.get_type_name())

    # Create the DataWriter
    writer_qos = DataWriterQos()
    writer = publisher.create_datawriter(topic, writer_qos)

    # Create the data instance
    lane_detection_result = LaneDetectionResult()

    # Fill in the left lane line data
    if left_line is not None:
        lane_detection_result.left_lane.x1 = left_line[0][0]
        lane_detection_result.left_lane.y1 = left_line[0][1]
        lane_detection_result.left_lane.x2 = left_line[1][0]
        lane_detection_result.left_lane.y2 = left_line[1][1]
    else:
        lane_detection_result.left_lane.x1 = 0
        lane_detection_result.left_lane.y1 = 0
        lane_detection_result.left_lane.x2 = 0
        lane_detection_result.left_lane.y2 = 0

    # Fill in the right lane line data
    if right_line is not None:
        lane_detection_result.right_lane.x1 = right_line[0][0]
        lane_detection_result.right_lane.y1 = right_line[0][1]
        lane_detection_result.right_lane.x2 = right_line[1][0]
        lane_detection_result.right_lane.y2 = right_line[1][1]
    else:
        lane_detection_result.right_lane.x1 = 0
        lane_detection_result.right_lane.y1 = 0
        lane_detection_result.right_lane.x2 = 0
        lane_detection_result.right_lane.y2 = 0

    # Publish the data
    writer.write(lane_detection_result)

    # Clean up
    participant.delete_contained_entities()
    DomainParticipantFactory.get_instance().delete_participant(participant)


video_participant, datareader = setup_fastdds_for_subscriber("VideoData")


try:
    while True:
        frame = read_frame(datareader)
        if frame is None:
            continue
        frame2 = enhanced_lane_detection(frame)


except KeyboardInterrupt:
    print("Subscriber terminated.")
finally:
    cv2.destroyAllWindows()
    participant.delete_contained_entities()
    DomainParticipantFactory.get_instance().delete_participant(participant)
