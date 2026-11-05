/**
 * @file triToFaom.C
 * @author Zhikui Guo (zguo@geomar.de)
 * @brief Convert Triangle mesh to OpenFOAM's polyMesh
 * @version 0.1
 * @date 2022-03-28
 * 
 * @copyright Copyright (c) 2022
 * 
 */

#include "fvCFD.H"

#include "cellModeller.H"
#include "argList.H"
#include "repatchPolyTopoChanger.H"
#include "cellSet.H"
#include "faceSet.H"
const word patch_name_back("back");
const word patch_name_front("front");
const word extName_map_boundaryMarkers2PatchNames("bm2name");
const word extName_map_eleAttributes2cellZoneNames("attrib2name");

void read_node(const fileName& fname_Triangle, const scalar& zmin, const scalar& zmax, pointField& points, Map<label>& mshToFoam);
void read_ele(const fileName& fname_Triangle, const pointField& points, const Map<label>& mshToFoam,const bool keepOrientation,
        cellShapeList& cells,labelList& patchToPhys,List<DynamicList<face>>& patchFaces,Map<word>& physicalNames,
        labelList& zoneToPhys,List<DynamicList<label>>& zoneCells
);
void  read_edge(const fileName& fname_Triangle, const pointField& points, const Map<label>& mshToFoam,
                labelList& patchToPhys,List<DynamicList<face>>& patchFaces,Map<word>& physicalNames);
void renumber(const Map<label>& mshToFoam,labelList& labels);
bool correctOrientation(const pointField& points, const cellShape& shape);
label findFace(const primitivePatch& pp, const labelList& meshF);
label findInternalFace(const primitiveMesh& mesh, const labelList& meshF);
void read_map_TriangleIndex2PhysicalName(const fileName& fname_map, Map<word>& index2name);
void storeCellInZone(const label regPhys, const label celli,Map<label>& physToZone,
                     labelList& zoneToPhys,List<DynamicList<label>>& zoneCells,Map<word>& physicalNames,const Map<word> eleAttributes2cellZoneNames,label baseNumber);

