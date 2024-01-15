#include <iostream>
#include <cstdlib>
#include <functional>

#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

double getPSNR(const Mat& I1, const Mat& I2);
Scalar getMSSIM( const Mat& i1, const Mat& i2);