SRC_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
ROOT_DIR = $(SRC_DIR)/../..
PROTOC = protoc
CLOSURE_COMPILER = $(ROOT_DIR)/bin/closure-compiler.jar
GRPC_WEB_PATH = $(ROOT_DIR)/third_party/grpc-web
PROTOBUF_PATH = $(GRPC_WEB_PATH)/third_party/grpc/third_party/protobuf
CLOSURE_LIBRARY_PATH = $(GRPC_WEB_PATH)/third_party/closure-library
GRPC_WEB_PLUGIN_PATH = $(GRPC_WEB_PATH)/javascript/net/grpc/web/protoc-gen-grpc-web
OUT_DIR = ../out
BUILD_DIR = ../build
JS_IMPORT_STYLE = import_style=closure,binary

all: proto-py compiled-js

proto-py:
	python -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. client.proto
	python -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. controller.proto

proto-js:
	rm -rf $(OUT_DIR)
	mkdir -p $(OUT_DIR)
	$(PROTOC) -I=$(PROTOBUF_PATH)/src/google/protobuf --js_out=$(JS_IMPORT_STYLE):$(OUT_DIR) $(PROTOBUF_PATH)/src/google/protobuf/any.proto
	$(PROTOC) -I=$(PROTOBUF_PATH)/src/google/protobuf --js_out=$(JS_IMPORT_STYLE):$(OUT_DIR) $(PROTOBUF_PATH)/src/google/protobuf/empty.proto
	$(PROTOC) -I=$(GRPC_WEB_PATH)/net/grpc/gateway/protos --js_out=$(JS_IMPORT_STYLE):$(OUT_DIR) $(GRPC_WEB_PATH)/net/grpc/gateway/protos/stream_body.proto
	$(PROTOC) -I=$(GRPC_WEB_PATH)/net/grpc/gateway/protos --js_out=$(JS_IMPORT_STYLE):$(OUT_DIR) $(GRPC_WEB_PATH)/net/grpc/gateway/protos/pair.proto
	$(PROTOC) -I=./ --js_out=$(JS_IMPORT_STYLE):$(OUT_DIR) ./controller.proto
	$(PROTOC) -I=./ --plugin=protoc-gen-grpc-web=$(GRPC_WEB_PLUGIN_PATH) --grpc-web_out=import_style=closure,mode=grpcwebtext:$(OUT_DIR) ./controller.proto

compiled-js: proto-js
	mkdir -p $(BUILD_DIR)
	java \
		-jar $(CLOSURE_COMPILER) \
		--js $(GRPC_WEB_PATH)/javascript \
  		--js $(GRPC_WEB_PATH)/net \
  		--js $(CLOSURE_LIBRARY_PATH) \
  		--js $(PROTOBUF_PATH)/js \
  		--js $(OUT_DIR) \
  		--entry_point=goog:proto.flightlab.ControlServiceClient \
  		--dependency_mode=STRICT \
  		--js_output_file $(BUILD_DIR)/controller.js