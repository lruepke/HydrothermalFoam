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

#include "noFluxFvPatchScalarField.H"
#include "addToRunTimeSelectionTable.H"
#include "linear.H"

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::noFlux::noFlux
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF
)
    :
    fixedGradientFvPatchScalarField(p, iF),
    rhorAUfName_("rhorAUf"),
    phigName_("phig")
{}

Foam::noFlux::noFlux
(
    const noFlux& ptf,
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
    :
    fixedGradientFvPatchScalarField(ptf, p, iF, mapper),
    rhorAUfName_(ptf.rhorAUfName_),
    phigName_(ptf.phigName_)
{
    //patchType() = ptf.patchType();

    // Map gradient. Set unmapped values and overwrite with mapped ptf
    gradient() = 0.0;
    mapper(gradient(), ptf.gradient());

    // Evaluate the value field from the gradient if the internal field is valid
    if (notNull(iF) && iF.size())
    {
        scalarField::operator=
        (
            // patchInternalField() + gradient()/patch().deltaCoeffs()
            // ***HGW Hack to avoid the construction of mesh.deltaCoeffs
            // which fails for AMI patches for some mapping operations
            patchInternalField() + gradient()*(patch().nf() & patch().delta())
        );
    }
    else
    {
        // Enforce mapping of values so we have a valid starting value. This
        // constructor is used when reconstructing fields
        mapper(*this, ptf);
    }
}

Foam::noFlux::noFlux
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const dictionary& dict
)
    :
    fixedGradientFvPatchScalarField(p, iF),
    rhorAUfName_(dict.lookupOrDefault<word>("rhorAUf", "rhorAUf")),
    phigName_(dict.lookupOrDefault<word>("phig", "phig"))
{
    if (dict.found("value") && dict.found("gradient"))
    {
        fvPatchField<scalar>::operator=
        (
            scalarField("value", dict, p.size())
        );
        gradient() = scalarField("gradient", dict, p.size());
    }
    else
    {
        fvPatchField<scalar>::operator=(patchInternalField());
        gradient() = 0.0;
    }
}

/*Foam::noFlux::noFlux
(
    const noFlux& ptf
)
    :
    fixedGradientFvPatchScalarField(ptf),
    rhorAUfName_(ptf.rhorAUfName_),
    phigName_(ptf.phigName_)
{}*/

Foam::noFlux::noFlux
(
    const noFlux& ptf,
    const DimensionedField<scalar, volMesh>& iF
)
    :
    fixedGradientFvPatchScalarField(ptf, iF),
    rhorAUfName_(ptf.rhorAUfName_),
    phigName_(ptf.phigName_)
{}

// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void Foam::noFlux::updateCoeffs()
{
    if (updated())
    {
        return;
    }

    const fvsPatchField<scalar>& rhorAUf=
        patch().lookupPatchField<surfaceScalarField, scalar>(rhorAUfName_);

    const fvsPatchField<scalar>& phig=
        patch().lookupPatchField<surfaceScalarField, scalar>(phigName_);

    gradient()=phig/rhorAUf/(patch().magSf());

    fixedGradientFvPatchScalarField::updateCoeffs();
}

void Foam::noFlux::write(Ostream& os) const
{
    fixedGradientFvPatchScalarField::write(os);
    writeEntry(os, "value", *this);
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
makePatchTypeField
(
    fvPatchScalarField,
    noFlux
);
}

// ************************************************************************* //