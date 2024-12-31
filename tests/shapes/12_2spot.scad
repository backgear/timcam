$fn=8;

difference() {
  offset(r=10) square([50, 50], center=true);
  difference() {
    square([50, 50], center=true);
    for(s=[[1,1], [-1, -1]])
      scale(s)
      translate([12.5, 12.5]) circle(d=7);
  }
}

