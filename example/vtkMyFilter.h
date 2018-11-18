#ifndef MINIMAL_H
#define MINIMAL_H

#include <vtkAlgorithm.h>

// pv_( filter(name='Minimal', label='Minimal Filter Example') )pv_
class vtkMinimal : public vtkAlgorithm {
public:
	vtkSetMacro(MemberA, int);
	vtkSetMacro(MemberB, int);

protected:
	class ForwardClass;

	// pv_( intvector(label='A') )pv_
	int MemberA = 1;

	// pv_( autovector() )pv_
	int MemberB {2};

	// pv_( intvector() )pv_
	int MemberC[2] {1,2};

	// pv_( autovector() )pv_
	double MemberD[2] = {3, 4};

	char* str1 {nullptr};

	// pv_( autovector() )pv_
	bool MemberE = true;
};

#endif
