#ifndef ASPECTTOFOAM_I
#define ASPECTTOFOAM_I
#include <aspect/aspectToFoam.h>

namespace aspect
{
    
  template <int dim>
  aspectToFoam<dim>::aspectToFoam()
  :m_currentTime(0),m_last_output_time(-1),m_output_interval(1),m_Steps(0),
  m_aspectFoam(NULL)
  {
  }
  template <int dim>
  aspectToFoam<dim>::~aspectToFoam()
  { 
    // if(m_aspectFoam)delete m_aspectFoam;
  }
  template <int dim>
  void aspectToFoam<dim>::initFoamSolver(const Foam::argList* args)
  {
    m_aspectFoam = new cAspectFoam(args);
  }
  // implementation 
  template <int dim>
  void aspectToFoam<dim>::declare_parameters (ParameterHandler &prm)
  {
    // declare parameters for OpenFOAM
    prm.enter_subsection ("OpenFOAM");
    {
      prm.declare_entry ("enable", "false",
                         Patterns::Bool(),
                         "Is enable OpenFOAM feature.");
      prm.declare_entry ("caseDir", "OpenFOAM",
                         Patterns::DirectoryName(),
                         "OpenFOAM case directory for coupling and communicating with ASPECT "
                         "can be anywhere. ");
      const std::string availablefieldNames =
            "all|"
            "temperature|velocity";
      prm.declare_entry("List of fields", "temperature",
                          Patterns::MultipleSelection(availablefieldNames),
                          "Field names converted between ASPECT and OpenFOAM"
                          "The following postprocessors are available:\n\n"
                          +
                          availablefieldNames);
      prm.declare_entry ("timePrecision", "6",
                         Patterns::Integer(-10, 20),
                         "Integer used in conjunction with timeFormat described above, 6 by default.");
      prm.declare_entry ("timeFormat", "general",
                       Patterns::Selection ("fixed|scientific|general"),
                        "Choice of format of the naming of the time directories.");
      prm.declare_entry ("mesh type", "static",
                       Patterns::Selection ("static|AMR|deformation"),
                        "Mesh type, one of (static|pure AMR|pure deformation|AMR deformation)."
                        "This descide how to store polyMesh information."
                        "(1) static: polyMesh only store once to constant/polyMesh;"
                        "(2) AMR: polyMesh will be stored in the corresponding time folder;"
                        "(3) deformation: this means pure deformable mesh, the topology of the mesh will not be changed with time, only vertices change."
                        "   So the topology information, e.g. owner, neighbour, will stored to constant/polyMesh only once."
                        "   But the points will be saved to each time/polyMesh folder and the link the other files of polyMesh from constant/polyMesh to time/polyMesh.");
    }
    prm.leave_subsection (); 
  }

  template <int dim>
  void aspectToFoam<dim>::parse_parameters (ParameterHandler &prm)
  {
    std::string aspect_outDir = prm.get ("Output directory");
    if (aspect_outDir.size() == 0)
      aspect_outDir = "./";
    else if (aspect_outDir[aspect_outDir.size()-1] != '/')
      aspect_outDir += "/";
    bool convert_to_years = prm.get_bool ("Use years in output instead of seconds");
    // get ASPECT output time interval
    prm.enter_subsection("Postprocess");
    {
      prm.enter_subsection("Visualization");
      {
        m_output_interval = prm.get_double ("Time between graphical output");
        if (convert_to_years)
          m_output_interval *= year_in_seconds;
      }
      prm.leave_subsection();
    }
    prm.leave_subsection();
    prm.enter_subsection ("OpenFOAM");
    {
      m_prm.enable = prm.get_bool("enable");
      m_prm.caseDir        = prm.get ("caseDir");
      if (m_prm.caseDir.size() == 0)
      m_prm.caseDir = "OpenFoam";
      if(m_prm.caseDir.find("/")==std::string::npos) //如果没有明确指定相对或绝对路径，则设置其父路径为ASPECT输出路径
      {
        m_prm.caseDir = aspect_outDir+m_prm.caseDir+"/processor"+std::to_string(Utilities::MPI::this_mpi_process(MPI_COMM_WORLD));
      }
      // field names
      m_prm.fieldNames = Utilities::split_string_list(prm.get("List of fields"));
      AssertThrow(Utilities::has_unique_entries(m_prm.fieldNames),
                  ExcMessage("The list of strings for the parameter "
                              "'OpenFOAM/List of fields' contains entries more than once. "
                              "This is not allowed. Please check your parameter file."));
      m_prm.timeFormat = prm.get("timeFormat");
      m_prm.timePrecision = prm.get_integer("timePrecision");
      m_prm.meshType = prm.get("mesh type");
    }
  }