int main(int argc, char *argv[])
{
    argList::noParallel();
    argList::validArgs.append(".node file of Triangle mesh result");
    argList::addBoolOption
    (
        "keepOrientation",
        "retain raw orientation for prisms(triangle)"
    );
    Foam::argList::addOption
    (
        "zmin",
        "float number",
        "specify zmin value for the extruded mesh. Default is 0."
    );
    Foam::argList::addOption
    (
        "zmax",
        "float number",
        "specify zmax value for the extruded mesh. Default is 1"
    );
    // set up the case
    #include "setRootCase.H"

    // create the run time object
    Info<< "Create time\n" << endl;
    Time runTime
    (
        Time::controlDictName,
        args.rootPath(),
        args.caseName()
    );
    // disable post-processing etc.
    runTime.functionObjects().off();
    Foam::word regionName = Foam::polyMesh::defaultRegion;
    const bool keepOrientation = args.optionFound("keepOrientation");
    // ================================================================
    // 1. zmin, zmax
    Foam::scalar zmin = 0, zmax =1;
    args.optionReadIfPresent("zmin", zmin);
    args.optionReadIfPresent("zmax", zmax);
    Foam::Info<< "The extension of the extruded polyMesh in z direction is [ " << zmin<<", "<<zmax<<"]" << endl;
    const fileName triFile = args[1];
    pointField points;
    Map<label> mshToFoam;
    cellShapeList cells;
    labelList patchToPhys;
    List<DynamicList<face>> patchFaces(0);
    // Map from cellZone to gmsh physical region
    labelList zoneToPhys;
    // Storage for cell zones.
    List<DynamicList<label>> zoneCells(0);
    Map<word> physicalNames;
    // 2.1 read points (node)
    read_node(triFile, zmin, zmax,points, mshToFoam);
    // 2.2 read_edge (boundaryies)
    read_edge(triFile, points, mshToFoam, patchToPhys, patchFaces,physicalNames);
    // 2.2 read element (triangles)
    read_ele(triFile, points, mshToFoam, keepOrientation, cells, patchToPhys, patchFaces,physicalNames, zoneToPhys, zoneCells);
    // ---

    faceListList boundaryFaces(patchFaces.size());
    wordList boundaryPatchNames(boundaryFaces.size());
    wordList boundaryPatchTypes(boundaryFaces.size(), polyPatch::typeName);
    forAll(boundaryPatchNames, patchi)
    {
        label physReg = patchToPhys[patchi];

        Map<word>::const_iterator iter = physicalNames.find(physReg);

        if (iter != physicalNames.end())
        {
            boundaryPatchNames[patchi] = iter();
        }
        else
        {
            boundaryPatchNames[patchi] = word("patch") + name(patchi);
        }
        if(boundaryPatchNames[patchi]==patch_name_back)boundaryPatchTypes[patchi] = emptyPolyPatch::typeName;
        if(boundaryPatchNames[patchi]==patch_name_front)boundaryPatchTypes[patchi] = emptyPolyPatch::typeName;

        Info<< "Patch " << patchi << " gets name " << boundaryPatchNames[patchi] << endl;
    }
    Info<< endl;

    label nValidCellZones = 0;

    forAll(zoneCells, zoneI)
    {
        if (zoneCells[zoneI].size())
        {
            nValidCellZones++;
        }
    }

    word defaultFacesName = "defaultFaces";
    word defaultFacesType = polyPatch::typeName;
    wordList boundaryPatchPhysicalTypes
    (
        boundaryFaces.size(),
        polyPatch::typeName
    );
    polyMesh mesh
    (
        IOobject
        (
            regionName,
            runTime.constant(),
            runTime
        ),
        move(points),
        cells,
        boundaryFaces,
        boundaryPatchNames,
        boundaryPatchTypes,
        defaultFacesName,
        defaultFacesType,
        boundaryPatchPhysicalTypes
    );

    repatchPolyTopoChanger repatcher(mesh);
    // Get the patch for all the outside faces (= default patch added as last)
    const polyPatch& pp = mesh.boundaryMesh().last();
    // Storage for faceZones.
    List<DynamicList<label>> zoneFaces(patchFaces.size());

    // Go through all the patchFaces and find corresponding face in pp.
    forAll(patchFaces, patchi)
    {
        const DynamicList<face>& pFaces = patchFaces[patchi];
        forAll(pFaces, i)
        {
            const face& f = pFaces[i];
            // Find face in pp using all vertices of f.
            label patchFacei = findFace(pp, f);

            if (patchFacei != -1)
            {
                label meshFacei = pp.start() + patchFacei;

                repatcher.changePatchID(meshFacei, patchi);
            }
            else
            {
                // Maybe internal face? If so add to faceZone with same index
                // - might be useful.
                label meshFacei = findInternalFace(mesh, f);

                if (meshFacei != -1)
                {
                    zoneFaces[patchi].append(meshFacei);
                }
                else
                {
                    WarningInFunction
                            << "Could not match gmsh face " << f
                            << " to any of the interior or exterior faces"
                            << " that share the same 0th point" << endl;
                }
            }
        }
    }
    Info<< nl;

    // Face zones
    label nValidFaceZones = 0;

    // Info<< "FaceZones:" << nl << "Zone\tSize" << endl;

    forAll(zoneFaces, zoneI)
    {
        zoneFaces[zoneI].shrink();

        const labelList& zFaces = zoneFaces[zoneI];

        if (zFaces.size())
        {
            nValidFaceZones++;

            Info<< "    " << zoneI << '\t' << zFaces.size() << endl;
        }
    }
    Info<< endl;

    // Get polyMesh to write to constant

    runTime.setTime(instant(runTime.constant()), 0);

    repatcher.repatch();

    List<cellZone*> cz;
    List<faceZone*> fz;
    if (nValidCellZones > 0)
    {
        cz.setSize(nValidCellZones);

        nValidCellZones = 0;

        forAll(zoneCells, zoneI)
        {
            if (zoneCells[zoneI].size())
            {
                label physReg = zoneToPhys[zoneI];

                Map<word>::const_iterator iter = physicalNames.find(physReg);

                word zoneName = "cellZone_" + name(zoneI);
                if (iter != physicalNames.end())
                {
                    zoneName = iter();
                }

                Info<< "Writing zone " << zoneI << " to cellZone "
                    << zoneName << " and cellSet"
                    << endl;

                cellSet cset(mesh, zoneName, zoneCells[zoneI]);
                cset.write();

                cz[nValidCellZones] = new cellZone
                        (
                                zoneName,
                                zoneCells[zoneI],
                                nValidCellZones,
                                mesh.cellZones()
                        );
                nValidCellZones++;
            }
        }
    }

    if (nValidFaceZones > 0)
    {
        fz.setSize(nValidFaceZones);

        nValidFaceZones = 0;

        forAll(zoneFaces, zoneI)
        {
            if (zoneFaces[zoneI].size())
            {
                label physReg = patchToPhys[zoneI];

                Map<word>::const_iterator iter = physicalNames.find(physReg);

                word zoneName = "faceZone_" + name(zoneI);
                if (iter != physicalNames.end())
                {
                    zoneName = iter();
                }

                Info<< "Writing zone " << zoneI << " to faceZone "
                    << zoneName << " and faceSet"
                    << endl;

                faceSet fset(mesh, zoneName, zoneFaces[zoneI]);
                fset.write();

                fz[nValidFaceZones] = new faceZone
                        (
                                zoneName,
                                zoneFaces[zoneI],
                                boolList(zoneFaces[zoneI].size(), true),
                                nValidFaceZones,
                                mesh.faceZones()
                        );
                nValidFaceZones++;
            }
        }
    }

    if (cz.size() || fz.size())
    {
        mesh.addZones(List<pointZone*>(0), fz, cz);
    }

    // Remove empty defaultFaces
    label defaultPatchID = mesh.boundaryMesh().findPatchID(defaultFacesName);
    if (mesh.boundaryMesh()[defaultPatchID].size() == 0)
    {
        List<polyPatch*> newPatchPtrList((mesh.boundaryMesh().size() - 1));
        label newPatchi = 0;
        forAll(mesh.boundaryMesh(), patchi)
        {
            if (patchi != defaultPatchID)
            {
                const polyPatch& patch = mesh.boundaryMesh()[patchi];

                newPatchPtrList[newPatchi] = patch.clone
                (
                    mesh.boundaryMesh(),
                    newPatchi,
                    patch.size(),
                    patch.start()
                ).ptr();

                newPatchi++;
            }
        }
        repatcher.changePatches(newPatchPtrList);
    }

    mesh.write();

    Info<< "End\n" << endl;

}

