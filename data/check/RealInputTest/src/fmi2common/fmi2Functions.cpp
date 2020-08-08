/*
FMI Interface for Model Exchange and CoSimulation Version 2

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

#include <memory>
#include <iostream>
#include <sstream>
#include <cstring> // for memcpy

#ifdef DEBUG


#define FMI_ASSERT(p)	if (!(p)) \
	{ std::cerr << "Assertion failure\nCHECK: " << #p << "\nFILE:  " << myFilename(__FILE__) << "\nLINE:  " << __LINE__ << '\n'; \
	  return fmi2Error; }

#else

#define FMI_ASSERT(p) (void)0;

#endif //  DEBUG

#ifdef _WIN32

#if _WIN32_WINNT < 0x0501
#define _WIN32_WINNT 0x0501
#endif

#include <windows.h>

#endif // _WIN32

#include "fmi2Functions.h"
#include "InstanceData.h"


// *** FMI Interface Functions ***


/* Inquire version numbers of header files */


const char* fmi2GetTypesPlatform() {
	// returns platform type, currently "default"
	return fmi2TypesPlatform;
}


const char* fmi2GetVersion() {
	// returns fmi version, currently "2.0"
	return "2.0";
}


// Enables/disables debug logging
fmi2Status fmi2SetDebugLogging(void* c, fmi2Boolean loggingOn, size_t nCategories, const char* const categories[]) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	modelInstance->logger(fmi2OK, "logAll", std::string("fmi2SetDebugLogging: logging switched ") + (loggingOn ? "on." : "off."));
	modelInstance->m_loggingOn = (loggingOn == fmi2True);
	if (modelInstance->m_loggingOn) {
		modelInstance->m_loggingCategories.clear();
		for (size_t i=0; i<nCategories; ++i)
			modelInstance->m_loggingCategories.push_back(std::string(categories[i]));
	}
	return fmi2OK;
}



/* Creation and destruction of FMU instances */


void* fmi2Instantiate(fmi2String instanceName, fmi2Type fmuType, fmi2String guid,
					  fmi2String fmuResourceLocation,
					  const fmi2CallbackFunctions* functions,
					  fmi2Boolean, fmi2Boolean loggingOn)
{
	// initial checks
	if (functions == NULL)
		return NULL;

	if (functions->logger == NULL)
		return NULL;

	std::string instanceNameString = instanceName;
	if (instanceNameString.empty()) {
		if (loggingOn)
			functions->logger(functions->componentEnvironment, instanceName, fmi2Error, "logStatusError", "fmi2Instantiate: Missing instance name.");
		return NULL;
	}

	// check for correct model
	if (std::string(InstanceData::GUID) != guid) {
		functions->logger(functions->componentEnvironment, instanceName, fmi2Error, "logStatusError", "fmi2Instantiate: Invalid/mismatching guid.");
		return NULL;
	}

	// instantiate data structure for instance-specific data
	InstanceData * data = InstanceData::create();
	// transfer function arguments
	data->m_callbackFunctions = functions;
	data->m_instanceName = instanceName;
	data->m_modelExchange = (fmuType == fmi2ModelExchange);
	data->m_resourceLocation = fmuResourceLocation;
	data->m_loggingOn = loggingOn;

	// return data pointer
	return data;
}


// Free allocated instance data structure
void fmi2FreeInstance(void* c) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	modelInstance->logger(fmi2OK, "logAll", "fmi2FreeInstance: Model instance deleted.");
	delete modelInstance;
}


/* Enter and exit initialization mode, terminate and reset */


// Overrides project settings?
fmi2Status fmi2SetupExperiment(void* c, int, double, double,
							   int, double)
{
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	modelInstance->logger(fmi2OK, "logAll", "fmi2SetupExperiment: Call of setup experiment.");
	// transfer experiment specs to Therakles
	return fmi2OK;
}


