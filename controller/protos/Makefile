all: proto

proto:
	python -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. client.proto
	python -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. controller.proto