void read_map_TriangleIndex2PhysicalName(const fileName& fname_map, Map<word>& index2name)
{
    IFstream inFile(fname_map);
    if (inFile.good())
    {
        if (fname_map.ext()==extName_map_boundaryMarkers2PatchNames)
        {
            Info<< "Starting to read .bm2name file of boundary markers to patch names" << endl;
        } else if(fname_map.ext()==extName_map_eleAttributes2cellZoneNames)
        {
            Info<< "Starting to read .attrib2name file of element attributes to cell zone names." << endl;
        }

        string line;
        while (inFile.good())
        {
            inFile.getLine(line); //skip the first row
            if(line[0]=='#')continue;
            IStringStream lineStr(line);
            label boundaryMarker;
            word patchName;
            lineStr >> boundaryMarker >> patchName;
            index2name.insert(boundaryMarker, patchName);
        }

    }else
    {
        if (fname_map.ext()==extName_map_boundaryMarkers2PatchNames)
        {
            WarningInFunction
                    << "Could not find .bm2name file to map the boundary markers to patch names. "
                    << "\nThe patch name will in format of 'Patch#Marker'" << endl;
        }else if(fname_map.ext()==extName_map_eleAttributes2cellZoneNames)
        {
            WarningInFunction
                    << "Could not find ."<<extName_map_eleAttributes2cellZoneNames<<" file to map the boundary markers to patch names. "
                    << "\nThe cell zone name will in format of 'zone#Attribute'" << endl;
        }else
        {
            WarningInFunction
                    << "Could not open "<<fname_map<<" file." << endl;
        }
    }
}

/**
 * @brief Read .edge file to construct boundary patches.
 * 
 * See https://www.cs.cmu.edu/~quake/triangle.ele.html for details of .edge file format.
 * 
 * @param fname_Triangle 
 * @param points 
 * @param mshToFoam 
 * @param patchFaces 
 */
