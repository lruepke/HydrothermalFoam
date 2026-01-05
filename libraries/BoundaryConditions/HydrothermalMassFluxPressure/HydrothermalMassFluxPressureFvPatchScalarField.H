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

Class
    Foam::HydrothermalMassFluxPressure

Description
    Fixed mass flux boundary condition to specify pressure gradient. Input mass flux: q [kg/s].
    \heading Patch usage
    \table
        Property     | Description             | Required    | Default value
        q            | heat flux value         | yes          |
    \endtable
    Example of the boundary condition specification:
    \verbatim
    myPatch
    {
        type            HydrothermalMassFluxPressure;
        q               uniform -0.0115; //kg/s, netagive means flow into domain; positive means flow out domain
    }
    \endverbatim

SourceFiles
    HydrothermalMassFluxPressure.C

\*---------------------------------------------------------------------------*/

#ifndef HydrothermalMassFluxPressure_H
#define HydrothermalMassFluxPressure_H

#include "fixedGradientFvPatchFields.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

/*---------------------------------------------------------------------------*\
    Class HydrothermalMassFluxPressureFvPatch Declaration
    \*---------------------------------------------------------------------------*/

class HydrothermalMassFluxPressure
:
    public fixedGradientFvPatchScalarField
{
    // Private data

    //- Name of the velocity and permeability fields used to calculate the wall BC in darcy's law
    word rhorAUfName_;
    // word rhophiName_;
    word phigName_;	
    scalarField q_; //mass flux [kg/m^2/s]

public:

    //- Runtime type information
    TypeName("hydrothermalMassFluxPressure");

    // Constructors

    //- Construct from patch and internal field
    HydrothermalMassFluxPressure
    (
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&
    );

    //- Construct from patch, internal field and dictionary
    HydrothermalMassFluxPressure
    (
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&,
        const dictionary&
    );

    //- Construct by mapping given
    //  HydrothermalMassFluxPressure onto a new patch
    HydrothermalMassFluxPressure
    (
        const HydrothermalMassFluxPressure&,
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&,
        const fvPatchFieldMapper&
    );

    //- Construct as copy
    HydrothermalMassFluxPressure
    (
        const HydrothermalMassFluxPressure&
    );

    //- Construct and return a clone
    virtual tmp<fvPatchScalarField> clone() const
        {
            return tmp<fvPatchScalarField>
                (
                    new HydrothermalMassFluxPressure(*this)
                );
        }

    //- Construct as copy setting internal field reference
    HydrothermalMassFluxPressure
    (
        const HydrothermalMassFluxPressure&,
        const DimensionedField<scalar, volMesh>&
    );

    //- Construct and return a clone setting internal field reference
    virtual tmp<fvPatchScalarField> clone
    (
        const DimensionedField<scalar, volMesh>& iF
    ) const
        {
            return tmp<fvPatchScalarField>
                (
                    new HydrothermalMassFluxPressure(*this, iF)
                );
        }

    // Member functions

    //- Update the coefficients associated with the patch field
    virtual void updateCoeffs();

    //- Write
    virtual void write(Ostream&) const;
};

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //