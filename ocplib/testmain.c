/*
 * Testing Function for LocateCube
 * Usage: 	1 - Naive Implementation
 */ 		 	

#include<stdio.h>
#include<stdint.h>
#include<stdlib.h>
#include<ocpcalib.h>

void main()
{
  int xyz[3] = {134,24,11};
  uint32_t locs[2][4] = { {1,2,3,4},{22,23,24,25} };
  uint32_t locations[3][3] = { {4,5,6},{7,8,9},{10,11,12} };
  int dims[3] = { 1,1,1 };

  int index = XYZMorton( xyz );
  int * xyz2;
  xyz2 = malloc(sizeof(int)*3) ;
  MortonXYZ ( index, xyz2 );
  //locateCube(locs, 2, locations, 3, dims );

  int i;

  for ( i=0; i<3; i++)
    printf("%d,",xyz2[i]);

  //for( i = 0; i<2; i++ )
    //printf("%d,%d,%d,%d\n",locs[i][0], locs[i][1], locs[i][2], locs[i][3]);


  printf("%d", index);
  
}
