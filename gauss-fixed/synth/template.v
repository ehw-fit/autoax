/*
Fixed gauss filter as in autoax paper

names in "quotes" will be replaced by the corresponding module

*/

module "uid"(X00, X01, X02, X10, X11, X12, X20, X21, X22, Y);
    input [7:0] X00, X01, X02, X10, X11, X12, X20, X21, X22;
    output [15:0] Y;

    wire [8:0] oA1, oA2, oA4, oA5;
    wire [9:0] oA3, oA6;
    wire [16:0] oA7, oA8, oA9, oA10, oS1;
    wire [16:0] iaA7, iaA8, iaA10, iaS1;

    "opAdd1" opAdd1(X00, X02, oA1);
    "opAdd2" opAdd2(X20, X22, oA2);
    "opAdd3" opAdd3(oA1, oA2, oA3);
    assign iaA10 = oA3 << 4;

    "opAdd4" opAdd4(X01, X21, oA4);
    "opAdd5" opAdd5(X10, X12, oA5);
    "opAdd6" opAdd6(oA4, oA5, oA6);
    assign iaS1 = oA6 << 5;
    "opSub1" opSub1(iaS1[15:0], {6'b000000,  oA6}, oS1);

    assign iaA7 = X11 << 5;
    "opAdd7" opAdd7(iaA7[15:0], {8'b0, X11}, oA7);
    assign iaA8 = oA7 << 1;
    "opAdd8" opAdd8(iaA8[15:0], {8'b0, X11}, oA8);


    "opAdd9" opAdd9(oS1[15:0], oA7[15:0], oA9);
    "opAdd10" opAdd10(iaA10[15:0], oA9[15:0], oA10);
    assign Y = oA10[15:0];
endmodule

