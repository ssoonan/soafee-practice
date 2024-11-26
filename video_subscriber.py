from VideoData import VideoData
from fastdds import DomainParticipantFactory, DomainParticipantQos, TopicQos, SubscriberQos, DataReaderQos, SampleInfo, TypeSupport
from common import topic_dict

import cv2
import numpy as np


def setup_fastdds_for_subscriber(topic_name="VideoData"):
    """Fast DDS 초기화 및 주요 객체 생성"""
    participant_qos = DomainParticipantQos()
    participant = DomainParticipantFactory.get_instance().create_participant(0, participant_qos)

    pubsub_type = getattr(topic_dict[topic_name], f"{topic_name}PubSubType")()
    pubsub_type.set_name(topic_name)
    pubsub_type_type_support = TypeSupport(pubsub_type)
    participant.register_type(pubsub_type_type_support)

    topic_qos = TopicQos()
    topic = participant.create_topic(
        topic_name, pubsub_type.get_name(), topic_qos)

    subscriber_qos = SubscriberQos()
    subscriber = participant.create_subscriber(subscriber_qos)

    datareader_qos = DataReaderQos()
    datareader = subscriber.create_datareader(topic, datareader_qos)

    return participant, datareader


def read_frame(datareader):
    """
    DataReader에서 데이터를 읽어 OpenCV 프레임으로 변환하는 함수.
    :param datareader: Fast DDS DataReader 객체
    :return: OpenCV 프레임 또는 None
    """
    sample_info = SampleInfo()
    video_data = VideoData()

    # ReturnCode_t.RETCODE_OK
    if datareader.read_next_sample(video_data, sample_info) == 0:
        raw_data = video_data.data()
        if len(raw_data) == 0:
            print("Received empty data, skipping frame.")
            return None

        np_arr = np.array(raw_data, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            print("Failed to decode frame, skipping.")
            return None

        return frame
    return None


def show_frame(frame):
    """
    프레임을 화면에 표시하는 함수.
    :param frame: OpenCV 프레임
    """
    cv2.imshow('Subscriber', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        raise KeyboardInterrupt  # 안전한 종료를 위해 예외 발생


def main(display=True):
    """
    메인 실행 함수.
    :param display: True면 imshow 사용, False면 데이터 수신만 수행
    """
    participant, datareader = setup_fastdds_for_subscriber()

    try:
        while True:
            frame = read_frame(datareader)
            if frame is None:
                continue
            if display:
                show_frame(frame)
                from lib.lane_detector import enhanced_lane_detection
                # process_subscriber_frame(frame, False)
                frame2 = enhanced_lane_detection(frame)
                cv2.imshow('Lane Detection', frame2)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("Subscriber terminated.")
    finally:
        cv2.destroyAllWindows()
        participant.delete_contained_entities()
        DomainParticipantFactory.get_instance().delete_participant(participant)


if __name__ == '__main__':
    # 화면에 프레임 표시 및 데이터 수신
    main(display=True)

    # 화면에 표시하지 않고 데이터만 수신
    # main(display=False)
