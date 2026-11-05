Info<< "Release xThermo object\n" << endl;

if(pxThermo)
{
    delete pxThermo;
    pxThermo = nullptr;
}