// All scalar variables with initial="exact" or "approx" can be set before
// fmi2SetupExperiment has to be called at least once before
fmi2Status fmi2EnterInitializationMode(void* c) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	modelInstance->logger(fmi2OK, "logAll", "fmi2EnterInitializationMode: Go into initialization mode.");
	modelInstance->m_initializationMode = true;
	// let instance data initialize everything that's needed
	// now the output directory parameter should be set
	try {
		modelInstance->init();
		// compute and cache serialization size, might be zero if serialization is not supported
		if (!modelInstance->m_modelExchange)
			modelInstance->computeFMUStateSize();

		// init successful
		return fmi2OK;
	}
	catch (std::exception & ex) {
		std::string err = ex.what();
		err += "\nModel initialization failed.";
		modelInstance->logger(fmi2Error, "logStatusError", err);
		return fmi2Error;
	}
}


// Switch off all initialization equations
fmi2Status fmi2ExitInitializationMode(void* c) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	modelInstance->logger(fmi2OK, "logAll", "fmi2ExitInitializationMode: Go out from initialization mode.");
	modelInstance->m_initializationMode = false;
	return fmi2OK;
}


fmi2Status fmi2Terminate(void* c) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	modelInstance->clearBuffers();
	modelInstance->logger(fmi2OK, "logAll", "fmi2Terminate: Terminate model.");
	return fmi2OK;
}


fmi2Status fmi2Reset(void* c) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	modelInstance->logger(fmi2Warning, "logStatusWarning", "fmi2Reset: Reset the whole model to default. Not implemented yet.");
	return fmi2OK;
}



/* Getting and setting variables values */

fmi2Status fmi2GetReal(void* c, const fmi2ValueReference vr[], size_t nvr, fmi2Real value[]) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	for (size_t i=0; i<nvr; ++i) {
		try {
			modelInstance->getReal(vr[i], value[i]);
		}
		catch (std::exception & ex) {
			std::string err = ex.what();
			err += "\nError in fmi2GetReal()";
			modelInstance->logger(fmi2Error, "logStatusError", err);
			return fmi2Error;
		}
	}
	return fmi2OK;
}


fmi2Status fmi2GetInteger(void* c, const fmi2ValueReference vr[], size_t nvr, fmi2Integer value[]) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	for (size_t i=0; i<nvr; ++i) {
		try {
			modelInstance->getInt(vr[i], value[i]);
		}
		catch (std::exception & ex) {
			std::string err = ex.what();
			err += "\nError in fmi2GetInteger()";
			modelInstance->logger(fmi2Error, "logStatusError", err);
			return fmi2Error;
		}
	}
	return fmi2OK;
}


fmi2Status fmi2GetBoolean(void* c, const fmi2ValueReference vr[], size_t nvr, fmi2Boolean value[]) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	for (size_t i=0; i<nvr; ++i) {
		try {
			bool val;
			modelInstance->getBool(vr[i], val);
			value[i] = val;
		}
		catch (std::exception & ex) {
			std::string err = ex.what();
			err += "\nError in fmi2GetBoolean()";
			modelInstance->logger(fmi2Error, "logStatusError", err);
			return fmi2Error;
		}
	}
	return fmi2OK;
}


fmi2Status fmi2GetString(void* c, const fmi2ValueReference vr[], size_t nvr, fmi2String value[]) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	for (size_t i=0; i<nvr; ++i) {
		try {
			modelInstance->getString(vr[i], value[i]);
		}
		catch (std::exception & ex) {
			std::string err = ex.what();
			err += "\nError in fmi2GetString()";
			modelInstance->logger(fmi2Error, "logStatusError", err);
			return fmi2Error;
		}
	}
	return fmi2OK;
}


fmi2Status fmi2SetReal (void* c, const fmi2ValueReference vr[], size_t nvr, const fmi2Real value[]) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	for (size_t i=0; i<nvr; ++i) {
		try {
			modelInstance->setReal(vr[i], value[i]);
		}
		catch (std::exception & ex) {
			std::string err = ex.what();
			err += "\nError in fmi2SetReal()";
			modelInstance->logger(fmi2Error, "logStatusError", err);
			return fmi2Error;
		}
	}
	return fmi2OK;
}


