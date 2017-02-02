FROM alpine

RUN apk --update add python py-pip
COPY . /dockercloud
RUN cd dockercloud && \
    pip install . && \
    docker-cloud -v
WORKDIR /root

ENTRYPOINT ["docker-cloud"]
