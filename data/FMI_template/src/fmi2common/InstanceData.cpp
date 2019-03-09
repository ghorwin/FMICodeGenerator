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
	if (m.find(varID) == m.end() )
		throw std::runtime_error("Invalid or unknown ID.");
}

void InstanceData::setRealParameter(int varID, double value) {
	checkIfIDExists(m_realInput, varID);
	m_realInput[varID] = value;
	m_externalInputVarsModified = true;
}


void InstanceData::setIntParameter(int varID, int value) {
	checkIfIDExists(m_integerInput, varID);
	m_integerInput[varID] = value;
	m_externalInputVarsModified = true;
}


void InstanceData::setStringParameter(int varID, fmi2String value) {
	checkIfIDExists(m_stringInput, varID);
	m_stringInput[varID] = value;
	m_externalInputVarsModified = true;
}


void InstanceData::setBoolParameter(int varID, bool value) {
	checkIfIDExists(m_boolInput, varID);
	m_boolInput[varID] = value;
	m_externalInputVarsModified = true;
}


void InstanceData::getRealParameter(int varID, double & value) {
	// update procedure for model exchange
	if (m_modelExchange)
		updateIfModified();
	checkIfIDExists(m_realOutput, varID);
	value = m_realOutput[varID];
}


void InstanceData::getIntParameter(int varID, int & value) {
	// update procedure for model exchange
	if(m_modelExchange)
		updateIfModified();
	checkIfIDExists(m_integerOutput, varID);
	value = m_integerOutput[varID];
}


void InstanceData::getStringParameter(int varID, fmi2String & value) {
	// update procedure for model exchange
	if(m_modelExchange)
		updateIfModified();
	checkIfIDExists(m_stringOutput, varID);
	value = m_stringOutput[varID].c_str();
}


void InstanceData::getBoolParameter(int varID, bool & value) {
	// update procedure for model exchange
	if(m_modelExchange)
		updateIfModified();
	checkIfIDExists(m_boolOutput, varID);
	value = m_boolOutput[varID];
}


void InstanceData::completedIntegratorStep() {
	// this function must only be called in ModelExchange mode!!!
	if (!m_modelExchange)
		throw std::runtime_error("Invalid function call; only permitted in ModelExchange mode.");
	updateIfModified();
	completedIntegratorStep(m_tInput, &m_yInput[0]);
}