fmi2Status fmi2SetInteger(void* c, const fmi2ValueReference vr[], size_t nvr, const fmi2Integer value[]) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	for (size_t i=0; i<nvr; ++i) {
		try {
			modelInstance->setInt(vr[i], value[i]);
		}
		catch (std::exception & ex) {
			std::string err = ex.what();
			err += "\nError in fmi2SetInteger()";
			modelInstance->logger(fmi2Error, "logStatusError", err);
			return fmi2Error;
		}
	}
	return fmi2OK;
}


fmi2Status fmi2SetBoolean(void* c, const fmi2ValueReference vr[], size_t nvr, const fmi2Boolean value[]) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	for (size_t i=0; i<nvr; ++i) {
		try {
			modelInstance->setBool(vr[i], value[i]);
		}
		catch (std::exception & ex) {
			std::string err = ex.what();
			err += "\nError in fmi2SetBoolean()";
			modelInstance->logger(fmi2Error, "logStatusError", err);
			return fmi2Error;
		}
	}
	return fmi2OK;
}


fmi2Status fmi2SetString(void* c, const fmi2ValueReference vr[], size_t nvr, const fmi2String value[]) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	for (size_t i=0; i<nvr; ++i) {
		try {
			modelInstance->setString(vr[i], value[i]);
		}
		catch (std::exception & ex) {
			std::string err = ex.what();
			err += "\nError in fmi2SetString()";
			modelInstance->logger(fmi2Error, "logStatusError", err);
			return fmi2Error;
		}
	}
	return fmi2OK;
}


/* Getting and setting the internal FMU state */

fmi2Status fmi2GetFMUstate(void* c, fmi2FMUstate* FMUstate) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);

	if (modelInstance->m_fmuStateSize == 0) {
		modelInstance->logger(fmi2Error, "logStatusError", "fmi2GetFMUstate is called though FMU was not yet completely set up "
							  "or serialization is not supported by this FMU.");
		return fmi2Error;
	}

	// check if new alloc is needed
	if (*FMUstate == NULL) {
		// alloc new memory
		fmi2FMUstate fmuMem = malloc(modelInstance->m_fmuStateSize);
		// remember this memory array
		modelInstance->m_fmuStates.insert(fmuMem);
		// store size of memory in first 8 bytes of fmu memory
		*(size_t*)(fmuMem) = modelInstance->m_fmuStateSize;
		// return newly created FMU mem
		*FMUstate = fmuMem;
	}
	else {
		// check if FMUstate is in list of stored FMU states
		if (modelInstance->m_fmuStates.find(*FMUstate) == modelInstance->m_fmuStates.end()) {
			modelInstance->logger(fmi2Error, "logStatusError", "fmi2GetFMUstate is called with invalid FMUstate (unknown or already released pointer).");
			return fmi2Error;
		}
	}

	// now copy FMU state into memory array
	modelInstance->serializeFMUstate(*FMUstate);

	return fmi2OK;
}


fmi2Status fmi2SetFMUstate(void* c, fmi2FMUstate FMUstate) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);

	// check if FMUstate is in list of stored FMU states
	if (modelInstance->m_fmuStates.find(FMUstate) == modelInstance->m_fmuStates.end()) {
		modelInstance->logger(fmi2Error, "logStatusError", "fmi2SetFMUstate is called with invalid FMUstate (unknown or already released pointer).");
		return fmi2Error;
	}

	// now copy FMU state into memory array
	if (!modelInstance->deserializeFMUstate(FMUstate))
		return fmi2Error;

	return fmi2OK;
}


fmi2Status fmi2FreeFMUstate(void* c, fmi2FMUstate* FMUstate) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);

	if (FMUstate == NULL) {
		// similar to "delete NULL" this is a no-op
		return fmi2OK;
	}

	// check if FMUstate is in list of stored FMU states
	if (modelInstance->m_fmuStates.find(*FMUstate) == modelInstance->m_fmuStates.end()) {
		modelInstance->logger(fmi2Error, "logStatusError", "fmi2FreeFMUstate is called with invalid FMUstate (unknown or already released pointer).");
		return fmi2Error;
	}

	// free memory
	free(*FMUstate);
	// and remove pointer from list of own fmu state pointers
	modelInstance->m_fmuStates.erase(*FMUstate);
	*FMUstate = NULL; // set pointer to zero

	return fmi2OK;
}