  template <int dim>
  void aspectToFoam<dim>::WriteOpenFOAMhead( std::ofstream& fout, std::string className, std::string location, std::string object, std::string note)
  {
    fout<<"FoamFile\n";
    fout<<"{\n";
    fout<<"  version     2.0;\n";
    fout<<"  format      ascii;\n";
    fout<<"  class       "<<className<<";\n";
    if(note!="")fout<<"    note        \""<<note<<"\";\n";
    fout<<"  location    \""<<location<<"\";\n";
    fout<<"  object      "<<object<<";\n";
    fout<<"}\n";
  }
  
  // return [xmin,xmax,ymin,ymax]
  template <int dim>
  std::vector<double> aspectToFoam<dim>::getBounds(const std::vector< Point< dim > > & 	xyz)
  {
    std::vector<double> bounds(dim*2);
    for (size_t i = 0; i < dim; i++)
    {
      bounds[i*2] = 1E15;
      bounds[i*2+1] = -1E15;
    }
    for (size_t i = 0; i < xyz.size(); i++)
    {
      for (size_t d = 0; d < dim; d++)
      {
        if(xyz[i][d]<bounds[d*2]){bounds[d*2]=xyz[i][d];}
        else if(xyz[i][d]>bounds[d*2+1]){bounds[d*2+1]=xyz[i][d];}
      }
    }
    return bounds;
  }

  // Y axis of ASPECT mesh must orient to depth, same as OpenFOAM coordinate system
  template <int dim>
  void aspectToFoam<dim>::WritePolyMesh_Points(std::string meshDir, int numPoints, const std::vector<Point<dim> >& vertices, 
        const aspect::LinearAlgebra::Vector& mesh_displacements,std::map<int,int> map_solution_vertices, bool deform_mesh)
  {
    std::ofstream fout(meshDir+"/points");
    WriteOpenFOAMhead(fout,"vectorField","constant/polyMesh","points");
    // ASPECT里面的solution向量排列顺序是(假设dim=2,且这个solution是一个矢量)[s0_x, s0_y, s1_x, s1_y, ..., sn_x, sn_y]
    if(dim==2)
    {
      std::vector<double> bounds = getBounds(vertices);
      // std::cout<<"bounding box: ["<<bounds[0]<<", "<<bounds[1]<<"], ["<<bounds[2]<<", "<<bounds[3]<<"]\n";
      double ratio_z2xy = 0.1;
      double zmin=0,zmax=(((bounds[1] - bounds[0]) + (bounds[3] - bounds[2]))/2.0*ratio_z2xy);
      fout<<numPoints*2<<"\n(\n";
      if (deform_mesh)
      {
        for (size_t i = 0; i < vertices.size(); i++)
        {
          fout<<"(";
          for (size_t j = 0; j < dim; j++)
          {
            fout<<(vertices[i][j]+mesh_displacements[map_solution_vertices[i]+j])<<" ";
          }
          fout<<zmax<<")\n";
        }
        for (size_t i = 0; i < vertices.size(); i++)
        {
          fout<<"(";
          for (size_t j = 0; j < dim; j++)
          {
            fout<<(vertices[i][j]+mesh_displacements[map_solution_vertices[i]+j])<<" ";
          }
          fout<<zmin<<")\n";
        }
      }else
      {
        for (size_t i = 0; i < vertices.size(); i++)
        {
          fout<<"(";
          for (size_t j = 0; j < dim; j++)
          {
            fout<<(vertices[i][j])<<" ";
          }
          fout<<zmax<<")\n";
        }
        for (size_t i = 0; i < vertices.size(); i++)
        {
          fout<<"(";
          for (size_t j = 0; j < dim; j++)
          {
            fout<<(vertices[i][j])<<" ";
          }
          fout<<zmin<<")\n";
        }
      }
      
      
    }
    else
    {
      std::cout<<"WritePolyMesh_Points Only support 2D so far\n"<<std::endl;
      exit(0);
    }
    fout<<")\n";

    fout.close();
  }

