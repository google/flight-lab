# Before first use on a new machine:
#  sudo make init
# During development when protos/*.proto is updated:
#   make build
# Run controller app:
#   make run


init:
  python -m pip install --upgrade pip
  pip install -r requirements.txt

build: proto-py

run:
  python main.py

run_server:
  python main.py server

proto-py:
  cd ./protos && make