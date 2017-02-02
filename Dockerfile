FROM alpine

RUN apk --update add python py-pip
COPY . /dockercloud
RUN cd dockercloud && \
    pip install . && \
    docker-cloud -v
WORKDIR /root

LABEL io.whalebrew.name docker-cloud
LABEL io.whalebrew.config.volumes '["~/.docker:/root/.docker:ro"]'

ENTRYPOINT ["docker-cloud"]
