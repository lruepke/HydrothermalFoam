/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2011-2016 OpenFOAM Foundation
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

#include "HydrothermalMassFluxPressureFvPatchScalarField.H"
#include "addToRunTimeSelectionTable.H"
#include "linear.H"

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::HydrothermalMassFluxPressure::HydrothermalMassFluxPressure
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF
)
    :
    fixedGradientFvPatchScalarField(p, iF),
    rhorAUfName_("rhorAUf"),
    phigName_("phig"),
    q_(p.size(), 0.0)
{}

Foam::HydrothermalMassFluxPressure::HydrothermalMassFluxPressure
(
    const HydrothermalMassFluxPressure& ptf,
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
    :
    fixedGradientFvPatchScalarField(ptf, p, iF, mapper),
    rhorAUfName_(ptf.rhorAUfName_),
    phigName_(ptf.phigName_),
    q_(ptf.q_)
{}

Foam::HydrothermalMassFluxPressure::HydrothermalMassFluxPressure
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const dictionary& dict
)
    :
    fixedGradientFvPatchScalarField(p, iF),
    rhorAUfName_(dict.lookupOrDefault<word>("rhorAUf", "rhorAUf")),
    phigName_(dict.lookupOrDefault<word>("phig", "phig")),
    q_("q", dict, p.size())
{
    fvPatchField<scalar>::operator=(patchInternalField());
    gradient() = 0.0;
}

// 22Mar2024 commented this because it led to an error, OF10 does not allow constructor w/o internal Field reference
//Foam::HydrothermalMassFluxPressure::HydrothermalMassFluxPressure
//(
 //   const HydrothermalMassFluxPressure& ptf
//)
//    :
//    fixedGradientFvPatchScalarField(ptf),
//    rhorAUfName_(ptf.rhorAUfName_),
//    phigName_(ptf.phigName_),
//    q_(ptf.q_)
//{}

Foam::HydrothermalMassFluxPressure::HydrothermalMassFluxPressure
(
    const HydrothermalMassFluxPressure& ptf,
    const DimensionedField<scalar, volMesh>& iF
)
    :
    fixedGradientFvPatchScalarField(ptf, iF),
    rhorAUfName_(ptf.rhorAUfName_),
    phigName_(ptf.phigName_),
    q_(ptf.q_)
{}

// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void Foam::HydrothermalMassFluxPressure::updateCoeffs()
{
    if (updated())
    {
        return;
    }

    const fvsPatchField<scalar>& rhorAUf=
        patch().lookupPatchField<surfaceScalarField, scalar>(rhorAUfName_);

    const fvsPatchField<scalar>& phig=
        patch().lookupPatchField<surfaceScalarField, scalar>(phigName_);
    
    gradient()=(phig - q_)/rhorAUf/(patch().magSf());

    fixedGradientFvPatchScalarField::updateCoeffs();
}

void Foam::HydrothermalMassFluxPressure::write(Ostream& os) const
{
    fixedGradientFvPatchScalarField::write(os);
    // writeEntryIfDifferent<word>(os, "rhorAUf","rhorAUf",rhorAUfName_);
    writeEntry(os, "q", q_);
    // writeEntry(os, "value", *this);
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
makePatchTypeField
(
    fvPatchScalarField,
    HydrothermalMassFluxPressure
);
}

// ************************************************************************* //