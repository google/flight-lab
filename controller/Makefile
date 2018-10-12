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
	python -m pip install --upgrade pip==9.0.1
	pip install -r $(RequirementsFile)

build:
	pushd ./protos && make proto-py && popd

install-client:
	sed -e 's,{SRC_DIR},'"$(SRC_DIR)",g \
		-e 's,{NAME},Controller-Client,g' \
		-e 's,{CMDLINE},'"/usr/bin/python2.7 main.py client",g \
		-e 's,{USER},${USER},g' \
		template.service > /tmp/controller-client.service
	sudo mv /tmp/controller-client.service /etc/systemd/system/controller-client.service
	sed -e 's,{SRC_DIR},'"$(SRC_DIR)",g -e s/{TYPE}/client/g template.rsyslog > /tmp/controller-client.conf
	sudo mv /tmp/controller-client.conf /etc/rsyslog.d/controller-client.conf
	sudo systemctl enable controller-client.service
	sudo systemctl restart rsyslog

install-server:
	sed -e 's,{SRC_DIR},'"$(SRC_DIR)",g \
		-e 's,{NAME},Controller-Server,g' \
		-e 's,{CMDLINE},'"/usr/bin/python2.7 main.py server",g \
		-e 's,{USER},${USER},g' \
		template.service > /tmp/controller-server.service
	sudo mv /tmp/controller-server.service /etc/systemd/system/controller-server.service
	sed -e 's,{SRC_DIR},'"$(SRC_DIR)",g -e s/{TYPE}/server/g template.rsyslog > /tmp/controller-server.conf
	sudo mv /tmp/controller-server.conf /etc/rsyslog.d/controller-server.conf
	sudo systemctl enable controller-server.service
	sudo systemctl restart rsyslog

	sed -e 's,{SRC_DIR},'"$(SRC_DIR)",g \
		-e 's,{NAME},Nginx,g' \
		-e 's,{CMDLINE},'"/usr/local/nginx/sbin/nginx -p /tmp -c ${SRC_DIR}/nginx.conf",g \
		-e 's,{USER},${USER},g' \
		template.service > /tmp/nginx.service
	sudo mv /tmp/nginx.service /etc/systemd/system/nginx.service
	sudo systemctl enable nginx.service

run-client: build
	python main.py

run-server: build
	python main.py server

