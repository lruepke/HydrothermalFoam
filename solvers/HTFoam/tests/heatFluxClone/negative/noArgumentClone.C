#include "HydrothermalHeatFluxFvPatchScalarField.H"
void unsupported(const Foam::HydrothermalHeatFlux& source)
{
    auto copy=source.clone();
}
int main() { return 0; }
