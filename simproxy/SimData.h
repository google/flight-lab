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

 /// Simulator data definitions and converters.
 ///
 /// This library provides:
 ///   * mapping between simulator variables and SimProxy data types.
 ///   * converters for values from and to simulator.

#pragma once

#include <map>

#include "sim_proxy.pb.h"

typedef double(*Converter)(double);

struct DataDefinition {
	const char* Name;
	const char* Unit;
	Converter FromSimValue;
	Converter ToSimValue;

	DataDefinition() {}
	DataDefinition(const char* Name, const char* Unit, Converter FromSimValue = NULL, Converter ToSimValue = NULL);
};

// Singleton class to keep mapping between simulator variables and SimProxy data types.
class SimData {
public:
	static const SimData& GetInstance() { return instance_; }

	const DataDefinition GetDataDefinition(const DataType type) const { return data_mapping_.at(type); }
private:
	SimData();

	std::map<DataType, DataDefinition> data_mapping_;
	static SimData instance_;
};