  template <int dim>
  void aspectToFoam<dim>::GetFaces(const Triangulation<dim>& triangulation, InternalFaces& internal, std::vector<BoundaryFaces>& boundary)
  {
    int numFaces_all = triangulation.n_faces();
    int numVertices = triangulation.n_vertices();
    std::vector<bool> faces_used(numFaces_all); //用不标记某一个face是否已经被提取: 向量初始化为false
    std::vector<std::vector<uint> > cellIDs_internal(numFaces_all);//记录每一个被提取的internal face的owner和neighbour的cell ID
    std::vector<uint> faceIDs_internal;
    BoundaryFaces frontPatch,backPatch,sidesPatch;
    frontPatch.patchName="front", backPatch.patchName="back", sidesPatch.patchName="sides";
    frontPatch.typeName="empty", backPatch.typeName="empty", sidesPatch.typeName="patch";
    std::vector<Point<dim> > center_active_cells;
    // 提取faces并加入faces向量
    int ind_cell=-1;
    for (auto &cell : triangulation.active_cell_iterators())
    {
      if (!(cell->is_locally_owned()))continue;
      ind_cell++;
      center_active_cells.push_back(cell->center());
      // add cell face it self [only for 2d]
      uint vertices_per_cell = cell->n_vertices();
      // 因为目前看到ASPECT的顶点顺序为[(xmin ymin), (xmax, ymin), (xmin,ymax), (xmax, ymax)]，三角形的情况还没遇到，所以在这里判断一下，以后遇到三角形的情况再校正
      std::vector<uint> vertices_cell_front(vertices_per_cell),vertices_cell_back(vertices_per_cell);
      if(vertices_per_cell==4)
      {
        for (unsigned int v = 0; v < 2; ++v)
        {
          vertices_cell_front[v] = cell->vertex_index(v);
          vertices_cell_front[4-1-v] = cell->vertex_index(v+2);
        }
      }else
      {
        std::cout<<"第 "<<ind_cell<<" 个cell有"<<vertices_per_cell<<"个顶点(一般为4个)，需要重新检查程序"<<std::endl;
        exit(0);
      }
      for (size_t i = 0; i <vertices_cell_front.size(); i++)
      {
        vertices_cell_back[vertices_cell_front.size()-1-i]=vertices_cell_front[i]+numVertices;
      }
      frontPatch.faces.push_back(vertices_cell_front);
      frontPatch.owners.push_back(ind_cell);
      backPatch.faces.push_back(vertices_cell_back);
      backPatch.owners.push_back(ind_cell);
      uint faceid=-1;
      for (auto &face : cell->face_iterators())
      {
        faceid++;
        uint faceID = face->index();
        if(faces_used[faceID]) //此face已经被提取，跳过
        {
          cellIDs_internal[faceID].push_back(ind_cell);
          continue;
        }
        // check neighbor is a refine cell, if yes, skip the coarse face
        if(cell->neighbor_index(faceid)!=-1)
        {
          bool hasChildern=cell->neighbor(faceid)->has_children();
          if(hasChildern)
          {
            uint fid=0;
            for (auto &face_neighbour_child : cell->neighbor_child_on_subface(faceid,0)->face_iterators())
            {
              if(cell->neighbor_child_on_subface(faceid,0)->neighbor_index(fid)==cell->index())
              {
                cellIDs_internal[face_neighbour_child->index()].push_back(ind_cell);
                break;
              }
              fid++;
            }
            fid=0;
            for (auto &face_neighbour_child : cell->neighbor_child_on_subface(faceid,1)->face_iterators())
            {
              if(cell->neighbor_child_on_subface(faceid,1)->neighbor_index(fid)==cell->index())
              {
                cellIDs_internal[face_neighbour_child->index()].push_back(ind_cell);
                break;
              }
              fid++;
            }
            continue;
          }
        }
        uint n_vertices=face->n_vertices();
        uint n_vertices2=n_vertices*2;
        std::vector<uint> vertices_face(n_vertices*2);
        for(uint j=0;j<n_vertices;j++)
        {
          vertices_face[j] = face->vertex_index(j);
          vertices_face[n_vertices2-1-j] = vertices_face[j]+numVertices;
        }
        // check boundary
        if(cell->neighbor_index(faceid)==-1)
        {
          sidesPatch.faces.push_back(vertices_face);
          sidesPatch.owners.push_back(ind_cell);
        }
        else
        {
          internal.faces.push_back(vertices_face);
          internal.owners.push_back(ind_cell);//暂时的，后面会计算校正的
          internal.neighbours.push_back(ind_cell);//暂时的
          faceIDs_internal.push_back(faceID);
          cellIDs_internal[faceID].push_back(ind_cell);
        }
        faces_used[faceID]=true; //标记此face已被提取
      }
    }
    std::cout<<"total internal faces: "<<internal.faces.size()<<std::endl;
    std::cout<<"front faces: "<<frontPatch.faces.size()<<std::endl;
    std::cout<<"back faces: "<<backPatch.faces.size()<<std::endl;
    std::cout<<"side patches: "<<sidesPatch.faces.size()<<std::endl;
    // 计算internal face的owner和neighbour
    const std::vector<Point<dim> > vertices=triangulation.get_vertices();
    for (size_t i = 0; i < internal.faces.size(); i++)
    {
      uint faceID_internal=faceIDs_internal[i];
      // 计算face的方向向量
      Point<2> norm_face, vCell12;
      norm_face[0]=-vertices[internal.faces[i][1]][1] + vertices[internal.faces[i][0]][1]; //-a2
      norm_face[1]=vertices[internal.faces[i][1]][0] - vertices[internal.faces[i][0]][0]; //a1
      if(cellIDs_internal[faceID_internal].size()<2)
      {
        // std::cout<<"internal face"<<i<<" only has "<<cellIDs_internal[faceID_internal].size()<<" cell, it could be processor boundary"<<std::endl;
        // exit(0);
      }
      else
      {
        uint ind_cell1=cellIDs_internal[faceID_internal][0], ind_cell2=cellIDs_internal[faceID_internal][1];
        vCell12[0]=center_active_cells[ind_cell2][0] - center_active_cells[ind_cell1][0];
        vCell12[1]=center_active_cells[ind_cell2][1] - center_active_cells[ind_cell1][1];
        double norm_dot_vCell12=norm_face[0]*vCell12[0] + norm_face[1]*vCell12[1];
        if(norm_dot_vCell12>0) //norm orient from owner to neighbour
        {
          internal.owners[i]=ind_cell1;
          internal.neighbours[i]=ind_cell2;
        }else
        {
          internal.owners[i]=ind_cell2;
          internal.neighbours[i]=ind_cell1;
        }
      }
    }
    // 重新计算并检查sides(front and back已经在赋值的时候确保了其正确性)边界face的节点连接顺序，确保法向方向向外
    for (size_t i = 0; i < sidesPatch.faces.size(); i++)
    {
      // 计算face的方向向量
      Point<2> norm_face, vCell2boundary;
      norm_face[0]=-vertices[sidesPatch.faces[i][1]][1] + vertices[sidesPatch.faces[i][0]][1]; //-a2
      norm_face[1]=vertices[sidesPatch.faces[i][1]][0] - vertices[sidesPatch.faces[i][0]][0]; //a1
      uint ind_cell=sidesPatch.owners[i];
      vCell2boundary[0]=vertices[sidesPatch.faces[i][0]][0] - center_active_cells[ind_cell][0];
      vCell2boundary[1]=vertices[sidesPatch.faces[i][0]][1] - center_active_cells[ind_cell][1];
      double norm_dot_vCell2boundary=norm_face[0]*vCell2boundary[0] + norm_face[1]*vCell2boundary[1];
      if(norm_dot_vCell2boundary<0)
      {
        std::vector<uint> connect_old(sidesPatch.faces[i]);
        for (size_t k = 0; k < connect_old.size(); k++)
        {
          sidesPatch.faces[i][k] = connect_old[connect_old.size()-1-k];
        }
        
      }
    }
    // split side patches to left, right, top, bottom
    std::vector< Point< dim > >xyz(vertices.size()*2);
    for (size_t i = 0; i < vertices.size(); i++)
    {
      xyz[i]=vertices[i];
      xyz[i+vertices.size()]=vertices[i];
    }
    std::vector<double> bounds_xyz = getBounds(vertices);
    // for (size_t i = 0; i < dim; i++)
    // {
    //   std::cout<<bounds_xyz[i*2]<<", "<<bounds_xyz[i*2+1]<<std::endl;
    // }
    BoundaryFaces leftPatch, rightPatch, topPatch, bottomPatch, unknownPatch;
    leftPatch.patchName="left", rightPatch.patchName="right", topPatch.patchName="top", bottomPatch.patchName="bottom", unknownPatch.patchName="unknown";
    leftPatch.typeName="patch", rightPatch.typeName="patch", topPatch.typeName="patch", bottomPatch.typeName="patch", unknownPatch.typeName="patch";
    const double eps = 1E-8;
    for (size_t i = 0; i < sidesPatch.faces.size(); i++)
    {
      if(std::fabs(xyz[sidesPatch.faces[i][0]][0]-bounds_xyz[0])<eps && std::fabs(xyz[sidesPatch.faces[i][1]][0]-bounds_xyz[0])<eps )
      {
        leftPatch.faces.push_back(sidesPatch.faces[i]);
        leftPatch.owners.push_back(sidesPatch.owners[i]);
      }else if(std::fabs(xyz[sidesPatch.faces[i][0]][0]-bounds_xyz[1])<eps && std::fabs(xyz[sidesPatch.faces[i][1]][0]-bounds_xyz[1])<eps )
      {
        rightPatch.faces.push_back(sidesPatch.faces[i]);
        rightPatch.owners.push_back(sidesPatch.owners[i]);
      }else if(xyz[sidesPatch.faces[i][0]][1]==bounds_xyz[2] && xyz[sidesPatch.faces[i][1]][1]==bounds_xyz[2])
      {
        bottomPatch.faces.push_back(sidesPatch.faces[i]);
        bottomPatch.owners.push_back(sidesPatch.owners[i]);
      }else if(xyz[sidesPatch.faces[i][0]][1]==bounds_xyz[3] && xyz[sidesPatch.faces[i][1]][1]==bounds_xyz[3])
      {
        topPatch.faces.push_back(sidesPatch.faces[i]);
        topPatch.owners.push_back(sidesPatch.owners[i]);
      }else
      {
        unknownPatch.faces.push_back(sidesPatch.faces[i]);
        unknownPatch.owners.push_back(sidesPatch.owners[i]);
      }
    }
    std::cout<<"left: "<<leftPatch.faces.size()
            <<"right: "<<rightPatch.faces.size()
            <<"bottom: "<<bottomPatch.faces.size()
            <<"top: "<<topPatch.faces.size()
            <<"unknown: "<<unknownPatch.faces.size()
            <<"sides: "<<sidesPatch.faces.size()
            <<"\n";
    // const std::vector< Point< spacedim > > & 	get_vertices () const
    boundary.push_back(frontPatch);
    boundary.push_back(backPatch);
    // boundary.push_back(sidesPatch);
    if(leftPatch.faces.size()>0)boundary.push_back(leftPatch);
    if(rightPatch.faces.size()>0)boundary.push_back(rightPatch);
    if(bottomPatch.faces.size()>0)boundary.push_back(bottomPatch);
    if(topPatch.faces.size()>0)boundary.push_back(topPatch);
    if(unknownPatch.faces.size()>0)boundary.push_back(unknownPatch);
    // return faces;
  }

