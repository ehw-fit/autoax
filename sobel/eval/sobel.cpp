/* 
Profiling application
Generates the distribution of input values of the components

not used in the project yet

*/
#include <cstdio>
#include <cstdlib> 
#include <iostream>
#include <ostream>
#include <cassert>
#include <cstdint>

#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv; 

template <class T1,class T2>
class saveClass {
private:
    int len;
    int * data;
    double * outputs;

    T1 lastA, lastB;

    T2 (*fn)(T1, T2);
public:
    saveClass(T2 (*fn)(T1, T2),  int len) {
        this->len = len;
        this->fn = fn;
        this->data = new int[len * len];
        memset(this->data, 0, sizeof(int) * len * len);

        this->outputs = NULL;
    }

    ~saveClass() {
        delete[] this->data;
    }

    void addOutput(double out) {
        if(!this->outputs) {
            this->outputs = new double[len * len];
            memset(this->outputs, 0, sizeof(double) * len * len);
        }

        this->data[(this->lastA * this->len) + this->lastB] += out;  
    }

    void addUse(T1 a, T1 b) {
        assert(a >= 0 && a < this->len);
        assert(b >= 0 && b < this->len);

        this->lastA = a;
        this->lastB = b;
        this->data[(a * this->len) + b]++;    
    }

    void saveData(const char * fname) {
        FILE * f = fopen(fname, "w");
        if(!f) {
            cerr << "Unable to write to " << fname << ": ";
            ferror(f);
            cerr << endl; 
            exit(1);            
        }

        fprintf(f, "[");
        for(int a = 0; a < this->len; a++) {
            if(a)
                fprintf(f, ",[");
            else
                fprintf(f, "[");

            for(int b = 0; b < this->len; b++) {
                if(b)
                    fprintf(f, ",");
                fprintf(f, "%d", this->data[(a * this->len) + b]);
            }
            fprintf(f, "]");
        }
        fprintf(f, "]");
        fclose(f);
    }

    void saveOutput(const char * fname) {
        if(this->outputs == NULL) {
            cerr << fname << ": no data are in the buffer; skipped" << endl;
            return;
        }

        FILE * f = fopen(fname, "w");
        if(!f) {
            cerr << "Unable to write to " << fname << ": ";
            ferror(f);
            cerr << endl; 
            exit(1);            
        }

        fprintf(f, "[");
        for(int a = 0; a < this->len; a++) {
            if(a)
                fprintf(f, ",[");
            else
                fprintf(f, "[");

            for(int b = 0; b < this->len; b++) {
                if(b)
                    fprintf(f, ",");
                if(this->data[(a * this->len) + b])
                    fprintf(f, "%g", this->outputs[(a * this->len) + b] / this->data[(a * this->len) + b]);
                else
                    fprintf(f, "NaN");
            }
            fprintf(f, "]");
        }
        fprintf(f, "]");
        fclose(f);
    }

    T2 operator () (const T1 a, const T2 b) {
        this->addUse(a, b);
        return this->fn(a, b);
    } 
};

static saveClass<int, int> opAdd1([](int a, int b) { return a + b; }, 256);
static saveClass<int, int> opAdd3([](int a, int b) { return a + b; }, 256);
static saveClass<int, int> opAdd2([](int a, int b) { return a + b; }, 512);
static saveClass<int, int> opAdd4([](int a, int b) { return a + b; }, 512);
static saveClass<int, int> opSub1([](int a, int b) { return b - a; }, 1024);


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
    if(m < 0) return 0;
    if(m > 255) return 255;
    return m;
}

