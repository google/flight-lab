# Before first use on a new machine:
#  sudo make init
# During development when protos/*.proto is updated:
#   make build
# Run controller app:
#   make run

ifeq ($(OS),Windows_NT)
	RequirementsFile := requirements-windows.txt
else
	RequirementsFile := requirements.txt
endif

SRC_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

init:
	python -m pip install --upgrade pip
	pip install -r $(RequirementsFile)
	# For gRPC-web support
	sudo apt-get install nginx

build: proto-py

proto-py:
	cd ./protos && make

install-client:
	sed -e 's,{SRC_DIR},'"$(SRC_DIR)",g -e s/{TYPE}/client/g template.service > /tmp/controller-client.service
	sudo mv /tmp/controller-client.service /etc/systemd/system/controller-client.service
	sudo systemctl enable controller-client.service

install-server:
	sed -e 's,{SRC_DIR},'"$(SRC_DIR)",g -e s/{TYPE}/server/g template.service > /tmp/controller-server.service
	sudo mv /tmp/controller-server.service /etc/systemd/system/controller-server.service
	sudo systemctl enable controller-server.service

run-client: build
	python main.py

run-server: build
	python main.py server