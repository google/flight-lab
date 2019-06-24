PROTOC=..\build\grpc\bin\protoc.exe
GRPC_CPP_PLUGIN=..\build\grpc\bin\grpc_cpp_plugin.exe
GRPC_PYTHON_PLUGIN=..\build\grpc\bin\grpc_python_plugin.exe

build:
	$(PROTOC) sim_proxy.proto --cpp_out=. --grpc_out=. --plugin=protoc-gen-grpc=$(GRPC_CPP_PLUGIN)
	python -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. sim_proxy.proto


clean:
	del *_pb2*.py
	del *.pyc
	del *.h
	del *.cc