fmi2Status fmi2SerializedFMUstateSize(fmi2Component c, fmi2FMUstate FMUstate, size_t* s) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);

	// check if FMUstate is in list of stored FMU states
	if (modelInstance->m_fmuStates.find(FMUstate) == modelInstance->m_fmuStates.end()) {
		modelInstance->logger(fmi2Error, "logStatusError", "fmi2FreeFMUstate is called with invalid FMUstate (unknown or already released pointer).");
		return fmi2Error;
	}

	// if the state of stored previously, then we must have a valid fmu size
	FMI_ASSERT(modelInstance->m_fmuStateSize != 0);

	// store size of memory to copy
	*s = modelInstance->m_fmuStateSize;

	return fmi2OK;
}


fmi2Status fmi2SerializeFMUstate(fmi2Component c, fmi2FMUstate FMUstate, fmi2Byte serializedState[], size_t /*s*/) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);

	// check if FMUstate is in list of stored FMU states
	if (modelInstance->m_fmuStates.find(FMUstate) == modelInstance->m_fmuStates.end()) {
		modelInstance->logger(fmi2Error, "logStatusError", "fmi2FreeFMUstate is called with invalid FMUstate (unknown or already released pointer).");
		return fmi2Error;
	}

	// if the state of stored previously, then we must have a valid fmu size
	FMI_ASSERT(modelInstance->m_fmuStateSize != 0);

	// copy memory
	std::memcpy(serializedState, FMUstate, modelInstance->m_fmuStateSize);

	return fmi2OK;
}


fmi2Status fmi2DeSerializeFMUstate(void* c, const char serializedState[], size_t s, fmi2FMUstate*  FMUstate) {
	(void)s;
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);

	// check if FMUstate is in list of stored FMU states
	if (modelInstance->m_fmuStates.find(FMUstate) == modelInstance->m_fmuStates.end()) {
		modelInstance->logger(fmi2Error, "logStatusError", "fmi2FreeFMUstate is called with invalid FMUstate (unknown or already released pointer).");
		return fmi2Error;
	}

	// if the state of stored previously, then we must have a valid fmu size
	FMI_ASSERT(modelInstance->m_fmuStateSize == s);

	// copy memory
	std::memcpy(*FMUstate, serializedState, modelInstance->m_fmuStateSize);

	return fmi2OK;
}



/* Getting partial derivatives */

// 33
// optional possibility to evaluate partial derivatives for the FMU
fmi2Status fmi2GetDirectionalDerivative(void* c, const unsigned int[], size_t,
																const unsigned int[], size_t,
																const double[], double[])
{
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);

	modelInstance->logger(fmi2Warning, "logStatusWarning", "fmi2GetDirectionalDerivative is called but not implemented");
	return fmi2Warning;
}



/* Enter and exit the different modes */

// Model-Exchange only
fmi2Status fmi2EnterEventMode(void* c){
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(modelInstance->m_modelExchange);
	std::string text = "fmi2EnterEventMode: Enter into event mode.";
	modelInstance->logger(fmi2OK, "logAll", text.c_str());
	return fmi2OK;
}


// Model-Exchange only
fmi2Status fmi2NewDiscreteStates(void*, fmi2EventInfo* eventInfo) {
	eventInfo->newDiscreteStatesNeeded = false;
	return fmi2OK;
}


// Model-Exchange only
fmi2Status fmi2EnterContinuousTimeMode(void* c) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(modelInstance->m_modelExchange);
	modelInstance->logger(fmi2OK, "logAll", "fmi2EnterContinuousTimeMode: Enter into continuous mode.");
	return fmi2OK;
}