void  read_edge(const fileName& fname_Triangle, const pointField& points, const Map<label>& mshToFoam,
                labelList& patchToPhys,List<DynamicList<face>>& patchFaces,Map<word>& physicalNames)
{
    Map<word> boundaryMarkers2PatchNames;
    read_map_TriangleIndex2PhysicalName(fname_Triangle.lessExt() + "." + extName_map_boundaryMarkers2PatchNames,boundaryMarkers2PatchNames);
    Info<< "Starting to read boundaries from .edge file" << endl;
    // make sure the extension name is correct
    fileName fname_edge = fname_Triangle.lessExt() + ".edge";
    IFstream inFile(fname_edge);
    if (!inFile.good())
    {
        FatalError<< "Can only read .edge file: "
                  <<inFile.name()
                  << exit(FatalError);
    }
    string line;
    inFile.getLine(line);
    IStringStream lineStr(line);
    label nEdges, hasBoundaryMarkers;
    lineStr >> nEdges >> hasBoundaryMarkers;
    if (hasBoundaryMarkers == 0)
    {
        WarningIn("There is no boundary markers in " + inFile.name())
                << "\n Please check!"
                << endl;
        return;
    }
    Map<label> physToPatch;
    face quadPoints(4);
    label regPhys;
    label nVerts_back = points.size()/2; // how many points on back patch
    for (label edgeI = 0; edgeI < nEdges; edgeI++)
    {
        string line;
        inFile.getLine(line);
        IStringStream lineStr(line);
        label edgeNumber;
        lineStr >> edgeNumber >> quadPoints[1] >> quadPoints[0] >> regPhys;
        if (regPhys==0)continue;
        quadPoints[2] = quadPoints[1] + nVerts_back;
        quadPoints[3] = quadPoints[0] + nVerts_back;
        renumber(mshToFoam, quadPoints); //Remember to renumber! Triangle's index start from 1 but polyMesh starts from 0
        Map<label>::iterator regFnd = physToPatch.find(regPhys);
        label patchi = -1;
        if (regFnd == physToPatch.end())
        {
            // New region. Allocate patch for it.
            patchi = patchFaces.size();
            patchFaces.setSize(patchi + 1);
            patchToPhys.setSize(patchi + 1);
            Info<< "Mapping region " << regPhys << " to Foam patch "
                << patchi << endl;
            physToPatch.insert(regPhys, patchi);
            if (boundaryMarkers2PatchNames.find(regPhys)==boundaryMarkers2PatchNames.end())
            {
                physicalNames.insert(regPhys, "Patch"+std::to_string(regPhys));
            } else
            {
                physicalNames.insert(regPhys, boundaryMarkers2PatchNames[regPhys]);
            }
            patchToPhys[patchi] = regPhys;
        }
        else
        {
            // Existing patch for region
            patchi = regFnd();
        }
        // Add quad to correct patchFaces.
        patchFaces[patchi].append(quadPoints);
    }
}


/**
 * @brief Read .ele file and construct cells. 
 * 
 * See https://www.cs.cmu.edu/~quake/triangle.ele.html for details of .ele file.
 * The cell zone information is included as attribute.
 * 
 * @param fname_Triangle 
 * @param points 
 * @param mshToFoam 
 * @param cells 
 */
