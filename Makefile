.PHONY: clean test build start
WORKDIR := $(shell pwd)
PKG_NAME := $(shell basename $(WORKDIR))
DOCKERFILE := "Dockerfile)"

build:
	@docker build . --tag $(PKG_NAME):1.0.0 -f Dockerfile
