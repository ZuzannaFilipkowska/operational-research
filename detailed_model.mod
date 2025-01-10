set I; 
set R; 
set E within I cross I; 
 
param p{I} > 0 integer; 
param d{I,R} >= 0 integer; 
param D{R} > 0 integer; 
param H > 0 integer; 
 
set T := 0..H; 
 
var s{I} >= 0; 
var Cmax >= 0; 
var x{I,T} binary; # Czy zadanie I jest aktywne w czasie T
 
minimize ObjectiveFunction: Cmax; 
 
subject to Precedence {(i,j) in E}: 
    s[i] + p[i] <= s[j]; 
 
 # Ograniczenia zasobów w każdym momencie czasu
subject to ResourceConstraints {t in T, r in R}: 
    (sum{i in I} d[i,r] * x[i,t]) <= D[r]; 
 
subject to ProjectCompletion {i in I}: 
    s[i] + p[i] <= Cmax; 
 
subject to TaskActivityStart {i in I, t in T}: 
    s[i] <= t + H * (1 - x[i,t]); 
 
subject to TaskActivityEnd {i in I, t in T}: 
    t + 1 <= s[i] + p[i] + H * (1 - x[i,t]); 
 
subject to TaskActivityConsistency {i in I}: 
    sum{t in T} x[i,t] = p[i]; 
 
subject to CmaxDefinition: 
    Cmax <= H; 