  template <int dim>
  void aspectToFoam<dim>::WritePolyMesh_Faces_owner_neighbor(std::string meshDir,const Triangulation<dim>& triangulation)
  {
    // write faces
    std::ofstream fout(meshDir+"/faces");
    WriteOpenFOAMhead(fout,"faceList","constant/polyMesh","faces");
    InternalFaces internal;
    std::vector<BoundaryFaces> boundaries;
    GetFaces(triangulation,internal,boundaries);
    m_boundaries = boundaries;
    int numFaces=internal.faces.size();
    for (size_t i = 0; i < m_boundaries.size(); i++)
    {
      numFaces+=m_boundaries[i].faces.size();
    }
    
    fout<<numFaces<<"\n(\n";
    // internal
    for (size_t i = 0; i < internal.faces.size(); i++)
    {
      fout<<internal.faces[i].size()<<"(";
      for (size_t j = 0; j < internal.faces[i].size(); j++)
      {
        fout<<internal.faces[i][j]<<" ";
      }
      fout<<")\n";
    }
    // boundaries
    for (size_t k = 0; k < m_boundaries.size(); k++)
    {
      for (size_t i = 0; i < m_boundaries[k].faces.size(); i++)
      {
        fout<<m_boundaries[k].faces[i].size()<<"(";
        for (size_t j = 0; j < m_boundaries[k].faces[i].size(); j++)
        {
          fout<<m_boundaries[k].faces[i][j]<<" ";
        }
        fout<<")\n";
      }
    }
    
    fout<<")\n";
    fout.close();
    // write owner and boundary
    std::ofstream fout_boundary(meshDir+"/boundary");
    WriteOpenFOAMhead(fout_boundary,"polyBoundaryMesh","constant/polyMesh","boundary");
    std::ofstream fout_owner(meshDir+"/owner");
    std::ofstream fout_neighbour(meshDir+"/neighbour");
    std::string note=""; //"nPoints: 60 nCells: 19 nFaces: 86 nInternalFaces: 0";
    WriteOpenFOAMhead(fout_owner,"labelList","constant/polyMesh","owner",note);
    WriteOpenFOAMhead(fout_neighbour,"labelList","constant/polyMesh","neighbour",note);
    fout_owner<<numFaces<<"\n(\n";
    fout_neighbour<<internal.faces.size()<<"\n(\n";
    fout_boundary<<m_boundaries.size()<<"\n(\n";
    // internal
    int start_boundary=0;
    for (size_t i = 0; i < internal.owners.size(); i++)
    {
      fout_owner<<" "<<internal.owners[i]<<" \n";
      fout_neighbour<<" "<<internal.neighbours[i]<<" \n";
      start_boundary++;
    }
    // boundary
    for (size_t k = 0; k < m_boundaries.size(); k++)
    {
      fout_boundary<<"    "<<m_boundaries[k].patchName<<"\n    {\n        type            "<<m_boundaries[k].typeName<<";\n";
      fout_boundary<<"        nFaces          "<<m_boundaries[k].faces.size()<<";\n";
      fout_boundary<<"        startFace       "<<start_boundary<<";\n    }\n";
      for (size_t i = 0; i < m_boundaries[k].owners.size(); i++)
      {
        fout_owner<<m_boundaries[k].owners[i]<<"\n";
        start_boundary++;
      }
    }
    fout_owner<<")\n";
    fout_owner.close();
    fout_neighbour<<")\n";
    fout_neighbour.close();
    fout_boundary<<")\n";
    fout_boundary.close();
  }

