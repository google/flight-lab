/* Copyright 2018 Flight Lab authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <sstream>
#include <grpc++/grpc++.h>

#include "SimConnectClient.h"
#include "SimProxyImpl.h"


const int kSimulatorReconnectIntervalMsec = 1000;
const int kSimProxyRpcPort = 50051;

std::unique_ptr<grpc::Server> StartRpcServer(SimProxyImpl* service) {
	std::ostringstream server_address;
	server_address << "0.0.0.0:" << kSimProxyRpcPort;

	grpc::ServerBuilder builder;
	builder.AddListeningPort(server_address.str(), grpc::InsecureServerCredentials());
	builder.RegisterService(service);
	std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
	std::cout << "Server listening on " << server_address.str() << std::endl;

	return server;
}

int main() {
	SimConnectClient client;
	SimProxyImpl service(client);
	auto rpc_server = StartRpcServer(&service);

	while (true) {
		try {
			client.Run();
		}
		catch (const std::exception& e) {
			printf("Exception: %s\n", e.what());
		}
		Sleep(kSimulatorReconnectIntervalMsec);
	}

	return 0;
}