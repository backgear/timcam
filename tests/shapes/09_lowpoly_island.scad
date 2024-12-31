difference() {
  square([90, 50]);
  difference() {
    offset(delta=-5) square([90, 50]);
    translate([90, 50]) scale([2, 1]) circle(d=50, $fn=16);
    translate([25, 25]) circle(d=14, $fn=4);
  }
}
