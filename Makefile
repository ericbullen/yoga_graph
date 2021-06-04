.PHONY: clean test build start
WORKDIR := $(shell pwd)
PKG_NAME := $(shell basename $(WORKDIR))
DOCKERFILE := "Dockerfile)"

build:
	@docker build . --tag $(PKG_NAME):1.0.0 -f Dockerfile

start:
	@docker run -d -p 5000:5000 -v /var/services/docker-registry:/srv/data --restart always --name ${PKG_NAME} docker-reg.home:5000/${PKG_NAME}:f32
