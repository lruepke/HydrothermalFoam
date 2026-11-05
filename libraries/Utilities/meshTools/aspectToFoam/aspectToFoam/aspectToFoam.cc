#include <deal.II/grid/tria.h>
#include <deal.II/grid/grid_generator.h>
#include <deal.II/grid/grid_out.h>
#include <iostream>
#include <fstream>
#include <cmath>
using namespace dealii;

struct BoundaryFaces
{
  std::string patchName,typeName;
  std::vector<std::vector<uint> > faces;
  std::vector<uint> owners;
};
struct InternalFaces
{
  std::vector<std::vector<uint> > faces;
  std::vector<uint> owners, neighbours;
};

void WriteOpenFOAMhead(
  std::ofstream& fout, 
  std::string class0, 
  std::string location, 
  std::string object,
  std::string note=""
      )
{
  fout<<"FoamFile\n";
  fout<<"{\n";
  fout<<"  version     2.0;\n";
  fout<<"  format      ascii;\n";
  fout<<"  class       "<<class0<<";\n";
  if(note!="")fout<<"    note        \""<<note<<"\";\n";
  fout<<"  location    \""<<location<<"\";\n";
  fout<<"  object      "<<object<<";\n";
  fout<<"}\n";
}
// Y axis of ASPECT mesh must orient to depth, same as OpenFOAM coordinate system
template <int dim>
void WritePolyMesh_Points(std::string caseDir, int numPoints, const std::vector<Point<dim> >& vertices)
{
  std::ofstream fout(caseDir+"/constant/polyMesh/points");
  WriteOpenFOAMhead(fout,"vectorField","constant/polyMesh","points");
  if(dim==2)
  {
    fout<<numPoints*2<<"\n(\n";
    double zmin=0,zmax=0.3;
    for (size_t i = 0; i < vertices.size(); i++)
    {
      fout<<"(";
      for (size_t j = 0; j < dim; j++)
      {
        fout<<vertices[i][j]<<" ";
      }
      fout<<zmax<<")\n";
    }
    for (size_t i = 0; i < vertices.size(); i++)
    {
      fout<<"(";
      for (size_t j = 0; j < dim; j++)
      {
        fout<<vertices[i][j]<<" ";
      }
      fout<<zmin<<")\n";
    }
  }
  else if(dim==3)
  {
    fout<<numPoints<<"\n(\n";
    for (size_t i = 0; i < vertices.size(); i++)
    {
      fout<<"(";
      for (size_t j = 0; j < dim; j++)
      {
        fout<<vertices[i][j]<<" ";
      }
      fout<<")\n";
    }
  }
  fout<<")\n";

  fout.close();
}

template <int dim>
std::vector<double> getBounds(const std::vector< Point< dim > > & 	xyz)
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

