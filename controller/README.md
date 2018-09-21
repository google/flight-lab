# Controller

Controller is the backend of the simulation system. It coordinates all machines
and devices to perform tasks, such as turning on/off the sytem, collecting
status, etc.

There are two parts: server and client. All communication between server and
client is via [gRPC](https://github.com/grpc/grpc).

## Server

Server runs on a single machine and connects to all clients to act as central
control. It:

*   dispatches command to all clients
*   collect component status from all clients
*   serve http APIs to frontend/UI

## Client

Client runs on every machine and acts as worker for server. Based on
configuration, it:

*   loads components to control apps, devices, etc
*   reports status of components to server.

# Usage

## Prerequisites

### For Windows Platform

1.  Install Python 2.7

    Choose X86 version regardless if OS is 64bit.

2.  Install Make for Windows

    2.1. Download and install from
    http://gnuwin32.sourceforge.net/packages/make.htm

    2.2. Add "C:\Program Files (X86)\GnuWin32\bin" to System PATH

3.  Install Microsoft Visual C++ Compiler for Python 2.7

    https://www.microsoft.com/en-us/download/details.aspx?id=44266

## Build

1. Install all the dependencies:

	```shell
	make init
	```

1. Build source code:

	```shell
	make build
	```


## Install

To have server or client run automatically on reboot:

```shell
make install-client
```

```shell
make install-server
```

# Development

To run server or client manually:

```shell
make run-client
```

```shell
make run-server
```