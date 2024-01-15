#include "lib.hpp"
#include <string>
#include <cstdlib>
#include <iostream>

extern "C" {
    #include <add8.h>
    #include <add9.h>
    #include <add16.h>
    #include <sub16.h>
}

using namespace std;

static int accurateSub(int a, int b) { return a - b; }
static int accurateAdd(int a, int b) { return a + b; }

AxLibrary::AxLibrary() { 
    ops[""] = make_tuple(accurateAdd, accurateAdd, accurateAdd, accurateAdd, accurateAdd, accurateAdd, accurateAdd, accurateAdd, accurateAdd, accurateAdd, accurateSub);
    #include "lib_tuples.cpp" 
    //ops["op1"] = make_tuple(accurateAdd, accurateAdd, accurateAdd, accurateAdd, accurateAdd, accurateSub);
}

tOp11 AxLibrary::GetFunction(string name) { 
    //cout << "Searching for \"" << name << "\"" << endl;
    auto op = ops.find(name);
    if(op == ops.end()) {
        cerr << "Operation " << name << " not found in the library" << endl;
        exit(1);
    }
    
    return op->second;


}