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
    Foam::HydrothermalHeatFlux

Description
    Fixed heat flux boundary condition. Positive q [W/m^2] is heat entering
    the domain: outward-normal temperature gradient = q/conductivity.
    conductivityField selects a registered bulk-conductivity volume field;
    if absent, retain thermophysicalProperties/mixture/porousMedia lookup.
    \heading Patch usage
    \table
        Property     | Description             | Required    | Default value
        q            | heat flux value         | yes          |
        kr           | conductivity entry in legacy porousMedia dictionary | no | kr
        conductivityField | registered conductivity field name | no | none
        shape           | special shape | no | fixed
    \endtable
    Example of the boundary condition specification:
    \verbatim
    myPatch
    {
        type            hydrothermalHeatFlux;
        q               uniform 5; //W/m^2
        kr              kr;
        value           uniform 0; // place holder
        shape             gaussian2d; //gaussian2d, gaussian3d
        x0                0; //for gaussian shape: peak position
        z0                0; //for gaussian3d shape: peak position
        qmax              5; //for gaussian shape
        qmin              0.05; //for gaussian shape
        c                 500; //for gaussian shape: heaf width
    }
    \endverbatim

SourceFiles
    HydrothermalHeatFlux.C

\*---------------------------------------------------------------------------*/


#ifndef HydrothermalHeatFlux_H
#define HydrothermalHeatFlux_H

#include "fvPatchFields.H"
#include "fixedGradientFvPatchFields.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

/*---------------------------------------------------------------------------*\
    Class HydrothermalHeatFluxFvPatch Declaration
    \*---------------------------------------------------------------------------*/

class HydrothermalHeatFlux
:
    public fixedGradientFvPatchScalarField
{
    // Private data

    word krName_;   // Legacy dictionary entry, default "kr"
    word conductivityFieldName_; // Empty retains legacy dictionary mode
    scalarField q_; //heat flux [W/m^2]
    // --------- Special heat flux boundary condition --------------
    word shape_; //Gaussian
    // 1. Gaussian shape
    /**
     * @brief Gaussian shape heat flux
     * 
     * \f[ q=q_{min} + (q_{max} - q_{min})e^{-\frac{(x-x_0)^2 + (z-z_0)^2}{2c^2}} \f]
     * 
     */
    scalar qmax_,qmin_,x0_,z0_,c_;
    scalar x1_, x2_, q1_, q2_; //variables for linear heat flux boundary
public:

    //- Runtime type information
    TypeName("hydrothermalHeatFlux");


    // Constructors

    //- Construct from patch and internal field
    HydrothermalHeatFlux
    (
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&
    );

    //- Construct from patch, internal field and dictionary
    HydrothermalHeatFlux
    (
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&,
        const dictionary&
    );

    //- Construct by mapping given
    //  HydrothermalHeatFlux onto a new patch
    HydrothermalHeatFlux
    (
        const HydrothermalHeatFlux&,
        const fvPatch&,
        const DimensionedField<scalar, volMesh>&,
        const fvPatchFieldMapper&
    );

    //- Disallow copy without setting the internal field reference (OF10 contract)
    HydrothermalHeatFlux
    (
        const HydrothermalHeatFlux&
    ) = delete;

    //- Construct as copy setting internal field reference
    HydrothermalHeatFlux
    (
        const HydrothermalHeatFlux&,
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
                    new HydrothermalHeatFlux(*this, iF)
                );
        }

    // Member functions

    //- Map nonuniform prescribed flux along with the underlying patch values
    virtual void autoMap(const fvPatchFieldMapper&);
    virtual void rmap(const fvPatchScalarField&, const labelList&);
    virtual void reset(const fvPatchScalarField&);

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