int main(int argc, char ** argv) {
    if(argc < 2) {
        cerr << "Usage: " << argv[0] << " image1 [image2 image3 ...]" << endl; 
        exit(EXIT_FAILURE);
    }



    for(int imgid = 1; imgid < argc; imgid ++) {

        cout << "+ filtering " << argv[imgid] << endl;
        Mat A, C, D;                          // creates just the header parts
        A = imread(argv[imgid], IMREAD_COLOR); // here we'll know the method used (allocate matrix)

        cv::cvtColor(A, A, CV_8U);
        cv::cvtColor(A, A, CV_BGR2GRAY);

        C = A.clone();

        //imshow("image input", A);

        cout << "elem size "  << C.elemSize() << endl;
        cout << "chans "  << C.channels() << endl;


        assert(C.elemSize() == 1);
        for (int r = 0; r < C.rows; r++) {
            for (int c = 0; c < C.cols; c++) {
                //C.data[15 + i * C.cols] = 0;
                getMatData(C, r, c) =  
                    saturate(abs(
                        opSub1(
                            opAdd2(
                                opAdd1(
                                    getMatData(A, r-1, c-1),
                                    getMatData(A, r+1, c-1)
                                ),
                                2 * ((int)getMatData(A, r, c-1))
                            ),

                            opAdd4(
                                opAdd3(
                                    getMatData(A, r-1, c+1),
                                    getMatData(A, r+1, c+1)

                                ),
                                2 * (int)getMatData(A, r, c+1)
                            )
                        )

                    )
                    /*+
                    abs(
                        -getMatData(A, r-1, c-1) +
                        -2 * getMatData(A, r-1, c) +
                        -getMatData(A, r-1, c+1) +

                        getMatData(A, r+1, c-1) +
                        2 * getMatData(A, r+1, c) +
                        getMatData(A, r+1, c+1)
                    )*/

                    
                    
                    
                    )
                
                ;

                double out = getMatData(C, r, c);
                opAdd1.addOutput(out);
                opAdd2.addOutput(out);
                opAdd3.addOutput(out);
                opAdd4.addOutput(out);
                opSub1.addOutput(out);

                if(0 && imgid == 1)
                cout << (uint)saturate(abs(
                        -(int)getMatData(A, r-1, c-1) +
                        (int)getMatData(A, r-1, c+1) +

                        
                        -2 * (int)getMatData(A, r, c-1) +
                        2 *(int) getMatData(A, r, c+1) +

                        -(int)getMatData(A, r+1, c-1) +
                        (int)getMatData(A, r+1, c+1)
                    )
                    /*+
                    abs(
                        -getMatData(A, r-1, c-1) +
                        -2 * getMatData(A, r-1, c) +
                        -getMatData(A, r-1, c+1) +

                        getMatData(A, r+1, c-1) +
                        2 * getMatData(A, r+1, c) +
                        getMatData(A, r+1, c+1)
                    )*/
                )
                
                << " ... " << (uint)getMatData(C, r, c) << endl;
        
            }
        }


        if(1 && imgid == 1)
             {    
        D = A.clone();


    Mat kern = (Mat_<float>(3,3)<<-1,0,1,-2,0,2,-1,0,1);
    //cv::flip(kern,kern, -1);
    cv::filter2D(A, D,A.type(),kern);
        //Sobel(A, D, CV_8U, 0, 1);


        imshow("image input", A);
        imshow("image output CV", D);
        imshow("image output", C);
        waitKey(0); // Wait for a keystroke in the window
        }
    }

    opAdd1.saveData("prof/opAdd1.json");
    opAdd3.saveData("prof/opAdd3.json");
    opAdd2.saveData("prof/opAdd2.json");
    opAdd4.saveData("prof/opAdd4.json");
    opSub1.saveData("prof/opSub1.json"); 

    opAdd1.saveOutput("prof/opAdd1.outputs.json");
    opAdd3.saveOutput("prof/opAdd3.outputs.json");
    opAdd2.saveOutput("prof/opAdd2.outputs.json");
    opAdd4.saveOutput("prof/opAdd4.outputs.json");
    opSub1.saveOutput("prof/opSub1.outputs.json");

    return EXIT_SUCCESS;
}