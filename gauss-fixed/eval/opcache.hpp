#include <functional>

using namespace std;
class OpCache {
private:
    int * cache;
    int inA, inB;
public:
    OpCache(int inA, int inB, function<int(int, int)> fn = NULL) {
        this->inA = inA;
        this->inB = inB;
        cache=new int[inA * inB];
        if(fn != NULL)
            SetFunction(fn);
    }

    ~OpCache() {
        if(cache != NULL)
            delete[] cache;
    }

    void SetFunction(function<int(int, int)> fn) {
        for(int a = 0; a < inA; a++) {
            for(int b = 0; b < inB; b++) {
                cache[a * inB + b] = fn(a, b);
            }
        }
    }

    int operator()  (const int a, const int b) {
        //return a + b;
        //assert(a < inA && b < inB);
        return cache[a * inB + b];
    }

};