void read_ele(const fileName& fname_Triangle, const pointField& points, const Map<label>& mshToFoam,const bool keepOrientation,
               cellShapeList& cells,labelList& patchToPhys,List<DynamicList<face>>& patchFaces,Map<word>& physicalNames,
              labelList& zoneToPhys,List<DynamicList<label>>& zoneCells
)
{
    Map<word> eleAttributes2cellZoneNames;
    read_map_TriangleIndex2PhysicalName(fname_Triangle.lessExt() + "." + extName_map_eleAttributes2cellZoneNames,eleAttributes2cellZoneNames);
    // make sure the extension name is correct
    fileName fname_ele = fname_Triangle.lessExt() + ".ele";
    IFstream inFile(fname_ele);
    if (!inFile.good())
    {
        FatalError<< "Can only read .ele file: "
                  <<inFile.name()
                  << exit(FatalError);
    }
    Info<< "Starting to read cells from .ele file" << endl;
    const cellModel& prism = *(cellModeller::lookup("prism"));
    labelList prismPoints(6);
    string line;
    inFile.getLine(line);
    IStringStream lineStr(line);
    // 1.
    label nElems, nNodesPerTri, nAttributes;
    lineStr >> nElems >> nNodesPerTri >> nAttributes;
    Info<< "Cells to be read:" << nElems << endl;
    Info<< "Each cell has " << nAttributes << " attributes." << endl << endl;
    cells.setSize(nElems);
    label celli = 0;
    label nPrism = 0;
    Map<label> physToPatch;
    Map<label> physToZone;
    face triPoints_back(3), triPoints_front(3);
    label regPhys_back = gMax(patchToPhys)+1, regPhys_front = gMax(patchToPhys)+2;
    label regPhys_cell;
    label nVerts_back = points.size()/2; // how many points on back patch
    for (label elemI = 0; elemI < nElems; elemI++)
    {
        string line;
        inFile.getLine(line);
        IStringStream lineStr(line);
        label elmNumber, regPhys;
        lineStr >> elmNumber >> prismPoints[0] >> prismPoints[1] >> prismPoints[2];
        for (label i = 0; i < 3; i++) {
            prismPoints[i+3] = prismPoints[i] + nVerts_back;
        }
        renumber(mshToFoam, prismPoints);
        for (label i = 0; i < 3; i++)
        {
            triPoints_back[i] = prismPoints[i];
            triPoints_front[i] = prismPoints[i+3];
        }
        // ------ add front and back patches -------
        Map<label>::iterator regFnd = physToPatch.find(regPhys_back);
        label patchi = -1;
        if (regFnd == physToPatch.end())
        {
            // New region. Allocate patch for it.
            patchi = patchFaces.size();
            patchFaces.setSize(patchi + 2);
            patchToPhys.setSize(patchi + 2);
            Info<< "Mapping back patches " << " to Foam patch " << patchi << endl;
            Info<< "Mapping front patches " << " to Foam patch " << patchi + 1 << endl;
            physToPatch.insert(regPhys_back, patchi);
            physToPatch.insert(regPhys_front, patchi + 1);
            physicalNames.insert(regPhys_back, patch_name_back);
            physicalNames.insert(regPhys_front, patch_name_front);
            patchToPhys[patchi] = regPhys_back;
            patchToPhys[patchi + 1] = regPhys_front;
        }
        else
        {
            // Existing patch for region
            patchi = regFnd();
        }
        // Add quad to correct patchFaces.
        patchFaces[patchi].append(triPoints_back);
        patchFaces[patchi + 1].append(triPoints_front);
        // read cell zone
        for (label i = 0; i < nAttributes; i++)
        {
            lineStr>> regPhys_cell;
        }
        storeCellInZone
        (
            regPhys_cell,
            celli,
            physToZone,
            zoneToPhys,
            zoneCells,
            physicalNames,
            eleAttributes2cellZoneNames,
            regPhys_front
        );
        cells[celli] = cellShape(prism, prismPoints);
        const cellShape& cell = cells[celli];
        if (!keepOrientation && !correctOrientation(points, cell))
        {
            Info<< "Inverting prism " << celli << endl;
            // Reorder prism.
            prismPoints[0] = cell[0];
            prismPoints[1] = cell[2];
            prismPoints[2] = cell[1];
            prismPoints[3] = cell[3];
            prismPoints[4] = cell[4];
            prismPoints[5] = cell[5];

            cells[celli] = cellShape(prism, prismPoints);
        }

        celli++;
        nPrism++;
    }
    //cells.setSize(celli);

    forAll(patchFaces, patchi)
    {
        patchFaces[patchi].shrink();
    }

    Info<< "Cells:" << endl
    << "    total:" << cells.size() << endl
    << "    prism:" << nPrism << endl
    << endl;

    if (cells.size() == 0)
    {
        FatalIOErrorInFunction(inFile)
                << "No cells read from file " << inFile.name()
                << "Perhaps you have not exported the 3D elements?"
                << exit(FatalIOError);
    }

    Info<< "CellZones:" << nl
        << "Zone\tSize" << endl;
}

void storeCellInZone(const label regPhys, const label celli,Map<label>& physToZone,
                     labelList& zoneToPhys,List<DynamicList<label>>& zoneCells,
                     Map<word>& physicalNames,const Map<word> eleAttributes2cellZoneNames,label baseNumber)
{
    label regPhys_cell = regPhys + baseNumber;
    Map<label>::const_iterator zoneFnd = physToZone.find(regPhys_cell);

    if (zoneFnd == physToZone.end())
    {
        // New region. Allocate zone for it.
        label zoneI = zoneCells.size();
        zoneCells.setSize(zoneI+1);
        zoneToPhys.setSize(zoneI+1);

        Info<< "Mapping region " << regPhys << " to Foam cellZone "
            << zoneI << endl;
        physToZone.insert(regPhys_cell, zoneI);
        if (eleAttributes2cellZoneNames.find(regPhys)==eleAttributes2cellZoneNames.end())
        {
            physicalNames.insert(regPhys_cell, "zone"+std::to_string(regPhys));
        } else
        {
            physicalNames.insert(regPhys + baseNumber, eleAttributes2cellZoneNames[regPhys]);
        }
        zoneToPhys[zoneI] = regPhys_cell;
        zoneCells[zoneI].append(celli);
    }
    else
    {
        // Existing zone for region
        zoneCells[zoneFnd()].append(celli);
    }
}


