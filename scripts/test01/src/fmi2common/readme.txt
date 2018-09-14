This directory shall be checked out below the src directory of an FMU project. Example:

MyFMU_v2
├── projects
│   ├── Qt
│   │   ├── MyFMU_v2.pro
│   └── VC10
│       ├── MyFMU_v2.vcxproj
│       └── MyFMU_v2.vcxproj.filters
└── src
	├── fmi2common                      --> svn:externals "^/../FMU/trunk/fmi2common fmi2common"
	│   ├── fmi2Functions_complete.h
	│   ├── fmi2Functions.cpp
	│   ├── fmi2Functions.h
	│   ├── fmi2FunctionTypes.h
	│   ├── fmi2TypesPlatform.h
	│   ├── InstanceDataCommon.cpp
	│   └── InstanceDataCommon.h
	├── FMUSpecificCode.cpp
	└── FMUSpecificCode.h


The code FMUSpecificCode.cpp must implement the following c-functions:

Also, these files should include a class that derives from class InstanceData and implement the
relevant virtual functions.



