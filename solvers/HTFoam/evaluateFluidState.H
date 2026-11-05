#ifndef HTFoam_evaluateFluidState_H
#define HTFoam_evaluateFluidState_H

#include "emptyFvPatch.H"
#include "processorFvPatch.H"
#include <cmath>
#include <exception>

namespace Foam
{
namespace HTFoamThermo
{

struct Location
{
    const fvMesh& mesh;
    label cell;
    label patch;
    label face;
    const char* stage;
};

inline void fail
(
    const word& fluid,
    const word& backend,
    const scalar T,
    const scalar p,
    const scalar X,
    const Location& location,
    const std::string& reason,
    const xThermal::PhaseRegion phase = xThermal::Unknown
)
{
    OStringStream context;
    context.precision(17);
    context << "HTFoam property failure: " << reason.c_str() << nl
        << "fluid=" << fluid << ", backend=" << backend
        << ", phase=" << label(phase);
    const auto name = xThermal::map_phase2name.find(phase);
    if (name != xThermal::map_phase2name.end())
    {
        context << " (" << name->second.c_str() << ')';
    }
    context << nl << "T=" << T << " K, p=" << p << " Pa, X=" << X
        << " kg/kg" << nl
        << "time=" << location.mesh.time().timeName()
        << ", rank=" << Pstream::myProcNo()
        << ", stage=" << location.stage;
    // Raw mesh geometry needs no collective communication on an error path.
    if (location.cell >= 0)
    {
        context << ", local cell=" << location.cell
            << ", centre=" << location.mesh.cellCentres()[location.cell];
    }
    if (location.patch >= 0)
    {
        const fvPatch& patch = location.mesh.boundary()[location.patch];
        context << ", patch=" << patch.name() << ", local face=" << location.face
            << ", centre="
            << location.mesh.faceCentres()[patch.start() + location.face];
    }
    FatalErrorInFunction << context.str().c_str() << nl << abort(FatalError);
}

inline bool singleFluidPhase(const xThermal::PhaseRegion phase)
{
    switch (phase)
    {
        case xThermal::SinglePhase_L:
        case xThermal::SinglePhase_V:
        case xThermal::Supercritical:
        case xThermal::Supercritical_vapor:
        case xThermal::Supercritical_liquid:
            return true;
        default:
            return false;
    }
}

inline void checkProperties
(
    const xThermal::ThermodynamicProperties& state,
    const word& fluid,
    const word& backend,
    const scalar T,
    const scalar p,
    const scalar X,
    const Location& location
)
{
    const double values[] =
    {
        state.Rho, state.Mu, state.Cp,
        state.IsothermalCompressibility, state.IsobaricExpansivity
    };
    const char* names[] = {"rho", "mu", "Cp", "betaT", "alphaP"};
    for (unsigned i = 0; i < 5; ++i)
    {
        if (!std::isfinite(values[i]) || (i < 4 && values[i] <= 0))
        {
            OStringStream reason;
            reason.precision(17);
            reason << "unusable property " << names[i] << '=' << values[i]
                << "; required " << (i < 4 ? "finite and > 0" : "finite");
            fail(fluid, backend, T, p, X, location, reason.str(), state.phase);
        }
    }
}

inline xThermal::ThermodynamicProperties evaluate
(
    xThermal::cxThermal& thermo,
    const word& fluid,
    const word& backend,
    const scalar T,
    const scalar p,
    const scalar X,
    const Location& location
)
{
    if
    (
        !std::isfinite(T) || T <= 0 || !std::isfinite(p) || p <= 0
     || !std::isfinite(X) || X < 0 || X > 1
    )
    {
        fail(fluid, backend, T, p, X, location,
             "invalid input: require finite T > 0 K, p > 0 Pa, and 0 <= X <= 1 kg/kg");
    }

    xThermal::ThermodynamicProperties state;
    std::string message;
    xThermal::EvaluationStatus status = xThermal::EvaluationStatus::Failed;
    try
    {
        // Retain the previous model-envelope guard; the library can impose
        // stricter state/composition-dependent limits within this envelope.
        if (T < thermo.Tmin() || T > thermo.Tmax()
         || p < thermo.pmin() || p > thermo.pmax())
        {
            OStringStream reason;
            reason.precision(17);
            reason << "outside advertised model bounds: T=[" << thermo.Tmin()
                << ", " << thermo.Tmax() << "] K, p=[" << thermo.pmin()
                << ", " << thermo.pmax() << "] Pa";
            fail(fluid, backend, T, p, X, location, reason.str());
        }
        status = thermo.tryUpdateState_TPX(state, T, p, X, &message);
    }
    catch (const std::exception& error)
    {
        fail(fluid, backend, T, p, X, location,
             std::string("exception during EOS evaluation: ") + error.what());
    }
    if (status != xThermal::EvaluationStatus::Ok)
    {
        fail(fluid, backend, T, p, X, location,
             std::string("xThermo status=")
             + xThermal::evaluation_status_name(status) + ": " + message);
    }
    if (!singleFluidPhase(state.phase))
    {
        fail(fluid, backend, T, p, X, location,
             "unsupported phase: require single-phase fluid; exact Critical is excluded",
             state.phase);
    }
    checkProperties(state, fluid, backend, T, p, X, location);
    return state;
}

} // namespace HTFoamThermo
} // namespace Foam

#endif
