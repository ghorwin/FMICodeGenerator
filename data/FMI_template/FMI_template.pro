# ----------------------------------
# Qt Project for building FMU 
# ----------------------------------
#
# This file is part of FMICodeGenerator (https://github.com/ghorwin/FMICodeGenerator)
# 
# BSD 3-Clause License
#
# Copyright (c) 2018, Andreas Nicolai
# All rights reserved.
#
# see https://github.com/ghorwin/FMICodeGenerator/blob/master/LICENSE for details.


TARGET = FMI_template
TEMPLATE = lib

# no GUI
QT -= core gui

CONFIG(debug, debug|release) {
	windows {
		DLLDESTDIR = bin/debug$${DIR_PREFIX}
	}
	else {
		DESTDIR = bin/debug$${DIR_PREFIX}
	}
}
else {
	windows {
		DLLDESTDIR = bin/release$${DIR_PREFIX}
	}
	else {
		DESTDIR = bin/release$${DIR_PREFIX}
	}
}

#DEFINES += FMI2_FUNCTION_PREFIX=FMI_template_

unix|mac {
	VER_MAJ = 1
	VER_MIN = 0
	VER_PAT = 0
	VERSION = $${VER_MAJ}.$${VER_MIN}.$${VER_PAT}
}

unix {
	# move actual lib to TARGET.so
	QMAKE_POST_LINK += $$quote(mv $${DESTDIR}/lib$${TARGET}.so.$${VER_MAJ}.$${VER_MIN}.$${VER_PAT} $${DESTDIR}/$${TARGET}.so)  &&
	# remove symlinks
	QMAKE_POST_LINK += $$quote(rm $${DESTDIR}/lib$${TARGET}.so.$${VER_MAJ}.$${VER_MIN})  &&
	QMAKE_POST_LINK += $$quote(rm $${DESTDIR}/lib$${TARGET}.so.$${VER_MAJ}) &&
	QMAKE_POST_LINK += $$quote(rm $${DESTDIR}/lib$${TARGET}.so)
}


INCLUDEPATH = src

SOURCES += \
	src/fmi2common/fmi2Functions.cpp \
	src/fmi2common/InstanceData.cpp \
	src/FMI_template.cpp

HEADERS += \
	src/fmi2common/fmi2Functions.h \
	src/fmi2common/fmi2Functions_complete.h \
	src/fmi2common/fmi2FunctionTypes.h \
	src/fmi2common/fmi2TypesPlatform.h \
	src/fmi2common/InstanceData.h \
	src/FMI_template.h


