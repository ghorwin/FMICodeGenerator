/* Inquire version numbers of header files */
1   FMI2_Export const char* fmi2GetTypesPlatform(void);
2   FMI2_Export const char* fmi2GetVersion(void);
7   FMI2_Export fmi2Status  fmi2SetDebugLogging(void* c, int loggingOn, size_t nCategories, const (const char* categories)[]);

/* Creation and destruction of FMU instances */
3   FMI2_Export void* fmi2Instantiate(const char* instanceName, fmi2Type fmuType, const char* fmuGUID, 
        const char* fmuResourceLocation, const fmi2CallbackFunctions* functions, int visible, int loggingOn);
6   FMI2_Export void fmi2FreeInstance(void* c);

/* Enter and exit initialization mode, terminate and reset */
32   FMI2_Export fmi2Status fmi2SetupExperiment(void* c, int toleranceDefined, double tolerance, double startTime, int stopTimeDefined, double stopTime);
4   FMI2_Export fmi2Status fmi2EnterInitializationMode(void* c);
5   FMI2_Export fmi2Status fmi2ExitInitializationMode(void* c);
22   FMI2_Export fmi2Status fmi2Terminate(void* c);
23   FMI2_Export fmi2Status fmi2Reset(void* c);

/* Getting and setting variables values */
14   FMI2_Export fmi2Status fmi2GetReal(void* c, const unsigned int vr[], size_t nvr, double value[]);
18   FMI2_Export fmi2Status fmi2GetInteger(void* c, const unsigned int vr[], size_t nvr, int value[]);
19   FMI2_Export fmi2Status fmi2GetBoolean(void* c, const unsigned int vr[], size_t nvr, int value[]);
20   FMI2_Export fmi2Status fmi2GetString (void* c, const unsigned int vr[], size_t nvr, (const char* value)[]);

13   FMI2_Export fmi2Status fmi2SetReal(void* c, const unsigned int vr[], size_t nvr, const double value[]);
15   FMI2_Export fmi2Status fmi2SetInteger(void* c, const unsigned int vr[], size_t nvr, const int value[]);
16   FMI2_Export fmi2Status fmi2SetBoolean(void* c, const unsigned int vr[], size_t nvr, const int value[]);
17   FMI2_Export fmi2Status fmi2SetString(void* c, const unsigned int vr[], size_t nvr, const (const char* value[]));

/* Getting and setting the internal FMU state */
26   FMI2_Export fmi2Status fmi2GetFMUstate(void* c, fmi2FMUstate* FMUstate);
27   FMI2_Export fmi2Status fmi2SetFMUstate(void* c, fmi2FMUstate FMUstate);
28   FMI2_Export fmi2Status fmi2FreeFMUstate(void* c, fmi2FMUstate* FMUstate);
29   FMI2_Export fmi2Status fmi2SerializedFMUstateSize(void* c, fmi2FMUstate FMUstate, size_t* size);
30   FMI2_Export fmi2Status fmi2SerializeFMUstate(void* c, fmi2FMUstate FMUstate, char serializedState[], size_t size);
31   FMI2_Export fmi2Status fmi2DeSerializeFMUstate(void* c, const char serializedState[], size_t size, fmi2FMUstate* FMUstate);

/* Getting partial derivatives */
33   FMI2_Export fmi2Status fmi2GetDirectionalDerivative(void* c, const unsigned int vUnknown_ref[], size_t nUnknown,
                                                                   const unsigned int vKnown_ref[], size_t nKnown,
                                                                   const double vKnown[], double dvUnknown[]);

/***************************************************
Functions for FMI2 for Model Exchange
****************************************************/

/* Enter and exit the different modes */
21   FMI2_Export fmi2Status fmi2EnterEventMode(void* c);
34   FMI2_Export fmi2Status fmi2NewDiscreteStates(void* c, fmi2EventInfo* fmi2eventInfo);
35   FMI2_Export fmi2Status fmi2EnterContinuousTimeMode(void* c);
24   FMI2_Export fmi2Status fmi2CompletedIntegratorStep(void* c, int noSetFMUStatePriorToCurrentPoint, int* enterEventMode, int* terminateSimulation);

/* Providing independent variables and re-initialization of caching */
8   FMI2_Export fmi2Status fmi2SetTime(void* c, double time);
9   FMI2_Export fmi2Status fmi2SetContinuousStates(void* c, const double x[], size_t nx);

/* Evaluation of the model equations */
12   FMI2_Export fmi2Status fmi2GetDerivatives(void* c, double derivatives[], size_t nx);
25   FMI2_Export fmi2Status fmi2GetEventIndicators(void* c, double eventIndicators[], size_t ni);
10   FMI2_Export fmi2Status fmi2GetContinuousStates(void* c, double x[], size_t nx);
11   FMI2_Export fmi2Status fmi2GetNominalsOfContinuousStates(void* c, double x_nominal[], size_t nx);

   
/***************************************************
Functions for FMI2 for Co-Simulation
****************************************************/

/* Simulating the slave */
   FMI2_Export fmi2Status fmi2SetRealInputDerivatives(void* c, const unsigned int vr[], size_t nvr, const int order[], const double value[]);
   FMI2_Export fmi2Status fmi2GetRealOutputDerivatives(void* c, const unsigned int vr[], size_t nvr, const int order[], double value[]);

   FMI2_Export fmi2Status fmi2DoStep(void* c, double currentCommunicationPoint, double communicationStepSize, int noSetFMUStatePriorToCurrentPoint);
   FMI2_Export fmi2Status fmi2CancelStep (void* c);

/* Inquire slave status */
   FMI2_Export fmi2Status fmi2GetStatus(void* c, const fmi2StatusKind s, fmi2Status* value);
   FMI2_Export fmi2Status fmi2GetRealStatus(void* c, const fmi2StatusKind s, double* value);
   FMI2_Export fmi2Status fmi2GetIntegerStatus(void* c, const fmi2StatusKind s, int* value);
   FMI2_Export fmi2Status fmi2GetBooleanStatus(void* c, const fmi2StatusKind s, int* value);
   FMI2_Export fmi2Status fmi2GetStringStatus(void* c, const fmi2StatusKind s, const char** value);