  template <int dim>
  void aspectToFoam<dim>::WriteVOLFieldData(std::string caseDir,std::string timeName, const Triangulation<dim>& triangulation, const DoFHandler<dim>& dof_handler,
        const FESystem<dim>& finite_element, const LinearAlgebra::BlockVector& solution, const Introspection<dim>& introspection,
        const std::vector<BoundaryFaces>& boundaries)
  {
    // write data
    // // solution [U, p, T, field1, field2, ..., ]
    // // 其中p的n_dofs_per_cell为4,其他的都为9
    // std::cout<<"nvertices: "<<triangulation.n_vertices()<<"\n";
    // std::cout<<"cells: "<<triangulation.n_active_cells()<<"\n";
    // std::cout<<"faces: "<<triangulation.n_faces()<<"\n";
    // std::cout<<"solutions size: "<<solution.size()<<"\n";
    // std::vector<std::string > fieldNames = introspection.get_composition_names();
    // for (size_t i = 0; i < fieldNames.size(); i++)
    // {
    //   std::cout<<fieldNames[i]<<std::endl;
    // }
    // std::cout<<"block_indices v: "<<introspection.block_indices.velocities<<"\n";
    // std::cout<<"block_indices p: "<<introspection.block_indices.pressure<<"\n";
    // std::cout<<"block_indices T: "<<introspection.block_indices.temperature<<"\n";
    // std::cout<<"introspection.get_fes: "<<introspection.get_fes().size()<<"\n";
    // const FiniteElement< dim > * fe = introspection.get_fes()[0];
    // for(size_t i=0;i<introspection.get_fes().size();i++)
    // std::cout<<"n_dofs_per_cell "<<i<<": "<<introspection.get_fes()[i]->n_dofs_per_cell()<<"\n"; 
    // std::cout<<"finite_element n_dofs_per_cell: "<<finite_element.n_dofs_per_cell()<<"\n";

    std::vector<std::ofstream > fpout_fields;
    std::vector<std::string > fieldNames;
    fieldNames.push_back("T");
    fpout_fields.emplace_back(std::ofstream{ caseDir+"/"+timeName+"/T" });
    for (size_t i = 0; i < introspection.get_composition_names().size(); i++)
    {
      fieldNames.push_back(introspection.get_composition_names()[i]);
      fpout_fields.emplace_back(std::ofstream{ caseDir+"/"+timeName+"/"+introspection.get_composition_names()[i] });
    }
    uint n_local_active_cells = 0;
    for (auto &cell : dof_handler.active_cell_iterators())
    {
      if (cell->is_locally_owned())
      {
        n_local_active_cells++;
      }
    }
    for (size_t i = 0; i < fpout_fields.size(); i++)
    {
      WriteOpenFOAMhead(fpout_fields[i],"volScalarField",timeName,fieldNames[i]);
      fpout_fields[i]<<"dimensions      [0 0 0 1 0 0 0];\n";
      fpout_fields[i]<<"internalField   nonuniform List<scalar> \n";
      fpout_fields[i]<<n_local_active_cells<<"\n";
      fpout_fields[i]<<"(\n";
    }
    
    // ==========
    for (auto &cell : dof_handler.active_cell_iterators())
    {
      if (cell->is_locally_owned())
      {
        std::vector<types::global_dof_index> local_dof_indices(finite_element.n_dofs_per_cell());
        cell->get_dof_indices(local_dof_indices);
        // for (uint i=0;i<finite_element.n_dofs_per_cell();i++)
        // {
        //   // std::cout<<solution[local_dof_indices[2]]<<"\n";
        // }
        for (size_t i = 0; i < fpout_fields.size(); i++)
        {
          fpout_fields[i]<<solution[local_dof_indices[local_dof_indices.size() -fpout_fields.size() + i]]<<"\n";
        }
      }
    }
    // ==========
    // for (auto &cell : triangulation.active_cell_iterators())
    // {
    //   fpout_field<<cell->center()[0]<<"\n";
    // }
    for (size_t i = 0; i < fpout_fields.size(); i++)
    {
      fpout_fields[i]<<")\n;\n";
      fpout_fields[i]<<"boundaryField\n";
      fpout_fields[i]<<"{\n";
      for (size_t k = 0; k < boundaries.size(); k++)
      {
        if(boundaries[k].typeName=="empty")
        {
          fpout_fields[i]<<"\t"<<boundaries[k].patchName<<"{ type "<<boundaries[k].typeName<<"; }\n";
        }else
        {
          fpout_fields[i]<<"\t"<<boundaries[k].patchName<<"{ type zeroGradient; }\n";
        }
        
      }
      fpout_fields[i]<<"}\n";
      fpout_fields[i].close();
    }
    // // renumber mesh: 测试了一下，renumber前后并没有计算效率的明显提升，因此不用这一步骤，避免不必要的麻烦！
    // std::string cmd = "renumberMesh -dict system/renumberMeshDict -overwrite -latestTime -case "+caseDir;
    // std::cout<<cmd<<"\n";
    // // system(cmd.c_str());
  }

