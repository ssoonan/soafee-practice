

## build

### idl build

```bash
cd dds
# fastddsgen 설치 폴더에서
~/Fast-DDS/src/fastddsgen/scripts/fastddsgen -python LaneDetection.idl ObjectDetection.idl VideoData.idl
cmake .
make
```

## run

### worker

각각 개별 터미널에서 실행
```bash
source install/setup.zsh # or .bash
python process_lane_detection.py
python process_object_detection.py
```

### flask
```bash
flask run --debug
```