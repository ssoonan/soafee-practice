from fastdds import DomainParticipantFactory, DomainParticipantQos, TopicQos, PublisherQos, DataWriterQos, TypeSupport, RELIABLE_RELIABILITY_QOS

from dds.LaneDetection import LaneDetectionResult, LaneDetectionResultPubSubType
from lib.lane_detector import enhanced_lane_detection
from video_subscriber import read_frame, setup_fastdds_for_subscriber


def setup_fastdds_for_lane_detection():
    """Fast DDS initialization and creation of main entities"""
    participant_qos = DomainParticipantQos()
    participant = DomainParticipantFactory.get_instance().create_participant(0,
                                                                             participant_qos)

    # Register the type
    lane_detection_type = LaneDetectionResultPubSubType()
    lane_detection_type.set_name("LaneDetection")
    lane_detection_type_support = TypeSupport(lane_detection_type)
    participant.register_type(lane_detection_type_support)

    # Create the Topic
    topic_qos = TopicQos()
    topic = participant.create_topic(
        "LaneDetectionTopic", lane_detection_type.get_name(), topic_qos)

    # Create the Publisher
    publisher_qos = PublisherQos()
    publisher = participant.create_publisher(publisher_qos)

    # Create the DataWriter
    datawriter_qos = DataWriterQos()
    datawriter = publisher.create_datawriter(topic, datawriter_qos)

    return participant, datawriter


def publish_lane_detection_results(datawriter, left_line, right_line):
    # Create the data instance
    lane_detection_result = LaneDetectionResult()
    left_line_var = lane_detection_result.left_lane()
    right_line_var = lane_detection_result.right_lane()

    # Fill in the left lane line data
    if left_line is not None:
        left_line_var.x1(left_line[0][0])
        left_line_var.y1(left_line[0][1])
        left_line_var.x2(left_line[1][0])
        left_line_var.y2(left_line[1][1])
    else:
        left_line_var.x1(0)
        left_line_var.y1(0)
        left_line_var.x2(0)
        left_line_var.y2(0)

    # Fill in the right lane line data
    if right_line is not None:
        right_line_var.x1(right_line[0][0])
        right_line_var.y1(right_line[0][1])
        right_line_var.x2(right_line[1][0])
        right_line_var.y2(right_line[1][1])
    else:
        right_line_var.x1(0)
        right_line_var.y1(0)
        right_line_var.x2(0)
        right_line_var.y2(0)

    # Publish the data
    datawriter.write(lane_detection_result)


def process_lane_detection_and_publish():
    video_participant, datareader = setup_fastdds_for_subscriber()
    lane_participant, datawriter = setup_fastdds_for_lane_detection()
    try:
        while True:
            frame = read_frame(datareader)
            if frame is None:
                continue
            left_line, right_line = enhanced_lane_detection(frame)
            publish_lane_detection_results(datawriter, left_line, right_line)

    except KeyboardInterrupt:
        print("Subscriber terminated.")
    finally:
        video_participant.delete_contained_entities()
        DomainParticipantFactory.get_instance().delete_participant(video_participant)
        lane_participant.delete_contained_entities()
        DomainParticipantFactory.get_instance().delete_participant(lane_participant)


if __name__ == "__main__":
    process_lane_detection_and_publish()
