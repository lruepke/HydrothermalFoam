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

Class
    Foam::submarinePressureFvPatchScalarField

Description
    This boundary condition provides hydrostatic pressure condition on the top or seafloor,
    calculated as:

        \f[
            p=\rho \cdot g \cdot h
        \f]

    where
    \vartable
        rho     | Density of seawater, default value is 1013 [\f[kg/m^3\f]]
        g       | Acceleration due to gravity [\f[ m/s^2\f]]
        h       | Depth below sea level [m]
    \endtable

Usage
    \table
        Property     | Description             | Required    | Default value
        rhoValue     | Density value           | no          | 1013
    \endtable

    Example of the boundary condition specification:
    \verbatim
    <patchName>
    {
        type            submarinePressure;
        rhoValue        uniform 1013;
    }
    \endverbatim

See also
    Foam::fixedValueFvPatchScalarField
    Foam::prghTotalPressureFvPatchScalarField

SourceFiles
    submarinePressureFvPatchScalarField.C

\*---------------------------------------------------------------------------*/

#ifndef submarinePressureFvPatchScalarField_H
#define submarinePressureFvPatchScalarField_H

#include "fixedValueFvPatchFields.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

/*---------------------------------------------------------------------------*\
         Class submarinePressureFvPatchScalarField Declaration
\*---------------------------------------------------------------------------*/

class submarinePressureFvPatchScalarField
:
    public fixedValueFvPatchScalarField
{
    // Hydrostatic pressure at seafloor is calculated by equation: rhoValue*g*h
    scalar rhoValue_;
    scalar p_Atmospheric;  //atmospheric pressure

public:

    //- Runtime type information
    TypeName("submarinePressure");


    // Constructors

        //- Construct from patch and internal field
        submarinePressureFvPatchScalarField
        (
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&
        );

        //- Construct from patch, internal field and dictionary
        submarinePressureFvPatchScalarField
        (
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&,
            const dictionary&
        );

        //- Construct by mapping given
        //  submarinePressureFvPatchScalarField onto a new patch
        submarinePressureFvPatchScalarField
        (
            const submarinePressureFvPatchScalarField&,
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&,
            const fvPatchFieldMapper&
        );

        //- Copy constructor
        submarinePressureFvPatchScalarField
        (
            const submarinePressureFvPatchScalarField&
        );

        //- Construct and return a clone
        virtual tmp<fvPatchScalarField> clone() const
        {
            return tmp<fvPatchScalarField >
            (
                new submarinePressureFvPatchScalarField(*this)
            );
        }

        //- Copy constructor setting internal field reference
        submarinePressureFvPatchScalarField
        (
            const submarinePressureFvPatchScalarField&,
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
                new submarinePressureFvPatchScalarField(*this, iF)
            );
        }


    // Member Functions

        // Evaluation functions

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
