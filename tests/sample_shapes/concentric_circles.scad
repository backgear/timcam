$fs=0.2;
$fa=1;
module somecir(n) {
    difference() {
        circle(d=n);
        if(n > 8) somecir(n-4);
    }
}

somecir(50);
