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

#ifndef Math003Part3H
#define Math003Part3H

#include "fmi2common/InstanceData.h"

/*! This class wraps all data needed for a single instance of the FMU. */
class Math003Part3 : public InstanceData {
public:
	/*! Initializes empty instance. */
	Math003Part3();

	/*! Destructor, writes out cached results from Therakles. */
	~Math003Part3();

	/*! Initializes model */
	void init();

	/*! This function triggers a state-update of the embedded model whenever our cached input
		data differs from the input data in the model.
	*/
	void updateIfModified();

	/*! Called from fmi2DoStep(). */
	virtual void integrateTo(double tCommunicationIntervalEnd);

	// Functions for getting/setting the state

	/*! This function computes the size needed for full serizalization of
		the FMU and stores the size in m_fmuStateSize.
		\note The size includes the leading 8byte for the 64bit integer size
		of the memory array (for testing purposes).
	*/
	virtual void computeFMUStateSize();

	/*! Copies the internal state of the FMU to the memory array pointed to by FMUstate.
		Memory array always has size m_fmuStateSize.
	*/
	virtual void serializeFMUstate(void * FMUstate);

	/*! Copies the content of the memory array pointed to by FMUstate to the internal state of the FMU.
		Memory array always has size m_fmuStateSize.
	*/
	virtual void deserializeFMUstate(void * FMUstate);

	/*! Cached current time point of the FMU, defines starting point for time integration in co-simulation mode. */
	double m_currentTimePoint;
}; // class Math003Part3

#endif // Math003Part3H
