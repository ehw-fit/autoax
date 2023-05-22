module "uid"(x0, x1, x2, x3, y0, y1, y2, y3);
	input [7:0]x0;
	input [7:0]x1;
	input [7:0]x2;
	input [7:0]x3;
	output [15:0]y0;
	output [15:0]y1;
	output [15:0]y2;
	output [15:0]y3;
	
	wire [8:0]a0;
	wire [8:0]a1;
	wire [8:0]b0;
	wire [8:0]b1;
	wire [9:0]y0p;
	wire [9:0]y2p;
	
    //cout << "x:" << x[0] <<","<< x[1] << "," << x[2] << "," << x[3] << endl;
    "dct_add1"(.Y(a0), .A(x0), .B(x3));
    "dct_add2"(.Y(a1), .A(x1), .B(x2));
    "dct_sub1"(.Y(b0), .A(x0), .B(x3));
    "dct_sub2"(.Y(b1), .A(x1), .B(x2));

    "dct_add3"(.Y(y0p), .A(a0), .B(a1));
    "dct_sub3"(.Y(y2p), .A(a0), .B(a1));
	assign y0[0] = 1'b0;
	assign y0[1] = 1'b0;
	assign y0[2] = 1'b0;
	assign y0[3] = 1'b0;
	assign y0[4] = 1'b0;
	assign y0[5] = 1'b0;
	assign y0[6] = y0p[0];
	assign y0[7] = y0p[1];
	assign y0[8] = y0p[2];
	assign y0[9] = y0p[3];
	assign y0[10] = y0p[4];
	assign y0[11] = y0p[5];
	assign y0[12] = y0p[6];
	assign y0[13] = y0p[7];
	assign y0[14] = y0p[8];
	assign y0[15] = y0p[9];
	
	assign y2[0] = 1'b0;
	assign y2[1] = 1'b0;
	assign y2[2] = 1'b0;
	assign y2[3] = 1'b0;
	assign y2[4] = 1'b0;
	assign y2[5] = 1'b0;
	assign y2[6] = y2p[0];
	assign y2[7] = y2p[1];
	assign y2[8] = y2p[2];
	assign y2[9] = y2p[3];
	assign y2[10] = y2p[4];
	assign y2[11] = y2p[5];
	assign y2[12] = y2p[6];
	assign y2[13] = y2p[7];
	assign y2[14] = y2p[8];
	assign y2[15] = y2p[9];

    mcm_c2_"uid"(.b0(b0), .b1(b1), .y1(y1), .y3(y3));
endmodule

module mcm_c2_"uid"(b0, b1, y1, y3);
	input [8:0]b0;
	input [8:0]b1;
	output [15:0]y1;
	output [15:0]y3;
	
	wire [12:0]b0_36;
	wire [12:0]b1_36;
	wire [11:0]b0_80;
	wire [11:0]b1_80;
	
	wire [13:0]y1p;
	wire [13:0]y3p;
	
	
	"c2_add1"(.Y(b0_36), .A({b0, 3'b000}), .B(b0));
    "c2_add2"(.Y(b0_80), .A({b0, 2'b00 }), .B(b0));
    "c2_add3"(.Y(b1_36), .A({b1, 3'b000}), .B(b1));
    "c2_add4"(.Y(b1_80), .A({b1, 2'b00 }), .B(b1));

    "c2_add5"(.Y(y1p), .A(b1_36), .B({b0_80, 2'b00}));
    "c2_sub1"(.Y(y3p), .A(b0_36), .B({b1_80, 2'b00}));
	
	assign y1[0] = 1'b0;
	assign y1[1] = 1'b0;
	assign y1[2] = y1p[0];
	assign y1[3] = y1p[1];
	assign y1[4] = y1p[2];
	assign y1[5] = y1p[3];
	assign y1[6] = y1p[4];
	assign y1[7] = y1p[5];
	assign y1[8] = y1p[6];
	assign y1[9] = y1p[7];
	assign y1[10] = y1p[8];
	assign y1[11] = y1p[9];
	assign y1[12] = y1p[10];
	assign y1[13] = y1p[11];
	assign y1[14] = y1p[12];
	assign y1[15] = y1p[13];

	assign y3[0] = 1'b0;
	assign y3[1] = 1'b0;
	assign y3[2] = y3p[0];
	assign y3[3] = y3p[1];
	assign y3[4] = y3p[2];
	assign y3[5] = y3p[3];
	assign y3[6] = y3p[4];
	assign y3[7] = y3p[5];
	assign y3[8] = y3p[6];
	assign y3[9] = y3p[7];
	assign y3[10] = y3p[8];
	assign y3[11] = y3p[9];
	assign y3[12] = y3p[10];
	assign y3[13] = y3p[11];
	assign y3[14] = y3p[12];
	assign y3[15] = y3p[13];
endmodule


