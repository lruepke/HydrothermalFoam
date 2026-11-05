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
#include "volFields.H"
#include <cmath>
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
    conductivityFieldName_(),
    q_(p.size(), 0.0),
    shape_("fixed"),
    qmax_(0),
    qmin_(0),
    x0_(0),
    z0_(0),
    c_(1),
    x1_(0), x2_(1), q1_(0), q2_(0)
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
    conductivityFieldName_(ptf.conductivityFieldName_),
    q_(mapper(ptf.q_)()),
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
    conductivityFieldName_(dict.lookupOrDefault<word>("conductivityField", word::null)),
    q_("q", dict, p.size()),
    shape_(dict.lookupOrDefault<word>("shape", "fixed")),
    qmax_(dict.lookupOrDefault<scalar>("qmax", 0)),
    qmin_(dict.lookupOrDefault<scalar>("qmin", 0)),
    x0_(dict.lookupOrDefault<scalar>("x0", 0)),
    z0_(dict.lookupOrDefault<scalar>("z0", dict.lookupOrDefault<scalar>("z0_", 0))),
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

Foam::HydrothermalHeatFlux::HydrothermalHeatFlux
(
    const HydrothermalHeatFlux& ptf,
    const DimensionedField<scalar, volMesh>& iF
)
    :
    fixedGradientFvPatchScalarField(ptf, iF),
    krName_(ptf.krName_),
    conductivityFieldName_(ptf.conductivityFieldName_),
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

void Foam::HydrothermalHeatFlux::autoMap(const fvPatchFieldMapper& mapper)
{
    fixedGradientFvPatchScalarField::autoMap(mapper);
    mapper(q_, q_);
}

void Foam::HydrothermalHeatFlux::rmap(const fvPatchScalarField& field, const labelList& addr)
{
    fixedGradientFvPatchScalarField::rmap(field, addr);
    q_.rmap(refCast<const HydrothermalHeatFlux>(field).q_, addr);
}

void Foam::HydrothermalHeatFlux::reset(const fvPatchScalarField& field)
{
    fixedGradientFvPatchScalarField::reset(field);
    q_.reset(refCast<const HydrothermalHeatFlux>(field).q_);
}

void Foam::HydrothermalHeatFlux::updateCoeffs()
{
    if (updated())
    {
        return;
    }

    const dimensionSet conductivityDimensions(1, 1, -3, -1, 0, 0, 0);
    scalarField conductivity(patch().size());
    if (!conductivityFieldName_.empty())
    {
        const volScalarField& k = db().lookupObject<volScalarField>(conductivityFieldName_);
        if (k.dimensions() != conductivityDimensions)
        {
            FatalErrorInFunction << "Conductivity field " << k.name()
                << " has dimensions " << k.dimensions() << "; require "
                << conductivityDimensions << ", patch=" << patch().name()
                << abort(FatalError);
        }
        conductivity = k.boundaryField()[patch().index()];
    }
    else
    {
        // Compatibility with hydroThermo-based solvers: no implicit field fallback.
        const IOdictionary& thermo = db().lookupObject<IOdictionary>("thermophysicalProperties");
        const dimensionedScalar k(thermo.subDict("mixture").subDict("porousMedia").lookup(krName_));
        if (k.dimensions() != conductivityDimensions)
        {
            FatalErrorInFunction << "Legacy conductivity " << krName_
                << " has dimensions " << k.dimensions() << "; require "
                << conductivityDimensions << ", patch=" << patch().name()
                << abort(FatalError);
        }
        conductivity = k.value();
    }
    forAll(conductivity, faceI)
    {
        if (!std::isfinite(conductivity[faceI]) || conductivity[faceI] <= 0)
        {
            FatalErrorInFunction << "Invalid boundary conductivity " << conductivity[faceI]
                << " W/(m K); require finite and > 0; field=" << conductivityFieldName_
                << ", patch=" << patch().name() << ", local face=" << faceI
                << ", centre=" << patch().patch().faceCentres()[faceI]
                << ", time=" << db().time().timeName() << ", rank=" << Pstream::myProcNo()
                << abort(FatalError);
        }
    }

    // All shapes describe inward flux density [W/m2], sampled at face centres.
    scalarField heatInput(q_);
    if (shape_ == "gaussian2d" || shape_ == "gaussian3d")
    {
        if (!std::isfinite(c_) || c_ <= 0)
        {
            FatalErrorInFunction << "Gaussian heat-flux width c must be finite and > 0"
                << abort(FatalError);
        }
        const scalarField x(patch().Cf().component(0));
        scalarField radiusSqr(sqr(x - x0_));
        if (shape_ == "gaussian3d")
        {
            radiusSqr += sqr(patch().Cf().component(2) - z0_);
        }
        heatInput = qmin_ + (qmax_ - qmin_)*exp(-radiusSqr/(2*sqr(c_)));
    }
    else if (shape_ == "linear2d")
    {
        if (!std::isfinite(x2_ - x1_) || x2_ == x1_)
        {
            FatalErrorInFunction << "Linear heat-flux endpoints require finite x2-x1 != 0"
                << abort(FatalError);
        }
        heatInput = (patch().Cf().component(0) - x1_)*(q2_ - q1_)/(x2_ - x1_) + q1_;
    }
    else if (shape_ != "fixed")
    {
        FatalErrorInFunction << "Unknown heat-flux shape " << shape_
            << "; expected fixed, gaussian2d, gaussian3d or linear2d" << abort(FatalError);
    }
    forAll(heatInput, faceI)
    {
        if (!std::isfinite(heatInput[faceI]))
        {
            FatalErrorInFunction << "Nonfinite prescribed heat flux; patch=" << patch().name()
                << ", local face=" << faceI << abort(FatalError);
        }
    }
    gradient() = heatInput/conductivity;
    fixedGradientFvPatchScalarField::updateCoeffs();
}

void Foam::HydrothermalHeatFlux::write(Ostream& os) const
{
    fixedGradientFvPatchScalarField::write(os);
    writeEntry(os, "q", q_);
    writeEntry(os, "value", *this);
    writeEntryIfDifferent<word>(os, "kr","kr",krName_);
    writeEntryIfDifferent<word>(os, "conductivityField", word::null, conductivityFieldName_);
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
    else if (shape_ == "linear2d")
    {
        writeEntry(os, "x1", x1_);
        writeEntry(os, "x2", x2_);
        writeEntry(os, "q1", q1_);
        writeEntry(os, "q2", q2_);
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