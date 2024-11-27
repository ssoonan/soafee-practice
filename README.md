
## install

### fastdds

```bash
python3 -m venv venv
source venb/bin/activate
pip install -U colcon-common-extensions vcstool

mkdir -p src
wget https://raw.githubusercontent.com/eProsima/Fast-DDS-python/main/fastdds_python.repos
# Download repositories
vcs import src < fastdds_python.repos
# Build the workspace
colcon build

# swig 및 기타 의존성
brew install swig # mac 기준
sudo apt install -y \
    swig4.1 \
    libpython3-dev # ubuntu
```

### fastddsgen

> 이 때 java version 11인지 체크 필요
```bash
mkdir -p ~/Fast-DDS/src
cd ~/Fast-DDS/src
git clone --recursive https://github.com/eProsima/Fast-DDS-Gen.git fastddsgen
cd fastddsgen
./gradlew assemble
```

## build

### idl build

```bash
cd dds
# fastddsgen 설치 폴더에서
~/Fast-DDS/src/fastddsgen/scripts/fastddsgen -python LaneDetection.idl ObjectDetection.idl VideoData.idl
cmake .
make
```

## docker build

```bash
sh build.sh # base image를 토대로 3개의 컨테이너 이미지 빌드

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