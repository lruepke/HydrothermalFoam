#include "thermo.h"
#include "H2ONaCl.h"
#include "fvCFD.H"
#include "evaluateFluidState.H"
#include <limits>
#include <stdexcept>

// Inject a failure after a real, valid water evaluation. This tests the guard
// contract independently of which empirical EOS regions reproduce each fault.
class FaultModel : public xThermal::PROST::cIAPS84
{
    Foam::word mode_;
public:
    explicit FaultModel(const Foam::word& mode) : mode_(mode) {}
    void UpdateState_TPX(xThermal::ThermodynamicProperties& state,
        const double& T, const double& p, const double& X) override
    {
        if (mode_ == "status") throw xThermal::OutOfRangeError("injected EOS range failure");
        if (mode_ == "exception") throw std::runtime_error("injected non-xThermo exception");
        xThermal::PROST::cIAPS84::UpdateState_TPX(state, T, p, X);
        if (mode_ == "nanMu") state.Mu = std::numeric_limits<double>::quiet_NaN();
        if (mode_ == "zeroCp") state.Cp = 0;
        if (mode_ == "negativeBeta") state.IsothermalCompressibility = -1;
        if (mode_ == "nanAlpha") state.IsobaricExpansivity = std::numeric_limits<double>::quiet_NaN();
        if (mode_ == "negativeAlpha") state.IsobaricExpansivity = -1e-5;
        if (mode_ == "zeroAlpha") state.IsobaricExpansivity = 0;
        if (mode_ == "critical") state.phase = xThermal::Critical;
        if (mode_ == "solid") state.phase = xThermal::SinglePhase_S;
        if (mode_ == "unknown") state.phase = xThermal::Unknown;
        if (mode_ == "superV") state.phase = xThermal::Supercritical_vapor;
        if (mode_ == "superL") state.phase = xThermal::Supercritical_liquid;
    }
};

int main(int argc, char* argv[])
{
    Foam::argList::addOption("mode", "word", "real or injected evaluation scenario");
    Foam::argList::addOption("temperature", "scalar", "K");
    Foam::argList::addOption("pressure", "scalar", "Pa");
    Foam::argList::addOption("salinity", "scalar", "kg/kg");
    Foam::argList::addOption("backend", "word", "IAPS84 or IAPWS95 for brine");
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    const Foam::word mode = args.optionLookupOrDefault<Foam::word>("mode", "brine");
    const Foam::word backend = args.optionLookupOrDefault<Foam::word>("backend", "IAPS84");
    const double T = args.optionLookupOrDefault<double>("temperature", 573.15);
    const double p = args.optionLookupOrDefault<double>("pressure", 3e7);
    const double X = args.optionLookupOrDefault<double>("salinity", 0.1);
    xThermal::cxThermal* model = nullptr;
    if (mode == "brine") model = new xThermal::H2ONaCl::cH2ONaCl(backend);
    else if (mode == "water") model = new xThermal::PROST::cIAPS84;
    else model = new FaultModel(mode);
    const Foam::HTFoamThermo::Location location = {mesh, 0, -1, -1, "property probe"};
    const auto state = Foam::HTFoamThermo::evaluate
        (*model, mode == "brine" ? "H2O-NaCl" : "H2O", backend,
         mode == "nanInput" ? std::numeric_limits<double>::quiet_NaN() : T, p, X, location);
    Foam::OStringStream result;
    result.precision(17);
    result << "PROBE phase=" << int(state.phase) << " rho=" << state.Rho
        << " mu=" << state.Mu << " Cp=" << state.Cp
        << " beta=" << state.IsothermalCompressibility
        << " alpha=" << state.IsobaricExpansivity;
    Foam::Info << result.str().c_str() << Foam::endl;
    delete model;
    return 0;
}
