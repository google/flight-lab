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

#define _USE_MATH_DEFINES // for C++  
#include <cmath>

#include "SimData.h"


double RadianToDegree(double value) {
	return value / M_PI * 180;
}

double DegreeToRadian(double value) {
	return value / 180 * M_PI;
}

double RadianToDegreeAndFlipSign(double value) {
	return -value / M_PI * 180;
}

double DegreeToRadianAndFlipSign(double value) {
	return -value / 180 * M_PI;
}

double MillibarToInhg(double value) {
	return value * 0.02953;
}

double InhgToMillibar(double value) {
	return value / 0.02953;
}

double flipSign(double value) {
	return -value;
}

DataDefinition::DataDefinition(const char* Name, const char* Unit, Converter FromSimValue, Converter ToSimValue) {
	this->Name = Name;
	this->Unit = Unit;
	this->FromSimValue = FromSimValue;
	this->ToSimValue = ToSimValue;
}

SimData SimData::instance_;

SimData::SimData() {
	data_mapping_[AIRSPEED_INDICATOR_INDICATION] = DataDefinition("Airspeed Indicated", "Knots");
	data_mapping_[ATTITUDE_INDICATOR_BANK_ANGLE] = DataDefinition("ATTITUDE INDICATOR BANK DEGREES", "Radians", RadianToDegreeAndFlipSign, DegreeToRadianAndFlipSign);
	data_mapping_[ATTITUDE_INDICATOR_PITCH_ANGLE] = DataDefinition("ATTITUDE INDICATOR PITCH DEGREES", "Radians", RadianToDegreeAndFlipSign, DegreeToRadianAndFlipSign);
	data_mapping_[HEADING_INDICATOR_INDICATION] = DataDefinition("PLANE HEADING DEGREES GYRO", "Radians", RadianToDegree, DegreeToRadian);
	data_mapping_[ALTIMETER_INDICATION] = DataDefinition("INDICATED ALTITUDE", "Feet");
	data_mapping_[ALTIMETER_KOHLSMAN_SETTING] = DataDefinition("KOHLSMAN SETTING MB", "Millibars", MillibarToInhg, InhgToMillibar);
	data_mapping_[MAGNETIC_COMPASS_INDICATION] = DataDefinition("WISKEY COMPASS INDICATION DEGREES", "Degrees");
	data_mapping_[FLAPS_POSITION] = DataDefinition("FLAPS HANDLE INDEX", NULL);
	data_mapping_[AIRCRAFT_LATITUDE] = DataDefinition("PLANE LATITUDE", "Degrees");
	data_mapping_[AIRCRAFT_LONGITUDE] = DataDefinition("PLANE LONGITUDE", "Degrees");
	data_mapping_[AIRCRAFT_ALTITUDE] = DataDefinition("PLANE ALTITUDE", "Feet");
	data_mapping_[AIRCRAFT_PITCH] = DataDefinition("PLANE PITCH DEGREES", "Degrees");
	data_mapping_[AIRCRAFT_BANK] = DataDefinition("PLANE BANK DEGREES", "Degrees");
	data_mapping_[AIRCRAFT_HEADING_TRUE] = DataDefinition("PLANE HEADING DEGREES TRUE", "Degrees");
	data_mapping_[ELEVATOR_TRIM_POSITION] = DataDefinition("ELEVATOR TRIM POSITION", "Degrees");
	data_mapping_[ELEVATOR_TRIM_INDICATOR] = DataDefinition("ELEVATOR TRIM INDICATOR", "Position");
	data_mapping_[TIME] = DataDefinition("ABSOLUTE TIME", "Seconds");
	data_mapping_[TIME_OF_DAY] = DataDefinition("TIME OF DAY", "Enum");
	data_mapping_[MAGNETIC_VARIATION] = DataDefinition("MAGVAR", "Degrees");
	data_mapping_[MASTER_BATTERY_SWITCH] = DataDefinition("ELECTRICAL MASTER BATTERY", "Bool");
	data_mapping_[MASTER_ALTERNATOR_SWITCH] = DataDefinition("GENERAL ENG MASTER ALTERNATOR:1", "Bool");
	data_mapping_[AVIONICS_MASTER_SWITCH] = DataDefinition("AVIONICS MASTER SWITCH", "Bool");
	data_mapping_[TAXI_LIGHT] = DataDefinition("LIGHT TAXI", "Bool");
	data_mapping_[LANDING_LIGHT] = DataDefinition("LIGHT LANDING", "Bool");
	data_mapping_[BEACON_LIGHT] = DataDefinition("LIGHT BEACON", "Bool");
	data_mapping_[NAVIGATION_LIGHT] = DataDefinition("LIGHT NAV", "Bool");
	data_mapping_[STROBE_LIGHT] = DataDefinition("LIGHT STROBE", "Bool");
	data_mapping_[FUEL_PUMP_SWITCH] = DataDefinition("GENERAL ENG FUEL PUMP SWITCH:1", "Bool");
	data_mapping_[PITOT_HEAT] = DataDefinition("PITOT HEAT", "Bool");
}
