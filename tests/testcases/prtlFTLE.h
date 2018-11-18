#ifndef LIBPRTL_VTK_PRTLFTLE_H
#define LIBPRTL_VTK_PRTLFTLE_H

#include "prtl_vtk_export.h"
#include <vtkImageAlgorithm.h>

/* pv_( 
  filter(name='FTLE').menu('prtl') \
    .input(data_types='vtkImageData') \
      .documentation('Vector field input.')
   )pv_ */
class PRTL_VTK_EXPORT prtlFTLE : public vtkImageAlgorithm {
 public:
  static prtlFTLE* New();
  vtkTypeMacro(prtlFTLE, vtkImageAlgorithm);
  void PrintSelf(ostream &os, vtkIndent indent) override;

  vtkSetVector3Macro(SeedBoxScale, double);
  vtkGetVector3Macro(SeedBoxScale, double);
  vtkSetVector3Macro(SeedBoxPosition, double);
  vtkGetVector3Macro(SeedBoxPosition, double);
  vtkSetVector3Macro(SeedBoxSamples, int);
  vtkGetVector3Macro(SeedBoxSamples, int);

  vtkSetMacro(SpaceTimeInput, bool);
  vtkGetMacro(SpaceTimeInput, bool);

  vtkSetMacro(BoundaryMode0, int);
  vtkGetMacro(BoundaryMode0, int);
  vtkSetMacro(BoundaryMode1, int);
  vtkGetMacro(BoundaryMode1, int);
  vtkSetMacro(BoundaryMode2, int);
  vtkGetMacro(BoundaryMode2, int);
  vtkSetMacro(BoundaryMode3, int);
  vtkGetMacro(BoundaryMode3, int);

  vtkSetMacro(StartTime, double);
  vtkGetMacro(StartTime, double);
  vtkSetMacro(AdvectionTime, double);
  vtkGetMacro(AdvectionTime, double);
  vtkSetMacro(StepSize, double);
  vtkGetMacro(StepSize, double);

  vtkSetMacro(UseCUDA, bool);
  vtkGetMacro(UseCUDA, bool);
  vtkSetMacro(BlockSize, int);
  vtkGetMacro(BlockSize, int);

 protected:
  // pv_( autovector(label='Seeding Resolution') )pv_
  int SeedBoxSamples[3] {10, 10, 10};

  // pv_( input_array(label='Vectors', attribute_type='Vectors') )pv_

  // pv_( autovector(label='SeedPosition', animateable=True).range() )pv_
  double SeedBoxPosition[3] {0.0, 0.0, 0.0};
  // pv_( autovector(label='SeedScale', animateable=True).range() )pv_
  double SeedBoxScale[3] {1.0, 1.0, 1.0};

  /* pv_( xml_property(''' 
      <PropertyGroup label="Seeding Box" panel_widget="InteractiveBox">
          <Property function="Position" name="SeedPosition" />
          <Property function="Scale" name="SeedScale" />
          <Property function="Input" name="Input" />
      </PropertyGroup>
  ''') )pv_ */

  // pv_( autovector(label='Initial Time', group_id=0, animateable=True).range() )pv_
  double StartTime {0.0};
  // pv_( autovector(label='Advection Time', group_id=0, animateable=True).range() )pv_
  double AdvectionTime {1.0};
  // pv_( autovector(label='Step Size', group_id=0) )pv_
  double StepSize {0.1};
  // pv_( group('Integrator', 0) )pv_

  // pv_( autovector(label='Use CUDA', panel_visibility='advanced') )pv_
  bool UseCUDA {false};
  // pv_( autovector(label='CUDA block size', panel_visibility='advanced') )pv_
  int BlockSize {1000000};

  // pv_( autovector(label='Input is space-time', group_id=1) )pv_
  bool SpaceTimeInput {false};
  // pv_( autovector(label='X1', group_id=1).enumeration(items=['None', 'Wrap', 'Clamp'], values=[0,1,2]) )pv_
  int BoundaryMode0 {0};
  // pv_( autovector(label='X2', group_id=1).enumeration(items=['None', 'Wrap', 'Clamp'], values=[0,1,2]) )pv_
  int BoundaryMode1 {0};
  // pv_( autovector(label='X3', group_id=1).enumeration(items=['None', 'Wrap', 'Clamp'], values=[0,1,2]) )pv_
  int BoundaryMode2 {0};
  // pv_( autovector(label='X4', group_id=1).enumeration(items=['None', 'Wrap', 'Clamp'], values=[0,1,2]) )pv_
  int BoundaryMode3 {0};
  // pv_( group('Vector Field Parameters', 1, panel_visibility='advanced') )pv_

  prtlFTLE();
  ~prtlFTLE() override;

  int RequestInformation(
      vtkInformation* request,
      vtkInformationVector** inputVector,
      vtkInformationVector* outputVector ) override;

  int RequestUpdateExtent(vtkInformation *,
                          vtkInformationVector **,
                          vtkInformationVector *) override;

  int RequestData(vtkInformation *,
                  vtkInformationVector **,
                  vtkInformationVector *) override;

 private:

  prtlFTLE(const prtlFTLE &) = delete;
  void operator=(const prtlFTLE &) = delete;
};

#endif //LIBPRTL_VTK_PRTLFTLE_H
