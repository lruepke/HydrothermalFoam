{
    // No constitutive law yet: kr already denotes effective bulk conductivity.
    // Correct the input's own physical conditions and exchange coupled values.
    // Reference conductivity BCs must not depend on T or kr_eff (startup ordering).
    // Validate local cells before communication so rank-local bad input fails fast.
    // Boundary values are checked after their boundary conditions are evaluated.
    forAll(kr, cellI)
    {
        if (!std::isfinite(kr[cellI]) || kr[cellI] <= 0)
        {
            checkConductivity(kr);
        }
    }
    kr.correctBoundaryConditions();
    checkConductivity(kr);

    kr_eff.primitiveFieldRef() = kr.primitiveField();
    forAll(kr_eff.boundaryField(), patchI)
    {
        if (!mesh.boundary()[patchI].coupled())
        {
            // Force assignment of calculated physical values, including explicit
            // reference patch values that differ from adjacent cell conductivity.
            kr_eff.boundaryFieldRef()[patchI] == kr.boundaryField()[patchI];
        }
    }
    kr_eff.correctBoundaryConditions();
    checkConductivity(kr_eff);
}
