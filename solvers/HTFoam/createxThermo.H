Info<< "Create xThermal object for fluid properties calculation\n" << endl;

Info<< "Reading xThermal (EOS of fluid) library settings\n" << endl;
IOdictionary xThermoPropertiesDict
(
    IOobject
    (
        "xThermoProperties",
        runTime.constant(),
        mesh,
        IOobject::MUST_READ,
        IOobject::NO_WRITE
    )
);

word xThermoFluidName(xThermoPropertiesDict.lookup("fluid"));
word xThermoBackend(xThermoPropertiesDict.lookup("backend"));
const word name_constX = "constX";
scalar constX = 0;
xThermal::cxThermal* pxThermo = nullptr;
xThermal::ThermodynamicProperties props;
// xThermo::PROST::cIAPS84 IAPS84;
// xThermo::IAPWS95::cIAPWS95 IAPWS95;
// xThermo::COOLPROP::cIAPWS95_CoolProp IAPWS95_CoolProp;
if(xThermoFluidName=="H2O" || xThermoFluidName=="water" || xThermoFluidName=="Water")
{
    if(xThermoBackend=="IAPS84")
    {
        pxThermo = new xThermal::PROST::cIAPS84;
    }else if(xThermoBackend=="IAPWS95")
    {
        pxThermo = new xThermal::IAPWS95::cIAPWS95;
    }else if(xThermoBackend=="IAPWS95_CoolProp")
    {
        //pxThermo = new xThermal::COOLPROP::cIAPWS95_CoolProp;
        FatalErrorInFunction<<COLOR_RED<<"The supported xThermal backend of pure water can be one of `IAPS84`, `IAPWS95` or `IAPWS95_CoolProp`. \nThe backend name in the constant/xThermoProperties dict file can not be identified: "<<COLOR_BLUE<<xThermoBackend
        <<COLOR_DEFAULT<<abort(FatalError);
    }
    else
    {
        FatalErrorInFunction<<COLOR_RED<<"The supported xThermal backend of pure water can be one of `IAPS84`, `IAPWS95` or `IAPWS95_CoolProp`. \nThe backend name in the constant/xThermoProperties dict file can not be identified: "<<COLOR_BLUE<<xThermoBackend
        <<COLOR_DEFAULT<<abort(FatalError);
    }
}else
{
    if(xThermal::cxThermal::validateFluid (xThermoFluidName) == xThermal::INDEX_FLUID::FLUID_H2O_NaCl)
    {
        pxThermo = new xThermal::H2ONaCl::cH2ONaCl(xThermoBackend);
        Info<<COLOR_INFO<<"Using "<<xThermoBackend<<"-based "<<xThermoFluidName<<" as the fluid in "<<args.executable()<<COLOR_DEFAULT<<endl;
        // lookup the constant X value if present, otherwise use the default value 0
        if(xThermoPropertiesDict.found(xThermoFluidName))
        {
            const dictionary& dict_H2ONaCl(xThermoPropertiesDict.subDict(xThermoFluidName));
            if(dict_H2ONaCl.found(name_constX))
            {
                constX = readScalar(dict_H2ONaCl.lookup(name_constX));
                Info<<COLOR_INFO<<"The constant salinity found: constX = "<<constX<<" [mass fraction kg/kg]"<<endl;
            }else
            {
                Info<<COLOR_WARNING<<"The subdict of "<<xThermoFluidName<<" is found, but there is no subdict for constant salinity `constX` entry "<<", default values will be used: "<<COLOR_DEFAULT<<endl;
                Info<<COLOR_INFO<<"Default salinity constX = "<<constX<<COLOR_DEFAULT<<endl;
            }
        }else
        {
            Info<<COLOR_WARNING<<"There is no subdict for further configuration of "<<COLOR_BLUE<<xThermoFluidName<<", default values will be used: "<<COLOR_DEFAULT<<endl;
            Info<<COLOR_INFO<<"Default salinity constX = "<<constX<<COLOR_DEFAULT<<endl;
        }
        Info<<COLOR_INFO<<"constX = "<<constX<<COLOR_DEFAULT<<endl;
    }else
    {
        FatalErrorInFunction<<COLOR_RED<<"The supported xThermal fluid for `"<<args.executable()<<"` is only pure water, the `fluid` name in constant/xThermoProperties dict file can be one of `H2O`, `Water` or `water`. \nThe input fluid name in the dict file can not be identified: "<<COLOR_BLUE<<xThermoFluidName
        <<COLOR_DEFAULT<<abort(FatalError);
    }
}