  template <int dim>
  void aspectToFoam<dim>::Triangulation2PolyMesh(std::string caseDir,std::string timeName,const Triangulation<dim>& triangulation, 
      const DoFHandler<dim>& dof_handler_deform_mesh, const aspect::LinearAlgebra::Vector& mesh_displacements, bool deform_mesh)
  {
    // !!!! mesh_displacements for every vertex, but it's index is not the same as global vertices
    // need a index map
    // construct map from global vertex index to solution
    std::map<int,int> map_solution_vertices; //只需要记录第一个分量的index即可，第二或第三只需要增1即可
    if(deform_mesh)
    {
      // uint cellID=0;
      for (const auto &cell : dof_handler_deform_mesh.active_cell_iterators())
      {
        if (cell->is_locally_owned())
        {
          std::vector<types::global_dof_index> local_dof_indices(cell->n_vertices()*dim);
          cell->get_dof_indices(local_dof_indices);
          for (uint i=0;i<cell->n_vertices();i++)
          { 
            // std::cout<<"cell "<<cellID<<" dof: "<<local_dof_indices[i]<<", vertex: "<<cell->vertex_index(i)<<" \n";
            map_solution_vertices[cell->vertex_index(i)] = local_dof_indices[i*dim];
          }
        }
        // cellID++;
      }
    }
    // write polyMesh
    std::string meshDir, cmd;
    if(m_prm.meshType=="AMR") //always write to time folder
    {
      meshDir=caseDir+"/"+timeName+"/polyMesh";
      cmd="mkdir -p "+meshDir; std::system(cmd.c_str()); // create data Dir
      WritePolyMesh_Points(meshDir, triangulation.n_vertices(),triangulation.get_vertices(), mesh_displacements, map_solution_vertices,deform_mesh);
      WritePolyMesh_Faces_owner_neighbor(meshDir,triangulation);
    }else if(m_prm.meshType=="deformation") //write topology data to constant/polyMesh only once, but always write points to time/polyMesh
    {
      if(m_Steps==0)
      {
        WritePolyMesh_Faces_owner_neighbor(caseDir+"/constant/polyMesh",triangulation);
      }
      meshDir = caseDir+"/"+timeName+"/polyMesh";
      cmd="mkdir -p "+meshDir; std::system(cmd.c_str()); // create data Dir
      // write points
      WritePolyMesh_Points(meshDir, triangulation.n_vertices(),triangulation.get_vertices(), mesh_displacements, map_solution_vertices,deform_mesh);
      // link topology data to time/polyMesh folder
      std::vector<std::string> topology = {"owner","neighbour","faces"};
      for (size_t i = 0; i < topology.size(); i++)
      {
        cmd = "ln -s "+caseDir+"/constant/polyMesh/"+topology[i]+" "+meshDir;
        std::cout<<"ln command: "<<cmd<<"\n";
        // system(cmd.c_str());
      }
    }else if(m_prm.meshType=="static") //write points and topology data to constant/polyMesh only once!!
    {
      if(m_Steps==0)
      {
        meshDir=caseDir+"/constant/polyMesh";
        WritePolyMesh_Points(meshDir, triangulation.n_vertices(),triangulation.get_vertices(), mesh_displacements, map_solution_vertices,deform_mesh);
        WritePolyMesh_Faces_owner_neighbor(meshDir,triangulation);
      }
    }
  }

