difference() {
  offset(r=3,$fn=32) square([20,10]);
  offset(r=-2,$fn=32) offset(r=4,$fn=32) offset(delta=-2) polygon(points=[
    [0, 0],
    [20,0],
    [16,8],
    [10,5],
    [3,10],
  ]);
}
