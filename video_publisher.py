from fastdds import DomainParticipantFactory, DomainParticipantQos, TopicQos, PublisherQos, DataWriterQos, TypeSupport, RELIABLE_RELIABILITY_QOS
# Replace with your actual module and class names
from dds.VideoData import VideoDataPubSubType, VideoData

import cv2
import sys


def setup_fastdds_for_publisher():
    """Fast DDS 초기화 및 주요 객체 생성"""
    participant_qos = DomainParticipantQos()
    participant = DomainParticipantFactory.get_instance().create_participant(0,
                                                                             participant_qos)

    video_data_pubsub_type = VideoDataPubSubType()
    video_data_pubsub_type.set_name("VideoData")
    video_data_type_support = TypeSupport(video_data_pubsub_type)
    participant.register_type(video_data_type_support)

    topic_qos = TopicQos()
    topic = participant.create_topic(
        "VideoTopic", video_data_pubsub_type.get_name(), topic_qos)

    publisher_qos = PublisherQos()
    publisher = participant.create_publisher(publisher_qos)

    datawriter_qos = DataWriterQos()
    datawriter = publisher.create_datawriter(topic, datawriter_qos)

    return participant, datawriter


def setup_capture(source=0):
    """
    cv2.VideoCapture 설정 함수.
    :param source: 0 (웹캠) 또는 파일 경로
    :return: cv2.VideoCapture 객체
    """
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise ValueError(f"Unable to open video source: {source}")
    return cap


def show_frame(frame):
    """
    프레임을 화면에 표시하는 함수.
    :param frame: OpenCV 프레임
    """
    cv2.imshow('Video Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        raise KeyboardInterrupt  # 안전한 종료를 위해 예외 발생


def send_frame(datawriter, frame):
    """
    프레임 데이터를 Fast DDS로 전송하는 함수.
    :param datawriter: Fast DDS DataWriter 객체
    :param frame: OpenCV 프레임
    """
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        print("Failed to encode frame")
        return

    video_data = VideoData()
    video_data.data(buffer.tobytes())
    datawriter.write(video_data)


def main(source=0, display=True):
    """
    메인 실행 함수.
    :param source: 0 (웹캠) 또는 파일 경로
    :param display: True면 imshow 사용, False면 전송만
    """
    participant, datawriter = setup_fastdds_for_publisher()
    cap = setup_capture(source)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video or failed to read frame.")
                break

            if display:
                show_frame(frame)  # 화면에 표시
            send_frame(datawriter, frame)  # 데이터 전송
    except KeyboardInterrupt:
        print("Stream interrupted.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        participant.delete_contained_entities()
        DomainParticipantFactory.get_instance().delete_participant(participant)


if __name__ == '__main__':
    try:
        source = sys.argv[1]
    # TODO: 카메라 동적으로 받을 수 있게 하기
    except IndexError:
        source = 0
    main(source, display=False)
