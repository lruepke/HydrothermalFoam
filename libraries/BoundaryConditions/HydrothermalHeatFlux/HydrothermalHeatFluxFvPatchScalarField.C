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

#include "HydrothermalHeatFluxFvPatchScalarField.H"
#include "addToRunTimeSelectionTable.H"
#include "linear.H"
// #include "fvPatchFieldMapper.H"

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::HydrothermalHeatFlux::HydrothermalHeatFlux
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF
)
    :
    fixedGradientFvPatchScalarField(p, iF),
    krName_("kr"),
    q_(p.size(), 0.0),
    shape_("fixed"),
    qmax_(0),
    qmin_(0),
    x0_(0),
    z0_(0),
    c_(1)
{}

Foam::HydrothermalHeatFlux::HydrothermalHeatFlux
(
    const HydrothermalHeatFlux& ptf,
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
    :
    fixedGradientFvPatchScalarField(ptf, p, iF, mapper),
    krName_(ptf.krName_),
    q_(ptf.q_), //why q_(ptf.q_, mapper) is used in turbulentHeatFluxTemperatureFvPatchScalarField.C ?
    shape_(ptf.shape_),
    qmax_(ptf.qmax_),
    qmin_(ptf.qmin_),
    x0_(ptf.x0_),
    z0_(ptf.z0_),
    c_(ptf.c_),
    x1_(ptf.x1_),
    x2_(ptf.x2_),
    q1_(ptf.q1_),
    q2_(ptf.q2_)
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

Foam::HydrothermalHeatFlux::HydrothermalHeatFlux
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const dictionary& dict
)
    :
    fixedGradientFvPatchScalarField(p, iF),
    krName_(dict.lookupOrDefault<word>("kr", "kr")),
    q_("q", dict, p.size()),
    shape_(dict.lookupOrDefault<word>("shape", "fixed")),
    qmax_(dict.lookupOrDefault<scalar>("qmax", 0)),
    qmin_(dict.lookupOrDefault<scalar>("qmin", 0)),
    x0_(dict.lookupOrDefault<scalar>("x0", 0)),
    z0_(dict.lookupOrDefault<scalar>("z0_", 0)),
    c_(dict.lookupOrDefault<scalar>("c", 1)),
    x1_(dict.lookupOrDefault<scalar>("x1", 0)),
    x2_(dict.lookupOrDefault<scalar>("x2", 1)),
    q1_(dict.lookupOrDefault<scalar>("q1", 0)),
    q2_(dict.lookupOrDefault<scalar>("q2", 0))
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

// Foam::HydrothermalHeatFlux::HydrothermalHeatFlux
// (
//     const HydrothermalHeatFlux& ptf
// )
//     :
//     fixedGradientFvPatchScalarField(ptf),
//     krName_(ptf.krName_),
//     q_(ptf.q_),
//     shape_(ptf.shape_),
//     qmax_(ptf.qmax_),
//     qmin_(ptf.qmin_),
//     x0_(ptf.x0_),
//     z0_(ptf.z0_),
//     c_(ptf.c_),
//     x1_(ptf.x1_),
//     x2_(ptf.x2_),
//     q1_(ptf.q1_),
//     q2_(ptf.q2_)
// {}

Foam::HydrothermalHeatFlux::HydrothermalHeatFlux
(
    const HydrothermalHeatFlux& ptf,
    const DimensionedField<scalar, volMesh>& iF
)
    :
    fixedGradientFvPatchScalarField(ptf, iF),
    krName_(ptf.krName_),
    q_(ptf.q_),
    shape_(ptf.shape_),
    qmax_(ptf.qmax_),
    qmin_(ptf.qmin_),
    x0_(ptf.x0_),
    z0_(ptf.z0_),
    c_(ptf.c_),
    x1_(ptf.x1_),
    x2_(ptf.x2_),
    q1_(ptf.q1_),
    q2_(ptf.q2_)
{}

// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void Foam::HydrothermalHeatFlux::updateCoeffs()
{
    if (updated())
    {
        return;
    }

    const IOdictionary& thermophysicalProperties = db().lookupObject<IOdictionary>("thermophysicalProperties");
    // const scalar kr(readScalar(transportProperties.lookup("kr")));
    dimensionedScalar kr(thermophysicalProperties.subDict("mixture").subDict("porousMedia").lookup(krName_));
    gradient() = q_/kr.value();
    // 1. gaussian shape
    if(shape_=="gaussian2d")
    {
        scalarField x(this->patch().Cf().component(0)); 
        gradient()=(qmin_ + (qmax_-qmin_)*exp(-((x-x0_)*(x-x0_))/(2*c_*c_)))/kr.value(); 
    }else if(shape_=="gaussian3d")
    {
        scalarField x(this->patch().Cf().component(0)); 
        scalarField y(this->patch().Cf().component(2)); 
        gradient()=(qmin_ + (qmax_-qmin_)*exp(-((x-x0_)*(x-x0_) + (y-z0_)*(y-z0_))/(2*c_*c_)))/kr.value(); 
    }else if(shape_=="linear2d")
    {
        scalar slope = (q2_ - q1_)/(x2_ - x1_);
        scalarField x(this->patch().Cf().component(0)); 
        gradient()=((x-x1_)*slope + q1_)/kr.value(); 
    }
    fixedGradientFvPatchScalarField::updateCoeffs();
}

void Foam::HydrothermalHeatFlux::write(Ostream& os) const
{
    fixedGradientFvPatchScalarField::write(os);
    writeEntry(os, "q", q_);
    writeEntry(os, "value", *this);
    writeEntryIfDifferent<word>(os, "kr","kr",krName_);
    writeEntry(os, "shape", shape_);
    if(shape_=="gaussian2d")
    {
        writeEntry(os, "x0", x0_);
        writeEntry(os, "c", c_);
        writeEntry(os, "qmin", qmin_);
        writeEntry(os, "qmax", qmax_);
    }else if(shape_=="gaussian3d")
    {
        writeEntry(os, "x0", x0_);
        writeEntry(os, "z0", z0_);
        writeEntry(os, "c", c_);
        writeEntry(os, "qmin", qmin_);
        writeEntry(os, "qmax", qmax_);
    }
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
makePatchTypeField
(
    fvPatchScalarField,
    HydrothermalHeatFlux
);
}

// ************************************************************************* //