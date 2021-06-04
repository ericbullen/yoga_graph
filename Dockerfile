FROM fedora:34
LABEL maintainer="eric.bullen@gmail.com"

RUN dnf update -y && dnf install -y \
        glibc-common \
        glibc-langpack-en \
        graphviz \
        python3-pyyaml \
    && dnf clean all

ENV TZ="America/Los_Angeles"
ENV LANG="en_US.utf8"

# The /.cache file is needed for GraphViz
RUN mkdir /data /.cache && \
    chown -R nobody:nobody /data /.cache

COPY make_yoga_graph.py /srv
COPY yoga_asanas.yaml /srv

VOLUME ["/data"]
WORKDIR /srv

USER nobody

ENV EXPERIENCE_LEVELS=""
ENV INTENSITY_LEVELS=""
ENV MIN_LENGTH=""
ENV MOBILITY_AREAS=""
ENV STRENGTH_AREAS=""

CMD ["python3", "/srv/make_yoga_graph.py"]
