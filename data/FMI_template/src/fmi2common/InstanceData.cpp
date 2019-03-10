/*	Generic FMI Interface Implementation

This file is part of FMICodeGenerator (https://github.com/ghorwin/FMICodeGenerator)

BSD 3-Clause License

Copyright (c) 2018, Andreas Nicolai
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

*/

#include "InstanceData.h"

#include <stdexcept>
#include <sstream>

#include "fmi2Functions.h"
#include "fmi2FunctionTypes.h"

InstanceData::InstanceData() :
	m_callbackFunctions(0),
	m_initializationMode(false),
	m_modelExchange(true),
	m_tInput(0),
	m_externalInputVarsModified(false),
	m_fmuStateSize(0)
{
}


InstanceData::~InstanceData() {
	for (std::set<void*>::iterator it = m_fmuStates.begin(); it != m_fmuStates.end(); ++it) {
		free(*it);
	}
}


void InstanceData::logger(fmi2Status state, fmi2String category, fmi2String message) {
	if (m_loggingOn) {
		m_callbackFunctions->logger(m_callbackFunctions->componentEnvironment,
									m_instanceName.c_str(), state, category,
									message);
	}
}


template <typename T>
void checkIfIDExists(const T & m, int varID) {
	if (m.find(varID) == m.end() ) {
		std::stringstream strm;
		strm << "Invalid or unknown value reference " << varID;
		throw std::runtime_error(strm.str());
	}
}

void InstanceData::setReal(int varID, double value) {
	checkIfIDExists(m_realVar, varID);
	m_realVar[varID] = value;
	m_externalInputVarsModified = true;
}


void InstanceData::setInt(int varID, int value) {
	checkIfIDExists(m_integerVar, varID);
	m_integerVar[varID] = value;
	m_externalInputVarsModified = true;
}


void InstanceData::setString(int varID, fmi2String value) {
	checkIfIDExists(m_stringVar, varID);
	m_stringVar[varID] = value;
	m_externalInputVarsModified = true;
}


void InstanceData::setBool(int varID, bool value) {
	checkIfIDExists(m_boolVar, varID);
	m_boolVar[varID] = value;
	m_externalInputVarsModified = true;
}


void InstanceData::getReal(int varID, double & value) {
	// update procedure for model exchange
	if (m_modelExchange)
		updateIfModified();
	checkIfIDExists(m_realVar, varID);
	value = m_realVar[varID];
}


void InstanceData::getInt(int varID, int & value) {
	// update procedure for model exchange
	if(m_modelExchange)
		updateIfModified();
	checkIfIDExists(m_integerVar, varID);
	value = m_integerVar[varID];
}


void InstanceData::getString(int varID, fmi2String & value) {
	// update procedure for model exchange
	if(m_modelExchange)
		updateIfModified();
	checkIfIDExists(m_stringVar, varID);
	value = m_stringVar[varID].c_str();
}


void InstanceData::getBool(int varID, bool & value) {
	// update procedure for model exchange
	if(m_modelExchange)
		updateIfModified();
	checkIfIDExists(m_boolVar, varID);
	value = m_boolVar[varID];
}


void InstanceData::completedIntegratorStep() {
	// this function must only be called in ModelExchange mode!!!
	if (!m_modelExchange)
		throw std::runtime_error("Invalid function call; only permitted in ModelExchange mode.");
	updateIfModified();
	completedIntegratorStep(m_tInput, &m_yInput[0]);
}

