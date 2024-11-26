import threading
import time
from fastdds import DomainParticipantFactory, DomainParticipantQos, DataReaderQos, SampleInfo, TypeSupport, TopicQos, SubscriberQos
from dds.ObjectDetection import ObjectDetectionResult, ObjectDetectionResultPubSubType


class ObjectDetectionSubscriber:
    def __init__(self):
        # Create the DomainParticipant
        participant_qos = DomainParticipantQos()
        self.participant = DomainParticipantFactory.get_instance().create_participant(0,
                                                                                      participant_qos)

        # Register the type
        object_detection_type = ObjectDetectionResultPubSubType()
        object_detection_type.set_name("ObjectDetection")
        object_detection_type_support = TypeSupport(
            object_detection_type)
        self.participant.register_type(object_detection_type_support)

        # Create the Topic
        topic_qos = TopicQos()
        self.topic = self.participant.create_topic(
            "ObjectDetectionTopic", object_detection_type.get_name(), topic_qos)

        # Create the Subscriber
        subscriber_qos = SubscriberQos()
        self.subscriber = self.participant.create_subscriber(subscriber_qos)

        # Create the DataReader
        reader_qos = DataReaderQos()
        self.datareader = self.subscriber.create_datareader(
            self.topic, reader_qos)

        # Data storage
        self.latest_data = None
        self.lock = threading.Lock()

        # Start the listener thread
        self.listener_thread = threading.Thread(target=self.listener)
        self.listener_thread.start()

    def listener(self):
        """Listener thread that reads data from the DataReader."""
        sample_info = SampleInfo()
        while True:
            object_detection_result = ObjectDetectionResult()
            ret_code = self.datareader.read_next_sample(
                object_detection_result, sample_info)
            if ret_code == 0:  # ReturnCode_t.RETCODE_OK
                if sample_info.valid_data:
                    with self.lock:
                        self.latest_data = object_detection_result
            else:
                # No data available; sleep briefly to avoid busy-waiting
                time.sleep(0.01)

    def get_latest_data(self):
        with self.lock:
            return self.latest_data

    def close(self):
        self.participant.delete_contained_entities()
        DomainParticipantFactory.get_instance().delete_participant(self.participant)
