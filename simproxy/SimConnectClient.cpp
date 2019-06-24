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

#include "SimConnectClient.h"


enum CLIENT_REQUEST_ID {
	CRID_REQUEST_SYSTEM_STATE = 1,
	CRID_RESERVATION_START = 100,
};

enum CLIENT_EVENT_ID {
	EVENT_SIM_START = 1,
};

SimConnectClient::SimConnectClient() {
	ResetAllIds();
}

void SimConnectClient::SetData(DataDefinition definition, double value) {
	if (definition.ToSimValue) {
		value = definition.ToSimValue(value);
	}

	int id = ReserveId();
	HRESULT hr = SimConnect_AddToDataDefinition(hSimConnect_, id, definition.Name, definition.Unit);
	if (FAILED(hr)) {
		throw std::runtime_error("Failed to set data value.");
	}

	try {
		HRESULT hr = SimConnect_SetDataOnSimObject(hSimConnect_, id, SIMCONNECT_SIMOBJECT_TYPE_USER, NULL, 0, sizeof(double), &value);
		if (FAILED(hr)) {
			throw std::runtime_error("Failed to set data value.");
		}
	}
	catch (...) {
		SimConnect_ClearDataDefinition(hSimConnect_, id);
		ReleaseId(id);
		throw;
	}

	SimConnect_ClearDataDefinition(hSimConnect_, id);
	ReleaseId(id);
}

int SimConnectClient::StartDataRequest(std::vector<DataDefinition> definitions, DataCallback data_callback, CancellationCallback cancel_callback) {
	if (!IsRunning()) {
		throw std::runtime_error("Simulator is not running.");
	}

	int id = ReserveId();
	printf("[SimConnectClient] Starting data request (id=%d)...\n", id);
	try {
		for (auto &definition : definitions) {
			HRESULT hr = SimConnect_AddToDataDefinition(hSimConnect_, id, definition.Name, definition.Unit);
			if (FAILED(hr)) {
				throw "Failed to add variable to watch.";
			}
		}

		data_requests_[id] = DataRequest{ definitions, data_callback, cancel_callback };

		HRESULT hr = SimConnect_RequestDataOnSimObject(hSimConnect_, id, id, SIMCONNECT_OBJECT_ID_USER, SIMCONNECT_PERIOD_SECOND, SIMCONNECT_DATA_REQUEST_FLAG_CHANGED);
		if (FAILED(hr)) {
			throw "Failed to request data.";
		}
	}
	catch (...) {
		StopDataRequest(id);
		throw;
	}

	return id;
}

void SimConnectClient::StopDataRequest(int dataDefId) {
	printf("[SimConnectClient] Stopping data request (id=%d)...\n", dataDefId);
	data_requests_.erase(dataDefId);
	if (hSimConnect_) {
		SimConnect_ClearDataDefinition(hSimConnect_, dataDefId);
	}
	ReleaseId(dataDefId);
}

void SimConnectClient::CancelAllDataRequests() {
	for (const auto& entry : data_requests_) {
		entry.second.cancel_callback();
	}
	data_requests_.clear();
}


void SimConnectClient::Run() {
	printf("[SimConnectClient] Connecting to simulator...\n");
	if (!SUCCEEDED(SimConnect_Open(&hSimConnect_, "SimProxy", NULL, 0, 0, 0))) {
		return;
	}
	printf("[SimConnectClient] Connected to simulator.\n");

	SimConnect_SubscribeToSystemEvent(hSimConnect_, EVENT_SIM_START, "SimStart");

	while (true) {
		SIMCONNECT_RECV* pData = NULL;
		DWORD cbData = 0;
		HRESULT hr = SimConnect_GetNextDispatch(hSimConnect_, &pData, &cbData);
		if (SUCCEEDED(hr)) {
			if (!OnDispatch(pData, cbData)) {
				break;
			}
		}
	}

	SimConnect_Close(hSimConnect_);
	hSimConnect_ = NULL;
	CancelAllDataRequests();
	ResetAllIds();
}

bool SimConnectClient::OnDispatch(SIMCONNECT_RECV* pData, DWORD cbData) {
	switch (pData->dwID) {
	case SIMCONNECT_RECV_ID_OPEN:
		OnOpen(pData, cbData);
		break;
	case SIMCONNECT_RECV_ID_EVENT:
		OnEvent((SIMCONNECT_RECV_EVENT*)pData);
		break;
	case SIMCONNECT_RECV_ID_SYSTEM_STATE:
		OnSystemState((SIMCONNECT_RECV_SYSTEM_STATE*)pData);
		break;
	case SIMCONNECT_RECV_ID_SIMOBJECT_DATA:
		OnSimObjectData((SIMCONNECT_RECV_SIMOBJECT_DATA*)pData);
		break;
	case SIMCONNECT_RECV_ID_QUIT:
		printf("[SimConnectClient] Simulator quit.\n");
		return false;
	}
	return true;
}

void SimConnectClient::OnEvent(SIMCONNECT_RECV_EVENT* pEvent) {
	DWORD uEventID = pEvent->uEventID;
	printf("[SimConnectClient] Event: id=%d\n", uEventID);

	switch (uEventID) {
	case EVENT_SIM_START:
		printf("[SimConnectClient] Simulation started.\n");
		break;
	}
}

void SimConnectClient::OnSimObjectData(SIMCONNECT_RECV_SIMOBJECT_DATA* pData) {
	try {
		auto &request = data_requests_.at(pData->dwDefineID);
		double* values = (double*)&pData->dwData;
		for (DWORD i = 0; i < pData->dwDefineCount; ++i) {
			if (request.data_definitions[i].FromSimValue) {
				values[i] = request.data_definitions[i].FromSimValue(values[i]);
			}
		}
		request.data_callback(values, pData->dwDefineCount);
	}
	catch (std::out_of_range) {
		StopDataRequest(pData->dwDefineID);
	}
}

void SimConnectClient::OnOpen(SIMCONNECT_RECV* pData, DWORD cbData) {
	printf("[SimConnectClient] Simulator launched.\n");
	SimConnect_RequestSystemState(hSimConnect_, CRID_REQUEST_SYSTEM_STATE, "Sim");
}

void SimConnectClient::OnSystemState(SIMCONNECT_RECV_SYSTEM_STATE* pObjData) {
	switch (pObjData->dwInteger) {
	case 0:
		printf("[SimConnectClient] Simulator mode: interactive UI.\n");
		break;
	case 1:
		printf("[SimConnectClient] Simulator mode: simulation.\n");
		break;
	default:
		printf("[SimConnectClient] Simulator mode: unknown.\n");
		break;
	}
}

int SimConnectClient::ReserveId() {
	std::lock_guard<std::mutex> lock(id_lock_);
	if (available_ids_.size() > 0) {
		int id = available_ids_.back();
		available_ids_.pop_back();
		return id;
	}
	else {
		return next_id_++;
	}
}

void SimConnectClient::ReleaseId(int id) {
	std::lock_guard<std::mutex> lock(id_lock_);
	available_ids_.push_back(id);
}

void SimConnectClient::ResetAllIds() {
	std::lock_guard<std::mutex> lock(id_lock_);
	available_ids_.clear();
	next_id_ = CRID_RESERVATION_START;
}