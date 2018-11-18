#ifndef LIBPRTL_VTK_PRTLEIGENVECTORS_H_
#define LIBPRTL_VTK_PRTLEIGENVECTORS_H_

#include "prtl_vtk_export.h"
#include <vtkDataObjectAlgorithm.h>

/* pv_(
    filter(name='Eigenvectors').menu('prtl') \
    .input(data_types='vtkDataObject', label='Input Field') \
      .array_domain(optional=True) \
    .input(data_types='vtkPointSet', name='InputPoints', label='Input Points', port_index=1) \
    .input_array(label='Vectors', none_string='No data')
   )pv_ */
class PRTL_VTK_EXPORT prtlEigenvectors : public vtkDataObjectAlgorithm {
 public:
  static prtlEigenvectors *New();
  vtkTypeMacro(prtlEigenvectors, vtkDataObjectAlgorithm);

  vtkSetMacro(AnalyticalStep, double);
  vtkGetMacro(AnalyticalStep, double);

 protected:
  // pv_( autovector(label='Step Width for Analytical Input') )pv_
  double AnalyticalStep {0.1};

  prtlEigenvectors();
  ~prtlEigenvectors() override;

  int FillInputPortInformation(int port, vtkInformation* info) override;
  int FillOutputPortInformation(int port, vtkInformation* info) override;

  int RequestInformation(
      vtkInformation* request,
      vtkInformationVector** inputVector,
      vtkInformationVector* outputVector) override;

  int RequestUpdateExtent(
      vtkInformation* request,
      vtkInformationVector** inputVector,
      vtkInformationVector* outputVector) override;

  int RequestDataObject(
      vtkInformation* request,
      vtkInformationVector** inputVector,
      vtkInformationVector* outputVector) override;

  int RequestData(
      vtkInformation* request,
      vtkInformationVector** inputVector,
      vtkInformationVector* outputVector) override;

 private:
  prtlEigenvectors(const prtlEigenvectors&); // Not implemented.
  void operator=(const prtlEigenvectors&); // Not implemented.
};

#endif //LIBPRTL_PRTLEIGENVECTORS_H_
