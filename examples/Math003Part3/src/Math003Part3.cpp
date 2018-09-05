/*	FMI Interface for the MasterSim Test Cases
  Written by Andreas Nicolai (2018), andreas.nicolai@gmx.net

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "fmi2common/fmi2Functions.h"
#include "fmi2common/fmi2FunctionTypes.h"
#include "Math003Part3.h"

// FMI interface variables

#define FMI_INPUT_X3 3
#define FMI_OUTPUT_X4 4



// *** Variables and functions to be implemented in user code. ***

// *** GUID that uniquely identifies this FMU code
const char * const InstanceData::GUID = "{471a3b52-4923-44d8-ab4a-fcdb813c7324}";

// *** Factory function, creates model specific instance of InstanceData-derived class
InstanceData * InstanceData::create() {
	return new Math003Part3; // caller takes ownership
}


Math003Part3::Math003Part3() :
	InstanceData()
{
	// initialize input variables
	m_realInput[FMI_INPUT_X3] = 0;

	// initialize output variables
	m_realOutput[FMI_OUTPUT_X4] = 0; // initial value
}


Math003Part3::~Math003Part3() {
}


// create a model instance
void Math003Part3::init() {
	logger(fmi2OK, "progress", "Starting initialization.");

	if (m_modelExchange) {
		// initialize states
		m_yInput.resize(1);
		m_ydot.resize(1);

		m_yInput[0] = 0;	// = x4
		m_ydot[0] = 0;		// = \dot{x4}
	}
	else {
		// initialize states, these are used for our internal time integration
		m_yInput.resize(1);
		m_yInput[0] = 0;			// = x4, initial value
		// initialize integrator for co-simulation
		m_currentTimePoint = 0;
	}

	logger(fmi2OK, "progress", "Initialization complete.");
}


void Math003Part3::updateIfModified() {
	if (!m_externalInputVarsModified)
		return;
	double x3 = m_realInput[FMI_INPUT_X3];

	// compute time derivative
	m_ydot[0] = x3*2;

	// output variable is the same as the conserved quantity
	m_realOutput[FMI_OUTPUT_X4] = m_yInput[0];

	// reset externalInputVarsModified flag
	m_externalInputVarsModified = false;
}


// only for Co-simulation
void Math003Part3::integrateTo(double tCommunicationIntervalEnd) {

	// state of FMU before integration:
	//   m_currentTimePoint = t_IntervalStart;
	//   m_y[0] = x4(t_IntervalStart)
	//   m_realInput[FMI_INPUT_X3] = x3(t_IntervalStart...tCommunicationIntervalEnd) = const

	// compute time step size
	double dt = tCommunicationIntervalEnd - m_currentTimePoint;
	double x3 = m_realInput[FMI_INPUT_X3];
	double deltaX4 = dt*x3*2;

	m_yInput[0] += deltaX4;
	m_realOutput[FMI_OUTPUT_X4] = m_yInput[0];
	m_currentTimePoint = tCommunicationIntervalEnd;

	// state of FMU after integration:
	//   m_currentTimePoint = tCommunicationIntervalEnd;
	//   m_y[0] = x4(tCommunicationIntervalEnd)
	//   m_realOutput[FMI_INPUT_X4] = x4(tCommunicationIntervalEnd)
}


void Math003Part3::computeFMUStateSize() {
	// distinguish between ModelExchange and CoSimulation
	if (m_modelExchange) {
		// store time, y and ydot, and output
		m_fmuStateSize = sizeof(double)*4;
	}
	else {
		// store time, y and output
		m_fmuStateSize = sizeof(double)*3;
	}
}


void Math003Part3::serializeFMUstate(void * FMUstate) {
	double * dataStart = (double*)FMUstate;
	if (m_modelExchange) {
		*dataStart = m_tInput;
		++dataStart;
		*dataStart = m_yInput[0];
		++dataStart;
		*dataStart = m_ydot[0];
		++dataStart;
		*dataStart = m_realOutput[FMI_OUTPUT_X4];
	}
	else {
		*dataStart = m_currentTimePoint;
		++dataStart;
		*dataStart = m_yInput[0];
		++dataStart;
		*dataStart = m_realOutput[FMI_OUTPUT_X4];
	}
}


void Math003Part3::deserializeFMUstate(void * FMUstate) {
	const double * dataStart = (const double*)FMUstate;
	if (m_modelExchange) {
		m_tInput = *dataStart;
		++dataStart;
		m_yInput[0] = *dataStart;
		++dataStart;
		m_ydot[0] = *dataStart;
		++dataStart;
		m_realOutput[FMI_OUTPUT_X4] = *dataStart;
		m_externalInputVarsModified = true;
	}
	else {
		m_currentTimePoint = *dataStart;
		++dataStart;
		m_yInput[0] = *dataStart;
		++dataStart;
		m_realOutput[FMI_OUTPUT_X4] = *dataStart;
	}
}


