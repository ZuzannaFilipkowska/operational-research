# Definicja zbior w
set I;  # Zbi r pracownik w
set J;  # Zbi r projekt w
set P;  # Zbi r stanowisk
set K;  # Zbi r kompetencji
set Groups; # Grupy pracowników które pracują wspólnie

# Parametry
param R {J, P} integer;  # Liczba os b wymaganych na stanowisku p w projekcie j
param S {J} integer;        # Zysk z projektu j
param K_i {I} integer;      # Koszt zatrudnienia pracownika i
param P_i {I} binary;    # Wska nik (0 - sta y, 1 - kontrakt)
param GroupMembers {Groups, I} binary;  # Przypisanie pracowników do grup
# Definiowanie du ej liczby M
param M := 100000;
param D {I, P} binary;


# Zmienne decyzyjne
var x {J} binary;               # 1, je li projekt j jest realizowany, 0 - je li nie
var y {I, P, J} binary;         # 1, je li pracownik i jest przypisany do stanowiska p w projekcie j
var is_qualified {I, P, K} binary;  # 1, je li pracownik i spe nia wymagania kompetencyjne na stanowisku p dla kompetencji k

var group_in_project {Groups, J} binary;
var groupmembers_count {Groups, J} integer;
var groupmembers_in_project {Groups, J} integer;
var b {Groups, J} binary;
# Funkcja celu: maksymalizacja zysku
maximize TotalProfit:
    sum {j in J} S[j] * x[j]  - 
    sum {i in I} K_i[i] * (P_i[i] * sum {j in J, p in P} y[i,p,j] + (1 - P_i[i]));

# Ograniczenia

# 3. Ka dy projekt wymaga odpowiedniej liczby os b na stanowiskach
s.t. coverage_check {p in P, j in J}:
    sum {i in I} y[i,p,j] >= R[j,p] * x[j];

# 4. Pracownik mo e pracowa  tylko na jednym stanowisku w jednym projekcie
# OK
s.t. worker_assignment_limit {i in I}:
    sum {p in P, j in J} y[i,p,j] <= 1;

# 5. Pracownik mo e by  przypisany do projektu tylko wtedy, gdy projekt jest realizowany
s.t. project_assignment {i in I, j in J}:
    sum {p in P} y[i,p,j] <= x[j];

# 6. Pracownik może zostać przypisany do stanowiska tylko wtedy, gdy jest na nie kwalifikowany
s.t. assignment_qualification_check {i in I, p in P, j in J}:
    y[i,p,j] <= D[i,p];

# If b[g,j] = 0, then groupmembers_in_project[g,j] = 0
s.t. zero_if_not_assigned {g in Groups, j in J}:
    groupmembers_in_project[g,j] <= M * b[g,j];

# If b[g,j] = 1, then groupmembers_in_project[g,j] must be >= 1
s.t. greater_than_zero_if_assigned {g in Groups, j in J}:
    groupmembers_in_project[g,j] >= 1 * b[g,j];
    
s.t. workers_together_project1 {g in Groups, j in J}:
    groupmembers_in_project[g,j] = sum {p in P, i in I: GroupMembers[g,i] == 1} y[i, p, j];
     
s.t. workers_together_project2 {g in Groups, j in J}:
     groupmembers_count[g,j] = sum {i in I} GroupMembers[g,i];
     
s.t. workers_together_project {g in Groups, j in J}:
   groupmembers_in_project[g,j] >= groupmembers_count[g,j] * b[g,j];
