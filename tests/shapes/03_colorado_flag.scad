$fn=32;

difference() {
  square([20,10]);
  translate([10,5]) circle(d=4.5);
  difference() {
    translate([10,5]) circle(d=8);
    translate([10,5]) rotate([0,0,-45]) square([10,10]);
    translate([10,5]) circle(d=4.6);
  }
}
