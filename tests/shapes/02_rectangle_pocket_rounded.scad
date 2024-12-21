$fn=32;
difference() {
  square([20,10]);
  offset(r=2) offset(delta=-4) square([20,10]);
}
