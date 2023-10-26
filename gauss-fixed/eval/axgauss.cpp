#include <iostream>
#include <cstdlib>
#include <functional>
#include "lib.hpp"

#include "similarity.hpp"
#include "opcache.hpp"

#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv; 

static uint8_t & getMatData(Mat & m, int r, int c) {
    int mr = r;
    int mc = c;

    if(mr < 0) mr = 0;
    if(mr >= m.rows) mr = m.rows - 1;

    if(mc < 0) mc = 0;
    if(mc >= m.cols) mc = m.cols - 1;
    return m.data[mc + mr * m.cols];
}


static uint8_t saturate(int m) {
    m = m >> 8;
    return m;
    //cout << m <<endl;
    if(m < 0) return 0;
    if(m > 255) return 255;
    return m;
}

static int accurateSub(int a, int b) { return a - b; }
static int accurateAdd(int a, int b) { return a + b; }


int main(int argc, char ** argv) {
    
/*
parameters:
   * TXT list (csv) with 5 columns and configurations
   * images 1 to N

reads each line in the file, split names, gets file from the library
finds the functions
prefills tables

for the each image generates the right image

pass thru all images, get PSNR od the each filter



*/

    if(argc < 2) {
        cerr << "Usage: " << argv[0] << " image1 [image2 image3 ...]" << endl; 
        exit(EXIT_FAILURE);
    }

    /* Library of ax circuits */
    AxLibrary library;

    /* Preprocessing and accurat solutions */
    char ** imgNames = argv + 1;
    int imgCount = argc - 1;

    Mat * mInput = new Mat[imgCount];
    Mat * mAccurate = new Mat[imgCount];
    Mat * mRes = new Mat[imgCount];

    /* accurate functions */
    OpCache opAdd1(256, 256, accurateAdd);
    OpCache opAdd2(256, 256, accurateAdd);
    OpCache opAdd3(512, 512, accurateAdd);
    OpCache opAdd4(256, 256, accurateAdd);
    OpCache opAdd5(256, 256, accurateAdd);
    OpCache opAdd6(512, 512, accurateAdd);

    tOperation opAdd7 = accurateAdd;
    tOperation opAdd8 = accurateAdd;
    tOperation opAdd9 = accurateAdd;
    tOperation opAdd10 = accurateAdd;
    tOperation opSub1 = accurateSub;

    for(int imgid = 0; imgid < imgCount; imgid ++) {

        cout << "+ filtering " << imgid << ": " << imgNames[imgid] << endl;

        Mat & A = mInput[imgid];
        A = imread(imgNames[imgid], IMREAD_COLOR); // here we'll know the method used (allocate matrix)
        cv::cvtColor(A, A, CV_8U);
        cv::cvtColor(A, A, COLOR_BGR2GRAY);

        Mat & C = mAccurate[imgid];
        C = A.clone();
        mRes[imgid] = A.clone();


        assert(C.elemSize() == 1);
        for (int r = 0; r < C.rows; r++) {
            for (int c = 0; c < C.cols; c++) {
                auto a6 = opAdd6(
                            opAdd4(
                                getMatData(A, r-1, c),
                                getMatData(A, r+1, c)
                            ),
                            opAdd5(
                                getMatData(A, r, c-1),
                                getMatData(A, r, c+1)
                            )
                        );
                       
                getMatData(C, r, c) =  
                    saturate(abs(
                        opAdd10(
                            opAdd3(
                                opAdd1(
                                    getMatData(A, r-1, c-1),
                                    getMatData(A, r+1, c-1)
                                ),
                                opAdd2(
                                    getMatData(A, r-1, c+1),
                                    getMatData(A, r+1, c+1)
                                )
                            ) << 4,
                            opAdd9(
                                opSub1(
                                    a6 << 5,
                                    a6
                                ),

                                opAdd8(
                                    opAdd7(
                                        getMatData(A, r, c) << 5,
                                        getMatData(A, r, c)
                                    ) << 1,
                                    getMatData(A, r, c)
                                )
                            ) /* add9 */
                        ) /* add10 */

                    )
                    )
                
                ;
        
            }
        }

#if 0
        if(1 && imgid == 0)
        {    
            Mat D = A.clone();
            Mat kern = (Mat_<float>(3,3)<<-1,0,1,-2,0,2,-1,0,1);
            cv::flip(kern,kern, -1);
            cv::filter2D(A, D, A.type(),kern);
            //Sobel(A, D, CV_8U, 0, 1);

            imshow("image input", A);
            imshow("image output CV", D);
            imshow("image output", C);
            waitKey(0); // Wait for a keystroke in the window
        }
#endif
    }

    /* End of input generation */

    while(!cin.eof()) {
        string funname;
        cin >> funname;

        cout << funname << ";";

        auto selOps = library.GetFunction(funname);

        opAdd1.SetFunction(get<0>(selOps));
        opAdd2.SetFunction(get<1>(selOps));
        opAdd3.SetFunction(get<2>(selOps));
        opAdd4.SetFunction(get<3>(selOps));
        opAdd5.SetFunction(get<4>(selOps));
        opAdd6.SetFunction(get<5>(selOps));

        opAdd7 = get<6>(selOps);
        opAdd8 = get<7>(selOps);
        opAdd9 = get<8>(selOps);
        opAdd10 = get<9>(selOps);
        opSub1 = get<10>(selOps);

        double sumSSIM = 0;
        double sumPSNR = 0;

        for(int imgid = 0; imgid < imgCount; imgid ++) {
            Mat & A = mInput[imgid];
            Mat & C = mRes[imgid];

            for (int r = 0; r < C.rows; r++) {
                for (int c = 0; c < C.cols; c++) {
                    auto a6 = opAdd6(
                            opAdd4(
                                getMatData(A, r-1, c),
                                getMatData(A, r+1, c)
                            ),
                            opAdd5(
                                getMatData(A, r, c-1),
                                getMatData(A, r, c+1)
                            )
                        );
                       
                getMatData(C, r, c) =  
                    saturate(abs(
                        opAdd10(
                            opAdd3(
                                opAdd1(
                                    getMatData(A, r-1, c-1),
                                    getMatData(A, r+1, c-1)
                                ),
                                opAdd2(
                                    getMatData(A, r-1, c+1),
                                    getMatData(A, r+1, c+1)
                                )
                            ) << 4,
                            opAdd9(
                                opSub1(
                                    a6 << 5,
                                    a6
                                ),

                                opAdd8(
                                    opAdd7(
                                        getMatData(A, r, c) << 5,
                                        getMatData(A, r, c)
                                    ) << 1,
                                    getMatData(A, r, c)
                                )
                            ) /* add9 */
                        ) /* add10 */

                    )
                    )
                
                ;
            
                }
            }

            double iSSIM = getMSSIM(mAccurate[imgid], mRes[imgid])[0];
            double iPSNR = getPSNR(mAccurate[imgid], mRes[imgid]);
            cout << ";PSNR[" << imgid << "]=" << iPSNR;
            cout << ";SSIM[" << imgid << "]=" << iSSIM;

            
            sumSSIM += iSSIM;
            sumPSNR += iPSNR;
        } /* All images */
        cout << ";PSNR_AVG=" << sumPSNR / imgCount;
        cout << ";SSIM_AVG=" << sumSSIM / imgCount;
        cout << endl;
    } /* cin eof */
}