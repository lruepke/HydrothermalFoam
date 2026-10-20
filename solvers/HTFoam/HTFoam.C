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
    #include "createTimeControls.H" // check time stepping
    #include "initContinuityErrs.H"

    // initialize pressure: correct initial hydrostatic pressure is very important!!!
    if(runTime.timeName()=="0")
    {
        Info << "Initialize hydrostatic pressure" << endl;       
        //#include "initpEqn_lhr.H"
        #include "initpEqn.H"
        Info << "Initialize hydrostatic pressure end" << endl;
    }   
    
    // extra loop controls
    const IOdictionary& fvSol = mesh.thisDb().lookupObject<IOdictionary>("fvSolution");
    const dictionary& pimDict = fvSol.subDict("PIMPLE");

    const label nNonOrth = pimDict.lookupOrDefault<label>("nNonOrthogonalCorrectors", 0);

    label K = 0;   // number of extra p↔T coupling iterations per time step
    if (fvSol.found("PTCOUPLING"))
    {
        const dictionary& ptcDict = fvSol.subDict("PTCOUPLING");
        K = ptcDict.lookupOrDefault<label>("tightCouplingIters", 0);
    }
    const label Keff = (K > 0) ? K : 1;

    // --- main time loop
    while (runTime.run())
    {
        #include "readTimeControls.H"
        #include "compressibleCourantNo.H"
        #include "setDeltaT.H"
        //#include "porousCourantNo.H"

        runTime++;
        Info<< "Time = " << runTime.timeName() << nl << endl;

        // ---------- tiny Picard loop per time step ----------

        volScalarField pPrevPicard("pPrevPicard", p);
        volScalarField TPrevPicard("TPrevPicard", T);

        for (label it = 0; it < Keff; ++it)
        {
            const bool finalIter = (it == Keff - 1);

            // will be set by the includes
            scalar __initResP = GREAT;
            scalar __initResT = GREAT;

            // 1) Pressure correction (non-orth), updates phi and U
            {
                // make nNonOrth visible to the include
                const label __nNonOrth = nNonOrth;
                {   // scope to avoid name clashes between multiple includes
                    #include "pEqn.H"
                }
            }

            // 2) Temperature with the updated phi
            {
                const bool __finalTEqn = finalIter;  // pass a flag into include
                {   // scope
                    #include "TEqn.H"
                }
            }

            // 3) Update properties from current (T, p)
            #include "updateProps.H"
            fvModels.correct();

            // --- monitoring: max changes this Picard iteration
            tmp<volScalarField> tDp = mag(p - pPrevPicard);
            tmp<volScalarField> tDt = mag(T - TPrevPicard);
            const scalar maxDeltaP = gMax(tDp());
            const scalar maxDeltaT = gMax(tDt());

            Info<< "Picard it " << it
                << "  max|Delta p|=" << maxDeltaP
                << "  max|Delta T|=" << maxDeltaT
                << (finalIter ? "  [final]" : "")
                << nl;

            // update snapshots for next iteration
            pPrevPicard = p;
            TPrevPicard = T;
        }

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
