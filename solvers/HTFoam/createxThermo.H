Info<< "Reading xThermo fluid/backend settings\n" << endl;
IOdictionary xThermoPropertiesDict
(
    IOobject
    (
        "xThermoProperties", runTime.constant(), mesh,
        IOobject::MUST_READ, IOobject::NO_WRITE
    )
);

word xThermoFluidName(xThermoPropertiesDict.lookup("fluid"));
word xThermoBackend(xThermoPropertiesDict.lookup("backend"));
scalar constX = 0;
xThermal::cxThermal* pxThermo = nullptr;
const bool pureWater =
    xThermoFluidName == "H2O" || xThermoFluidName == "water"
 || xThermoFluidName == "Water";

// Composition is fixed for this solver. Preserve the legacy missing-entry default.
if (!pureWater)
{
    if (xThermoPropertiesDict.found(xThermoFluidName))
    {
        const dictionary& config = xThermoPropertiesDict.subDict(xThermoFluidName);
        if (config.found("constX"))
        {
            constX = readScalar(config.lookup("constX"));
        }
        else
        {
            WarningInFunction << "No constX for " << xThermoFluidName
                << "; using the existing default X=0 kg/kg" << endl;
        }
    }
    else
    {
        WarningInFunction << "No composition subdictionary for " << xThermoFluidName
            << "; using the existing default X=0 kg/kg" << endl;
    }
}

auto configurationFailure = [&](const std::string& reason)
{
    OStringStream context;
    context.precision(17);
    context << "xThermo configuration failure: " << reason.c_str() << nl
        << "fluid=" << xThermoFluidName << ", backend=" << xThermoBackend
        << ", X=" << constX << " kg/kg, time=" << runTime.timeName()
        << ", rank=" << Pstream::myProcNo() << nl
        << "dictionary=constant/xThermoProperties; p/T and mesh location are not yet read";
    FatalErrorInFunction << context.str().c_str() << nl << abort(FatalError);
};
if (!std::isfinite(constX) || constX < 0 || constX > 1)
{
    configurationFailure("require finite 0 <= constX <= 1 kg/kg");
}

try
{
    if (pureWater)
    {
        if (xThermoBackend == "IAPS84")
        {
            pxThermo = new xThermal::PROST::cIAPS84;
        }
        else if (xThermoBackend == "IAPWS95")
        {
            pxThermo = new xThermal::IAPWS95::cIAPWS95;
        }
        else
        {
            configurationFailure("supported pure-water backends: IAPS84, IAPWS95");
        }
    }
    else if
    (
        xThermal::cxThermal::validateFluid(xThermoFluidName)
     == xThermal::INDEX_FLUID::FLUID_H2O_NaCl
    )
    {
        pxThermo = new xThermal::H2ONaCl::cH2ONaCl(xThermoBackend);
    }
    else
    {
        configurationFailure("supported fluids: H2O (water/Water), or H2O-NaCl");
    }
}
catch (const std::exception& error)
{
    configurationFailure(std::string("model construction exception: ") + error.what());
}
Info<< "Using " << xThermoBackend << " / " << xThermoFluidName
    << ", constX=" << constX << " kg/kg" << endl;
