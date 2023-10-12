/*
Simple sobel-edge detector

names in "quotes" will be replaced by the corresponding module

*/

module "uid"(X00, X01, X02, X10, X11, X12, X20, X21, X22, Y);
    input [7:0] X00, X01, X02, X10, X11, X12, X20, X21, X22;
    output [10:0] Y;

    wire [8:0] oA1, oA3;
    wire [8:0] sX21, sX01;
    wire [9:0] oA2, oA4;

    //assign sX21 = X21 << 1;
    //assign sX01 = X01 << 1;
    // abc compatible notation
    assign sX21[8] = X21[7];
    assign sX21[7] = X21[6];
    assign sX21[6] = X21[5];
    assign sX21[5] = X21[4];
    assign sX21[4] = X21[3];
    assign sX21[3] = X21[2];
    assign sX21[2] = X21[1];
    assign sX21[1] = X21[0];
    assign sX21[0] = 1'b0;
    assign sX01[8] = X01[7];
    assign sX01[7] = X01[6];
    assign sX01[6] = X01[5];
    assign sX01[5] = X01[4];
    assign sX01[4] = X01[3];
    assign sX01[3] = X01[2];
    assign sX01[2] = X01[1];
    assign sX01[1] = X01[0];
    assign sX01[0] = 1'b0;
    
    "opAdd1" opAdd1(.A(X00), .B(X02), .Y(oA1));
    "opAdd2" opAdd2(.A(oA1), .B(sX01), .Y(oA2));
    "opAdd3" opAdd3(.A(X20), .B(X22), .Y(oA3));
    "opAdd4" opAdd4(.A(oA3), .B(sX21), .Y(oA4));
    "opSub" opSub1(.A(oA4), .B(oA2), .Y(Y));
endmodule