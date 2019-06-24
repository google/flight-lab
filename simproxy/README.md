# Prerequisites

* Microsoft Flight Simulator X with SP2
* Microsoft Flight Simulator X SP2 SDK

If Prepar3D is used instead, please update SIMCONNECT_SDK_DIR in Makefile to "C:\Program Files (x86)\Lockheed Martin\Prepar3D [version]\Utilities\SimConnect SDK".

# Setup

From command line, run the following in simproxy directory:

```
    make init
```

## gRPC

SimProxy depends on gRPC and related libraries.

Currently building these dependencies on Windows platform is not automated yet. Files have to be manually copied to [github root]\build\grpc.

```
    TODO: automate building of grpc on Windows platform.
```

# Build 

From command line, run the following in simproxy directory:

```
    make build
```