// Model-Exchange only
fmi2Status fmi2CompletedIntegratorStep (void* c, fmi2Boolean,
										fmi2Boolean* enterEventMode, fmi2Boolean* terminateSimulation)
{
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(modelInstance->m_modelExchange);

	// Currently, we never enter Event mode
	*enterEventMode = false;

	modelInstance->logger(fmi2OK, "logAll", "Integrator step completed.");
	try {
		modelInstance->completedIntegratorStep();
	}
	catch (std::exception & ex) {
		std::string err = ex.what();
		err += "\nError in fmi2CompletedIntegratorStep()";
		modelInstance->logger(fmi2Error, "logStatusError", err);
		*terminateSimulation = true;
		return fmi2Error;
	}

	*terminateSimulation = false;

	return fmi2OK;
}



/* Providing independent variables and re-initialization of caching */

// Sets a new time point
// Model-Exchange only
fmi2Status fmi2SetTime (void* c, fmi2Real time) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(modelInstance->m_modelExchange);
	std::stringstream strm;
	strm << "fmi2SetTime: Set time point: " << time << " s";
	modelInstance->logger(fmi2OK, "logAll", strm.str());
	// cache new time point
	modelInstance->m_tInput = time;
	modelInstance->m_externalInputVarsModified = true;
	return fmi2OK;
}


// Model-Exchange only
fmi2Status fmi2SetContinuousStates(void* c, const fmi2Real x[], size_t nx) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(modelInstance->m_modelExchange);

	std::stringstream strm;
	strm << "fmi2SetContinuousStates: Setting continuous states with size " << nx << " with model size " << modelInstance->m_yInput.size();
	modelInstance->logger(fmi2OK, "logAll", strm.str());
	FMI_ASSERT(nx == modelInstance->m_yInput.size());

	// cache input Y vector
	std::memcpy( &(modelInstance->m_yInput[0]), x, nx*sizeof(double) );
	modelInstance->m_externalInputVarsModified = true;
	return fmi2OK;
}



/* Evaluation of the model equations */


// Model-Exchange only
fmi2Status fmi2GetDerivatives(void* c, fmi2Real derivatives[], size_t nx) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(modelInstance->m_modelExchange);

	std::stringstream strm;
	strm << "fmi2GetDerivatives: Getting derivatives with size " << nx << " with model size " << modelInstance->m_ydot.size();
	modelInstance->logger(fmi2OK, "logAll", strm.str());

	// Update model state if any of the inputs have been modified.
	// Does nothing, if the model state is already up-to-date after a previous call
	// to updateIfModified().
	try {
		modelInstance->updateIfModified();
	}
	catch (std::exception & ex) {
		std::string err = ex.what();
		err += "\nfmi2GetDerivatives: Exception while updating model";
		modelInstance->logger(fmi2Error, "logStatusError", err);
		return fmi2Error;
	}

	// return derivatives currently cached in model
	std::memcpy( derivatives, &(modelInstance->m_ydot[0]), nx * sizeof(double) );
	return fmi2OK;
}


// Model-Exchange only
fmi2Status fmi2GetEventIndicators (void*, fmi2Real[], size_t){
	return fmi2OK;
}


// Model-Exchange only
fmi2Status fmi2GetContinuousStates(void* c, fmi2Real x[], size_t nx) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);
	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(modelInstance->m_modelExchange);

	std::stringstream strm;
	strm << "fmi2GetContinuousStates: Getting continuous states with size " << nx << " with model size " << modelInstance->m_yInput.size();
	modelInstance->logger(fmi2OK, "logAll", strm.str());
	FMI_ASSERT(nx == modelInstance->m_yInput.size());

	std::memcpy( x, &(modelInstance->m_yInput[0]), nx * sizeof(double) );
	return fmi2OK;
}


// Model-Exchange only
fmi2Status fmi2GetNominalsOfContinuousStates(void*, fmi2Real[], size_t) {
	return fmi2OK;
}


