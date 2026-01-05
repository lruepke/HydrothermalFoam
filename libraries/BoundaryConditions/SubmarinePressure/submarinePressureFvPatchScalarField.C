/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Copyright (C) 2016-2019 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "submarinePressureFvPatchScalarField.H"
#include "addToRunTimeSelectionTable.H"
#include "fvPatchFieldMapper.H"
#include "volFields.H"
#include "surfaceFields.H"
#include "uniformDimensionedFields.H"

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::submarinePressureFvPatchScalarField::
submarinePressureFvPatchScalarField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF
)
:
    fixedValueFvPatchScalarField(p, iF),
    rhoValue_(1013),
    p_Atmospheric(0.1e6)
{}


Foam::submarinePressureFvPatchScalarField::
submarinePressureFvPatchScalarField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const dictionary& dict
)
:
    fixedValueFvPatchScalarField(p, iF, dict),
    rhoValue_(dict.lookupOrDefault<scalar>("rhoValue",1013)),
    // rhoValue_(readScalar(dict.lookup("rhoValue"))),
    p_Atmospheric(0.1e6)
{}


Foam::submarinePressureFvPatchScalarField::
submarinePressureFvPatchScalarField
(
    const submarinePressureFvPatchScalarField& ptf,
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    fixedValueFvPatchScalarField(ptf, p, iF, mapper),
    rhoValue_(ptf.rhoValue_),
    p_Atmospheric(0.1e6)
{}


// Foam::submarinePressureFvPatchScalarField::
// submarinePressureFvPatchScalarField
// (
//     const submarinePressureFvPatchScalarField& ptf
// )
// :
//     fixedValueFvPatchScalarField(ptf),
//     rhoValue_(ptf.rhoValue_),
//     p_Atmospheric(0.1e6)
// {}


Foam::submarinePressureFvPatchScalarField::
submarinePressureFvPatchScalarField
(
    const submarinePressureFvPatchScalarField& ptf,
    const DimensionedField<scalar, volMesh>& iF
)
:
    fixedValueFvPatchScalarField(ptf, iF),
    rhoValue_(ptf.rhoValue_),
    p_Atmospheric(0.1e6)
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void Foam::submarinePressureFvPatchScalarField::updateCoeffs()
{
    if (updated())
    {
        return;
    }
    const uniformDimensionedVectorField& g = db().lookupObject<uniformDimensionedVectorField>("g");
    // atmospheric pressure plus hydrostatic pressure of water
    operator==
    (
    p_Atmospheric + rhoValue_ * (g.value() & patch().Cf())
    );
    fixedValueFvPatchScalarField::updateCoeffs();
}


void Foam::submarinePressureFvPatchScalarField::write
(
    Ostream& os
) const
{
    fvPatchScalarField::write(os);
    writeEntry(os, "rhoValue_", rhoValue_);
    writeEntry(os, "value", *this);
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
    makePatchTypeField
    (
        fvPatchScalarField,
        submarinePressureFvPatchScalarField
    );
}

// ************************************************************************* //
