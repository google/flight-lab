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

/// Library to provide SimProxy gRPC service.

#pragma once

#include "sim_proxy.pb.h"
#include "sim_proxy.grpc.pb.h"
#include "SimConnectClient.h"

class SimProxyImpl final : public SimProxy::Service {
public:
	SimProxyImpl(SimConnectClient& client);

	grpc::Status Watch(grpc::ServerContext* context, const WatchRequest* request, grpc::ServerWriter<WatchResponse>* writer) override;

	grpc::Status Set(grpc::ServerContext* context, const Data* request, EmptyResponse* response) override;

	grpc::Status Trigger(grpc::ServerContext* context, const Event* request, EmptyResponse* response) override;

private:
	SimConnectClient& client_;
	const SimData& sim_data_;
};