Convert [ASPECT](https://aspect.geodynamics.org) mesh to OpenFOAM polyMesh.

# Usage 

## Step 1 

Run the modified program e.g. `aspect detachment.prm`

> 稍后添加一个 -case 参数用于指定caseDir

## Step 2

运行`renumberMesh -dict system/renumberMeshDict -overwrite` 进行重新排序，否则如果用`checkMesh`检查网格，应该会出现`upper triangular faces`的错误。
但是原始网格的cell排序跟ASPECT的cell排序是一致的，这样重新排序后，在将OpenFOAM结果转到ASPECT的时候就会出现问题：对应不上！**不过不用担心，renumberMesh可以输出一个cellMap文件记录了新旧网格的map**，这个必须通过`renumberMeshDict`中的`writeMaps true;`参数开启。

* 有时候有可能也需要运行一下`zipUpMesh`，根据情况看，如果checkMesh出现错误提示需要运行的时候再运行。

## Step 3
将OpenFOAM运算结果写入文件供ASPECT读取，ASPECT的每个单元一般有9个自由度，比如二维情况包括四个顶点+四条边上的中点+单元的中心，不过压力p只有四个自由度，即四个顶点。所以，可以将需要传递给ASPECT的field根据cellMap按照ASPECT的cell排序写入文件，然后在ASPECT中读取这个文件的数据到一个一维数组里面（一维数组就跟solution数组一样的逻辑就行）用一个类似下面的循环进行赋值更新：

```cpp
for (auto &cell : dof_handler.active_cell_iterators())
{
  if (cell->is_locally_owned())
  {
    std::vector<types::global_dof_index> local_dof_indices(finite_element.n_dofs_per_cell());
    cell->get_dof_indices(local_dof_indices);
    for (size_t i = 0; i < fpout_fields.size(); i++)
    {
      solution[local_dof_indices[local_dof_indices.size() -fpout_fields.size() + i]] = field_OpenFoam[i];//伪代码！！！ 具体取决于赋值给哪个变量，参考WritePolyMesh_Faces_owner_neighbor函数中的数据写入部分，这里的读取必须跟OpenFOAM里面的写出保持一致！！！
    }
  }
}
```

# Develop

## Step 1

Copy `aspectToFoam.h` to `***/include/aspect`

## Step 2

Add a member function `void aspectToFoam ();` just below `void run ();` in `include/aspect/simulator.h`

```cpp
void run ();
void aspectToFoam ();
```

## Step3 

Copy codes, which actually is implementation of member function `aspectToFoam`, in `core.cc` and paste it in `source/simulator/core.cc` just below member function of `run()` 

```cpp
template <int dim>
  void Simulator<dim>::run ()
  {
      //...
  }
template <int dim>
  void Simulator<dim>::aspectToFoam ()
  {
      //...
  }
```

## Step 4

Modify `main.cc` of ASPECT, add a argument check, if `-caseDir` is given, call `simulator.aspectToFoam();`.