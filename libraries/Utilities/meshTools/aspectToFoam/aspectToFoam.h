/**
 * @file aspectToFoam.h
 * @author Zhikui Guo (zguo@geomar.de)
 * @brief Convert ASPECT data and  OpenFOAM data to each other.
 * @version 0.1
 * @date 2021-06-30
 * 
 * @copyright Copyright (c) 2021
 * 
 */

#include "aspect/simulator.h"
#include "aspect/parameters.h"
#include "HydrothermalSinglePhaseDarcyFoam.H"
#ifndef ASPECT2FOAM
#define ASPECT2FOAM

namespace OpenFOAM
{
  struct parameters
  {
    bool enable;
    std::string caseDir, timeFormat, meshType;
    int timePrecision;
    std::vector<std::string> fieldNames;
  };
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
}

namespace aspect
{
  using namespace dealii;
  using namespace OpenFOAM;
  template <int dim>
  class aspectToFoam
  {
    public:
      parameters m_prm;
      std::string m_timeName;
      double m_currentTime, m_last_output_time, m_output_interval;
      std::vector<BoundaryFaces> m_boundaries;
      int m_Steps;
      cAspectFoam* m_aspectFoam;
    private:
      void WriteOpenFOAMhead(std::ofstream& fout, std::string className, std::string location, std::string object, std::string note="");
      std::vector<double> getBounds(const std::vector< Point< dim > > & xyz);
      void WritePolyMesh_Points(std::string meshDir, int numPoints, const std::vector<Point<dim> >& vertices, 
        const aspect::LinearAlgebra::Vector& mesh_displacements,std::map<int,int> map_solution_vertices, bool deform_mesh);
      void GetFaces(const Triangulation<dim>& triangulation, InternalFaces& internal, std::vector<BoundaryFaces>& boundary);
      void WritePolyMesh_Faces_owner_neighbor(std::string meshDir, const Triangulation<dim>& triangulation);
      void WriteVOLFieldData(std::string caseDir,std::string timeName, const Triangulation<dim>& triangulation, const DoFHandler<dim>& dof_handler,
        const FESystem<dim>& finite_element, const LinearAlgebra::BlockVector& solution, const Introspection<dim>& introspection,const std::vector<BoundaryFaces>& boundaries);
      void Triangulation2PolyMesh(std::string caseDir,std::string timeName,const Triangulation<dim>& triangulation, 
          const DoFHandler<dim>& dof_handler_deform_mesh, const aspect::LinearAlgebra::Vector& mesh_displacements, bool deform_mesh);
      std::string getTimeName(double time, std::string timeFormat, int timePrecision);
    public:
      aspectToFoam();
      ~aspectToFoam();
      void initFoamSolver(const Foam::argList* args);
      static void declare_parameters (ParameterHandler &prm);
      void parse_parameters (ParameterHandler &prm);
      void toFoam(const Triangulation<dim>& triangulation, const DoFHandler<dim>& dof_handler, 
      const FESystem<dim>& finite_element, const LinearAlgebra::BlockVector& solution, const Introspection<dim>& introspection,
      const DoFHandler<dim>& dof_handler_deform_mesh, const aspect::LinearAlgebra::Vector& mesh_displacements,bool deform_mesh, double time);
  };

}

#endif