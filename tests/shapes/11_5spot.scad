$fn=8;

difference() {
  offset(r=10) square([50, 50], center=true);
  difference() {
    square([50, 50], center=true);
    circle(d=7);
    for(xs=[1, -1], ys=[1,-1])
      scale([xs, ys])
      translate([12.5, 12.5]) circle(d=7);
  }
}