// CoSim only
fmi2Status fmi2SetRealInputDerivatives(void*,	const fmi2ValueReference vr[], size_t nvr,
										const fmi2Integer order[], const fmi2Real value[])
{
	(void)order; (void)value; (void)vr; (void)nvr;
	return fmi2OK;
}


// CoSim only
fmi2Status fmi2GetRealOutputDerivatives(void*, const fmi2ValueReference vr[], size_t nvr,
										const fmi2Integer order[], fmi2Real value[])
{
	(void)order; (void)value; (void)vr; (void)nvr;
	return fmi2OK;
}


// CoSim only
fmi2Status fmi2DoStep(void* c, double currentCommunicationPoint, double communicationStepSize,
					  int noSetFMUStatePriorToCurrentPoint)
{
	InstanceData * modelInstance = static_cast<InstanceData*>(c);

	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(!modelInstance->m_modelExchange);

	if (noSetFMUStatePriorToCurrentPoint == fmi2True) {
		modelInstance->clearBuffers();
	}
	//modelInstance->logger(fmi2OK, "logAll", IBK::FormatString("fmi2DoStep: %1 += %2").arg(currentCommunicationPoint).arg(communicationStepSize));

	// if currentCommunicationPoint < current time of integrator, restore
	try {
		modelInstance->integrateTo(currentCommunicationPoint + communicationStepSize);
	}
	catch (std::exception & ex) {
		std::string err = ex.what();
		err += "\fmi2DoStep: Exception while integrating model";
		modelInstance->logger(fmi2Error, "logStatusError", err);
		return fmi2Error;
	}
	return fmi2OK;
}


// CoSim only
fmi2Status fmi2CancelStep(void* c) {
	InstanceData * modelInstance = static_cast<InstanceData*>(c);

	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(!modelInstance->m_modelExchange);
	modelInstance->logger(fmi2OK, "logAll", "fmi2CancelStep: cancel current step.");
	return fmi2OK;
}



// CoSim only
fmi2Status fmi2GetStatus(void* c, const fmi2StatusKind s, fmi2Status* value) {
	(void)s;(void)value;
	InstanceData * modelInstance = static_cast<InstanceData*>(c);

	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(!modelInstance->m_modelExchange);
	modelInstance->logger(fmi2OK, "logAll", "fmi2GetStatus: get current status.");
	return fmi2OK;
}


// CoSim only
fmi2Status fmi2GetRealStatus(void* c, const fmi2StatusKind s, fmi2Real* value) {
	(void)s;(void)value;
	InstanceData * modelInstance = static_cast<InstanceData*>(c);

	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(!modelInstance->m_modelExchange);
	modelInstance->logger(fmi2OK, "logAll", "fmi2GetRealStatus: get real status.");
	return fmi2OK;
}


// CoSim only
fmi2Status fmi2GetIntegerStatus(void* c, const fmi2StatusKind s, fmi2Integer* value) {
	(void)s;(void)value;
	InstanceData * modelInstance = static_cast<InstanceData*>(c);

	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(!modelInstance->m_modelExchange);
	modelInstance->logger(fmi2OK, "logAll", "fmi2GetIntegerStatus: get integer status.");
	return fmi2OK;
}


// CoSim only
fmi2Status fmi2GetBooleanStatus(void* c, const fmi2StatusKind s, fmi2Boolean* value) {
	(void)s;(void)value;
	InstanceData * modelInstance = static_cast<InstanceData*>(c);

	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(!modelInstance->m_modelExchange);
	modelInstance->logger(fmi2OK, "logAll", "fmi2GetBooleanStatus: get boolean status.");
	return fmi2OK;
}


// CoSim only
fmi2Status fmi2GetStringStatus(void* c, const fmi2StatusKind s, fmi2String* value) {
	(void)s;(void)value;
	InstanceData * modelInstance = static_cast<InstanceData*>(c);

	FMI_ASSERT(modelInstance != NULL);
	FMI_ASSERT(!modelInstance->m_modelExchange);
	modelInstance->logger(fmi2OK, "logAll", "fmi2GetStringStatus: get string status.");
	return fmi2OK;
}
