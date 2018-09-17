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

init:
	python -m pip install --upgrade pip==9.0.1
	pip install -r $(RequirementsFile)

build: proto-py

run:
	python main.py

run_server:
	python main.py server

proto-py:
	cd ./protos && make
