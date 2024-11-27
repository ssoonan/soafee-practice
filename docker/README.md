# Build Ultralytics for ARM neoverse

## QuickStart

### 1. Build ultralytics:neoverse

if it was already built, you can skip it. (also you can use pre-built image on docker hub seunmul/ultralytics:neoverse )

```
git clone https://github.com/ultralytics/ultralytics.git
cd ultralytics && docker build -f ../Dockerfile-neoverse -t seunmul/ultralytics:neoverse .
```

### 2. Build ultralytics:neoverse+DDS

if it was already built, you can skip it. (also you can use pre-built image on docker hub: seunmul/ultralytics:neoverse_DDS )

```
docker build -f ../Dockerfile-neoverse+DDS -t seunmul/ultralytics:neoverse_DDS .
```


### 3. TEST
```
# raw
docker run --name SOAFEE_DEV_2 -it seunmul/ultralytics:neoverse_DDS  /bin/bash

# with custom volumn
docker run --name SOAFEE_DEV_2 -it -v /Users/seunmul/Desktop/docker_shared/SOAFEE:/home/ubuntu/workspace seunmul/ultralytics:neoverse_DDS  /bin/bash

# (for mac) with display option
docker run --name SOAFEE_DEV_2 -it -e DISPLAY=docker.for.mac.host.internal:0 -v /Users/seunmul/Desktop/docker_shared/SOAFEE:/home/ubuntu/workspace seunmul/ultralytics:neoverse_DDS_latest  /bin/bash
```