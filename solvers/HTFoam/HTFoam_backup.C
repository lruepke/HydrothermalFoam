/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2011-2016 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------*/

/**
 * @file HTFoam.C
 * @author Zhikui Guo (zhikuiguo@live.cn)
 * @brief single phase Hydrothermal Darcy flow solver
 * \dotfile HTFoam.dot
 * @version 1.0
 * @date 2019-10-14
 * 
 * @copyright Copyright (c) 2019
 * 
 */
// ---------------xThermo---------------------
#include "thermo.h"
#include "H2ONaCl.h"
//---------------------------------------------

#include "fvCFD.H"
#include "fvModels.H"
#include "fvConstraints.H"
#include "pimpleControl.H"
#include "simpleMatrix.H"  //for investigating coefficients matrix

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    #include "postProcess.H"

    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createControl.H"
    #include "createFields.H"
    #include "createTimeControls.H"
    #include "initContinuityErrs.H"

    // initialize pressure: correct initial hydrostatic pressure is very important!!!
    if(runTime.timeName()=="0")
    {
        Info << "Initialize hydrostatic pressure" << endl;       
        //#include "initpEqn_lhr.H"
        #include "initpEqn_chatgpt.H"
        Info << "Initialize hydrostatic pressure end" << endl;

    }   
    
    while (runTime.run())
    {
        #include "readTimeControls.H"
        #include "compressibleCourantNo.H"
        #include "setDeltaT.H"

        runTime++;

        Info<< "Time = " << runTime.timeName() << nl << endl;

        /* while (pimple.loop())
        {
            #include "TEqn.H"
            // --- Pressure corrector loop
            // while (pimple.correct())
            {
            #include "pEqn.H"
                }
        }*/

        #include "TEqn.H"
        #include "updateProps.H"
        #include "pEqn.H"

        // #include "continuityErrs.H"
        runTime.write();
        Info<< "ExecutionTime = " << runTime.elapsedCpuTime() << " s"
            << "  ClockTime = " << runTime.elapsedClockTime() << " s"
            << nl << endl;
    }

    #include "releasexThermo.H"
    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