  template <int dim>
  std::string aspectToFoam<dim>::getTimeName(double time, std::string timeFormat, int timePrecision)
  {
    std::stringstream timeName;
    if(timeFormat=="general")
    {
      if(time<std::pow(10,timePrecision+1) || time>1E-4) //
      {
        timeName << std::setprecision(timePrecision) << time;
      }
      else 
      {
        timeName<< std::resetiosflags(std::ios::fixed) << std::setiosflags(std::ios::scientific) << time;
      }
    }else
    {
      timeName<< std::resetiosflags(std::ios::fixed) << std::setiosflags(std::ios::scientific) << time;
    }
    return timeName.str();
  }


  template <int dim>
  void aspectToFoam<dim>::toFoam(const Triangulation<dim>& triangulation, const DoFHandler<dim>& dof_handler, 
      const FESystem<dim>& finite_element, const LinearAlgebra::BlockVector& solution, const Introspection<dim>& introspection,
      const DoFHandler<dim>& dof_handler_deform_mesh, const aspect::LinearAlgebra::Vector& mesh_displacements, 
      bool deform_mesh, double time)
  {
    if(!m_prm.enable)
    {
      return;
    }
    m_currentTime = time;
    if ((m_currentTime < (m_last_output_time + m_output_interval)) && (m_currentTime != 0))
    return;

    m_timeName=getTimeName(time,m_prm.timeFormat,m_prm.timePrecision);
    std::string cmd;
    cmd="mkdir -p "+m_prm.caseDir+"/"+m_timeName;
    std::system(cmd.c_str()); // create data Dir
    if(m_Steps==0)
    {
      cmd="mkdir -p "+m_prm.caseDir+"/constant/polyMesh";
      std::system(cmd.c_str()); // create constant polyMesh dir
    }
    // Utilities::create_directory (output_directory, mpi_communicator,false);
    // write polyMesh
    Triangulation2PolyMesh(m_prm.caseDir,m_timeName,triangulation, dof_handler_deform_mesh, mesh_displacements,deform_mesh);
    // write solution data as OpenFOAM volField data
    WriteVOLFieldData(m_prm.caseDir,m_timeName,triangulation, dof_handler, finite_element, solution, introspection, m_boundaries);

    // update last write time and steps
    m_last_output_time = time;
    m_Steps++;
  }

} 

#endif