template <int dim>
void GetFaces(Triangulation<dim>& triangulation, InternalFaces& internal, std::vector<BoundaryFaces>& boundary)
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
      std::cout<<"internal face"<<i<<" only has "<<cellIDs_internal[faceID_internal].size()<<" cells"<<std::endl;
      exit(0);
    }
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
  for (size_t i = 0; i < dim; i++)
  {
    std::cout<<bounds_xyz[i*2]<<", "<<bounds_xyz[i*2+1]<<std::endl;
  }
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
void WritePolyMesh_Faces_owner_neighbor(std::string caseDir, Triangulation<dim>& triangulation)
{
  // write faces
  std::ofstream fout(caseDir+"/constant/polyMesh/faces");
  WriteOpenFOAMhead(fout,"faceList","constant/polyMesh","faces");
  InternalFaces internal;
  std::vector<BoundaryFaces> boundaries;
  GetFaces(triangulation,internal,boundaries);
  int numFaces=internal.faces.size();
  for (size_t i = 0; i < boundaries.size(); i++)
  {
    numFaces+=boundaries[i].faces.size();
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
  for (size_t k = 0; k < boundaries.size(); k++)
  {
    for (size_t i = 0; i < boundaries[k].faces.size(); i++)
    {
      fout<<boundaries[k].faces[i].size()<<"(";
      for (size_t j = 0; j < boundaries[k].faces[i].size(); j++)
      {
        fout<<boundaries[k].faces[i][j]<<" ";
      }
      fout<<")\n";
    }
  }
  
  fout<<")\n";
  fout.close();
  // write owner and boundary
  std::ofstream fout_boundary(caseDir+"/constant/polyMesh/boundary");
  WriteOpenFOAMhead(fout_boundary,"polyBoundaryMesh","constant/polyMesh","boundary");
  std::ofstream fout_owner(caseDir+"/constant/polyMesh/owner");
  std::ofstream fout_neighbour(caseDir+"/constant/polyMesh/neighbour");
  std::string note=""; //"nPoints: 60 nCells: 19 nFaces: 86 nInternalFaces: 0";
  WriteOpenFOAMhead(fout_owner,"labelList","constant/polyMesh","owner",note);
  WriteOpenFOAMhead(fout_neighbour,"labelList","constant/polyMesh","neighbour",note);
  fout_owner<<numFaces<<"\n(\n";
  fout_neighbour<<internal.faces.size()<<"\n(\n";
  fout_boundary<<boundaries.size()<<"\n(\n";
  // internal
  int start_boundary=0;
  for (size_t i = 0; i < internal.owners.size(); i++)
  {
    fout_owner<<internal.owners[i]<<"\n";
    fout_neighbour<<internal.neighbours[i]<<"\n";
    start_boundary++;
  }
  // boundary
  for (size_t k = 0; k < boundaries.size(); k++)
  {
    fout_boundary<<"    "<<boundaries[k].patchName<<"\n    {\n        type            "<<boundaries[k].typeName<<";\n";
    fout_boundary<<"        nFaces          "<<boundaries[k].faces.size()<<";\n";
    fout_boundary<<"        startFace       "<<start_boundary<<";\n    }\n";
    for (size_t i = 0; i < boundaries[k].owners.size(); i++)
    {
      fout_owner<<boundaries[k].owners[i]<<"\n";
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
void Triangulation2PolyMesh(Triangulation<dim>& triangulation,std::string caseDir="example")
{
  std::string cmd="mkdir -p "+caseDir+"/constant/polyMesh";
  std::system(cmd.c_str());
  // write polyMesh
  WritePolyMesh_Points(caseDir, triangulation.n_vertices(),triangulation.get_vertices());
  WritePolyMesh_Faces_owner_neighbor(caseDir,triangulation);
}

void first_grid()
{
  const int dim=2;
  Triangulation<dim> triangulation;
  GridGenerator::hyper_cube(triangulation);
  triangulation.refine_global(4);
  int i=0;
  for (auto &cell : triangulation.active_cell_iterators())
  {
    if(i==12 || i==11)
    cell->set_refine_flag();
    i++;
  }
  triangulation.execute_coarsening_and_refinement();
  for (auto &cell : triangulation.active_cell_iterators())
  {
    if(cell->global_active_cell_index()==18)
    {
      cell->set_refine_flag();
      break;
    }
  }
  triangulation.execute_coarsening_and_refinement();
  std::ofstream out("grid-1.vtu");
  GridOut       grid_out;
  grid_out.write_vtu(triangulation, out);

  Triangulation2PolyMesh(triangulation,"Regular2DBox");
}

void second_grid()
{
  Triangulation<2> triangulation;
  const Point<2> center(1, 0);
  const double   inner_radius = 0.5, outer_radius = 1.0;
  GridGenerator::hyper_shell(
    triangulation, center, inner_radius, outer_radius, 10);
  for (unsigned int step = 0; step < 5; ++step)
    {
      for (auto &cell : triangulation.active_cell_iterators())
        {
          for (const auto v : cell->vertex_indices())
            {
              const double distance_from_center =
                center.distance(cell->vertex(v));
              if (std::fabs(distance_from_center - inner_radius) <=
                  1e-6 * inner_radius)
                {
                  cell->set_refine_flag();
                  break;
                }
            }
        }
      triangulation.execute_coarsening_and_refinement();
    }
  std::ofstream out("grid-2.vtu");
  GridOut       grid_out;
  grid_out.write_vtu(triangulation, out);

  Triangulation2PolyMesh(triangulation);
}
int main()
{
  first_grid();
  // second_grid();
}