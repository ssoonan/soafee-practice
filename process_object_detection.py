from fastdds import DomainParticipantFactory, DomainParticipantQos, TopicQos, PublisherQos, DataWriterQos, TypeSupport, RELIABLE_RELIABILITY_QOS

from dds.ObjectDetection import ObjectDetectionResult, ObjectDetectionResultPubSubType, BoundingBox
from lib.object_detector import object_detection
from video_subscriber import read_frame, setup_fastdds_for_subscriber


def setup_fastdds_for_object_detection():
    """Fast DDS initialization and creation of main entities"""
    participant_qos = DomainParticipantQos()
    participant = DomainParticipantFactory.get_instance().create_participant(0,
                                                                             participant_qos)

    # Register the type
    object_detection_type = ObjectDetectionResultPubSubType()
    object_detection_type.set_name("ObjectDetection")
    object_detection_type_support = TypeSupport(object_detection_type)
    participant.register_type(object_detection_type_support)

    # Create the Topic
    topic_qos = TopicQos()
    topic = participant.create_topic(
        "ObjectDetectionTopic", object_detection_type.get_name(), topic_qos)

    # Create the Publisher
    publisher_qos = PublisherQos()
    publisher = participant.create_publisher(publisher_qos)

    # Create the DataWriter
    datawriter_qos = DataWriterQos()
    datawriter = publisher.create_datawriter(topic, datawriter_qos)

    return participant, datawriter


def publish_object_detection_results(datawriter, box_results):
    # Create the data instance
    object_detection_result = ObjectDetectionResult()
    box_sequence = object_detection_result.boxes()
    bounding_box = BoundingBox()
    bounding_box.x(20)
    bounding_box.y(30)
    bounding_box.width(100)
    bounding_box.height(200)
    bounding_box.class_name("car")
    box_sequence.push_back(bounding_box)
    
    # for box in box_results:
    #     # Create a new BoundingBox instance
    #     bounding_box = BoundingBox()
    #     bounding_box.x(box['x'])
    #     bounding_box.y(box['y'])
    #     bounding_box.width(box['width'])
    #     bounding_box.height(box['height'])
    #     bounding_box.class_name(box['class_name'])

    #     # Append to the sequence
    #     boxes_sequence.push_back(bounding_box)

    # Publish the data
    datawriter.write(object_detection_result)


def process_object_detection_and_publish():
    video_participant, datareader = setup_fastdds_for_subscriber()
    object_detection_participant, datawriter = setup_fastdds_for_object_detection()
    try:
        while True:
            frame = read_frame(datareader)
            if frame is None:
                continue
            box_results = object_detection(frame)
            publish_object_detection_results(datawriter, box_results)

    except KeyboardInterrupt:
        print("Subscriber terminated.")
    finally:
        video_participant.delete_contained_entities()
        DomainParticipantFactory.get_instance().delete_participant(video_participant)
        object_detection_participant.delete_contained_entities()
        DomainParticipantFactory.get_instance().delete_participant(
            object_detection_participant)


if __name__ == "__main__":
    process_object_detection_and_publish()