/**
 * @brief Read .node file. 
 * 
 * See https://www.cs.cmu.edu/~quake/triangle.node.html for the details of the format of .node file.
 * 
 * @param fname_Triangle 
 * @return pointField 
 */
void read_node(const fileName& fname_Triangle, const scalar& zmin, const scalar& zmax, pointField& points, Map<label>& mshToFoam)
{
    // make sure the extension name is correct
    fileName fname_node = fname_Triangle.lessExt() + ".node";
    IFstream inFile(fname_node);
    if (!inFile.good())
    {
        FatalError<< "Can only read .node file: "
                <<inFile.name()
                << exit(FatalError);
    }
    string line;
    inFile.getLine(line);
    IStringStream lineStr(line);
    // 1.
    label nVerts, dim, nAttributes, nBoudryMarkers;
    lineStr >> nVerts >> dim >> nAttributes >> nBoudryMarkers;
    Info<< "Vertices to be read:" << nVerts << endl;
    points.setSize(nVerts * 2); // front and back
    mshToFoam.resize(2*nVerts * 2);
    for (label pointi = 0; pointi < nVerts; pointi++)
    {
        label mshLabel;
        scalar xVal, yVal;
        string line;
        inFile.getLine(line);
        IStringStream lineStr(line);
        // not process the attributes and point markers at this moment
        // because this information is not needed by OpenFOAM polyMesh
        lineStr >> mshLabel >> xVal >> yVal;
        // points on back patch (zmin)
        point& pt_back = points[pointi];
        pt_back.x() = xVal;
        pt_back.y() = yVal;
        pt_back.z() = zmin;
        mshToFoam.insert(mshLabel, pointi);
        // points on back patch (zmin)
        point& pt_front = points[pointi + nVerts];
        pt_front.x() = xVal;
        pt_front.y() = yVal;
        pt_front.z() = zmax;
        mshToFoam.insert(mshLabel + nVerts, pointi + nVerts);
    }
}

// Determine whether cell is inside-out by checking for any wrong-oriented
// face.
bool correctOrientation(const pointField& points, const cellShape& shape)
{
    // Get centre of shape.
    point cc(shape.centre(points));

    // Get outwards pointing faces.
    faceList faces(shape.faces());

    forAll(faces, i)
    {
        const face& f = faces[i];

        const vector a(f.area(points));

        // Check if vector from any point on face to cc points outwards
        if (((points[f[0]] - cc) & a) < 0)
        {
            // Incorrectly oriented
            return false;
        }
    }

    return true;
}

// Find face in pp which uses all vertices in meshF (in mesh point labels)
label findFace(const primitivePatch& pp, const labelList& meshF)
{
    const Map<label>& meshPointMap = pp.meshPointMap();

    // meshF[0] in pp labels.
    if (!meshPointMap.found(meshF[0]))
    {
        Warning<< "Not using gmsh face " << meshF
               << " since zero vertex is not on boundary of polyMesh" << endl;
        return -1;
    }

    // Find faces using first point
    const labelList& pFaces = pp.pointFaces()[meshPointMap[meshF[0]]];

    // Go through all these faces and check if there is one which uses all of
    // meshF vertices (in any order ;-)
    forAll(pFaces, i)
    {
        label facei = pFaces[i];

        const face& f = pp[facei];

        // Count uses of vertices of meshF for f
        label nMatched = 0;

        forAll(f, fp)
        {
            if (findIndex(meshF, f[fp]) != -1)
            {
                nMatched++;
            }
        }

        if (nMatched == meshF.size())
        {
            return facei;
        }
    }

    return -1;
}


// Same but find internal face. Expensive addressing.
label findInternalFace(const primitiveMesh& mesh, const labelList& meshF)
{
    const labelList& pFaces = mesh.pointFaces()[meshF[0]];

    forAll(pFaces, i)
    {
        label facei = pFaces[i];

        const face& f = mesh.faces()[facei];

        // Count uses of vertices of meshF for f
        label nMatched = 0;

        forAll(f, fp)
        {
            if (findIndex(meshF, f[fp]) != -1)
            {
                nMatched++;
            }
        }

        if (nMatched == meshF.size())
        {
            return facei;
        }
    }
    return -1;
}

void renumber(const Map<label>& mshToFoam,labelList& labels)
{
    forAll(labels, labelI)
    {
        labels[labelI] = mshToFoam[labels[labelI]];
    }
}

// ************************************************************************* //
