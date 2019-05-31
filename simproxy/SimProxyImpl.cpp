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

#include "SimProxyImpl.h"
#include "SimData.h"

SimProxyImpl::SimProxyImpl(SimConnectClient& client) : client_(client), sim_data_(SimData::GetInstance()) {
}

grpc::Status SimProxyImpl::Watch(grpc::ServerContext* context,
	const WatchRequest* request, grpc::ServerWriter<WatchResponse>* writer) {
	printf("[Watch] New client connected.\n");

	

	std::vector<DataDefinition> definitions;
	for (int i = 0; i < request->types_size(); ++i) {
		const DataType dataType = request->types(i);
		const DataDefinition definition = sim_data_.GetDataDefinition(dataType);
		definitions.push_back(definition);
	}

	// Pre-populate response to be efficient.
	WatchResponse response;
	bool running = true;
	for (int i = 0; i < request->types_size(); ++i) {
		Data* data = response.add_data();
		data->set_type(request->types(i));
	}

	// Use mutex and condition_variable to ensure data consistency between update and streaming.
	std::condition_variable ready;
	std::mutex mtx;

	int id;
	try {
		id = client_.StartDataRequest(definitions, [&ready, &mtx, &response](double* values, int length) {
			// Values are changed. Save them and notify streaming thread.
			std::unique_lock<std::mutex> lock(mtx);
			for (int i = 0; i < length; ++i) {
				response.mutable_data(i)->set_value(values[i]);
			}
			ready.notify_one();
		}, [&ready, &running]() {
			// Simulator stops. Notify the streaming thread to stop.
			running = false;
			ready.notify_one();
		});
	}
	catch (const std::exception& e) {
		printf("[Watch] Failed to start data request: %s\n", e.what());
		return grpc::Status::CANCELLED;
	}

	WatchResponse responseCopy;
	while (true) {
		if (context->IsCancelled()) {
			printf("[Watch] Client cancelled connection.\n");
			client_.StopDataRequest(id);
			return grpc::Status::OK;
		}

		if (!running) {
			printf("[Watch] Data request cancelled.\n");
			return grpc::Status::CANCELLED;
		}

		{
			std::unique_lock<std::mutex> lock(mtx);
			if (ready.wait_for(lock, std::chrono::seconds(1)) == std::cv_status::timeout) {
				// Wake up once a while to check if client or simulator stops.
				continue;
			}

			// Spends minimum time within the lock to not block SimConnectClient message dispatching.
			responseCopy.CopyFrom(response);
		}

		writer->Write(responseCopy);
	}
}

grpc::Status SimProxyImpl::Set(grpc::ServerContext* context, const Data* request, EmptyResponse* response) {
	const DataDefinition definition = sim_data_.GetDataDefinition(request->type());
	try {
		client_.SetData(definition, request->value());
	}
	catch (...) {
		return grpc::Status::CANCELLED;
	}
	return grpc::Status::OK;
}

grpc::Status SimProxyImpl::Trigger(grpc::ServerContext* context, const Event* request, EmptyResponse* response) {
	// TBD
	return grpc::Status::OK;
}
