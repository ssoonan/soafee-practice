docker build -t ssoonan0770/soafee-practice:base . -f Dockerfile.base
docker build -t ssoonan0770/soafee-practice:lane_detector . -f Dockerfile.lane_detector
docker build -t ssoonan0770/soafee-practice:object_detector . -f Dockerfile.object_detector
docker build -t ssoonan0770/soafee-practice:flask . -f Dockerfile.flask


docker push ssoonan0770/soafee-practice:lane_detector
docker push ssoonan0770/soafee-practice:object_detector
docker push ssoonan0770/soafee-practice:flask