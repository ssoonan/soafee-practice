# buildx 빌더 생성 및 사용 설치
# docker buildx create --name mybuilder --use
# docker buildx inspect --bootstrap

# 각 이미지 빌드
# docker buildx build --platform linux/arm64 -t snurtos/soafee-practice:base . -f Dockerfile.base --push
echo build start!

docker buildx build --platform linux/arm64 -t snurtos/soafee-practice:lane_detector . -f Dockerfile.lane_detector --push
docker buildx build --platform linux/arm64 -t snurtos/soafee-practice:object_detector . -f Dockerfile.object_detector --push
docker buildx build --platform linux/arm64 -t snurtos/soafee-practice:flask . -f Dockerfile.flask --push