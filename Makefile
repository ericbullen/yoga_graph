.PHONY: build
PKG_NAME := $(shell basename $(WORKDIR))

build:
	@docker build . --tag $(PKG_NAME):1.0.0 -f Dockerfile
