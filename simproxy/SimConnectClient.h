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

 /// Library to encapsulate communications with flight simulator via SimConnect SDK.

#pragma once

#include <map>
#include <mutex>
#include <vector>

#include <windows.h>
#include "SimConnect.h" 
#include "SimData.h"

typedef std::function<void(double*, int)> DataCallback;
typedef std::function<void()> CancellationCallback;

struct DataRequest {
	std::vector<DataDefinition> data_definitions;
	DataCallback data_callback;
	CancellationCallback cancel_callback;
};

class SimConnectClient {
public:
	SimConnectClient();

	bool IsRunning() {
		return hSimConnect_ != NULL;
	}

	/// Sets value for specified simulator data.
	void SetData(DataDefinition definition, double value);

	/// Requests continuous reading of values of a given set of simulator data.
	///
	/// Every time value of any specified simulator data is changed, data_callback will be called.
	/// If simulator quits, cancel_callback will be called.
	///
	/// An id is returned. Caller is responsible for stopping the data request by calling
	/// StopDataRequest() with the id.
	int StartDataRequest(std::vector<DataDefinition> definitions, DataCallback data_callback, CancellationCallback cancel_callback);

	/// Stops data request.
	void StopDataRequest(int dataDefId);

	/// Connects to flight simulator and continuously processes messages.
	///
	/// This call will block until flight simulator quits.
	void Run();

private:
	int ReserveId();
	void ReleaseId(int id);
	void ResetAllIds();

	void CancelAllDataRequests();

	bool OnDispatch(SIMCONNECT_RECV* pData, DWORD cbData);
	void OnEvent(SIMCONNECT_RECV_EVENT* pEvent);
	void OnSimObjectData(SIMCONNECT_RECV_SIMOBJECT_DATA* pData);
	void OnOpen(SIMCONNECT_RECV* pData, DWORD cbData);
	void OnSystemState(SIMCONNECT_RECV_SYSTEM_STATE* pObjData);

	HANDLE hSimConnect_ = NULL;

	std::mutex id_lock_;
	std::vector<int> available_ids_ = std::vector<int>();
	int next_id_;

	std::map<int, DataRequest> data_requests_;
};