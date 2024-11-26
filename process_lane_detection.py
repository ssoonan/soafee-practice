from build.fastdds_python.src.swig.fastdds import DomainParticipantFactory
from lib.lane_detector import enhanced_lane_detection
from video_subscriber import read_frame, setup_fastdds_for_subscriber

import cv2


participant, datareader = setup_fastdds_for_subscriber()
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
