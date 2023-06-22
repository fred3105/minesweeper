import time 
import numpy as np
import random as rd

def statistiques_resolution(taille,Nbr_de_mines,taille_de_l_echantillon):
    L_tour = [0 for i in range(0,taille*taille)]
    L_tour_defaite = [0 for i in range(0,taille*taille)]
    time_debut = time.time()
    aboutie = 0
    non_aboutie = 0
    erreur = 0
    partie_perdue = 0
    bombe = 0
    
    for i in range(taille_de_l_echantillon):
        #print(i)
        resultat,T = jouer_machine_plus_max(jeu_ordi,check_logique_elementaire,taille,Nbr_de_mines)
        if resultat == "non aboutie":
            non_aboutie += 1
        elif resultat == "grille resolue" :
            aboutie += 1
        elif resultat == "Partie perdu":
            partie_perdue+= 1
        elif resultat == "Bombe":
            #print (resultat)
            bombe += 1
        else:
            return "Erreur dans stats"

        L_tour[T-1] += 1
        if resultat == "Partie perdu":
            L_tour_defaite[T-1] += 1
            
    time_fin = time.time()
    temps_ecoule = time_fin - time_debut
    
    if temps_ecoule > 60:
        mins = int(temps_ecoule/60)
        secondes = temps_ecoule - mins*60
    else:
        mins = 0
        secondes = temps_ecoule 
        
    secondes = float(int(secondes*100))/100
    pourcentage = (float(aboutie)/float(aboutie + partie_perdue))
    rounded_pourcentage = float(int(pourcentage*10000))/100
    
    inv_racine = 1/(taille_de_l_echantillon**0.5)
    
    interv_min = pourcentage - inv_racine
    interv_max = pourcentage + inv_racine
    
    print(rounded_pourcentage,"pourcentage de reussite", "realise en ", mins,"minutes",secondes, "secondes")
    print("intervalle de confiance", float(int(interv_min*10000))/100,float(int(interv_max*10000))/100)
    #print (non_aboutie)
    #print (partie_perdue)
    #print(L_tour)
    #print(L_tour_defaite)
    return("Termine")

def jouer_machine_plus_max(jeu_ordi,check_logique_elementaire,taille,nbr_mines):
    tour = 0
    drapeaux_places = 0
    mort = False
    X_a_jouer = []
    Y_a_jouer = []
    Bloque = False
    Termine = False
    Nbr_de_repetition = 0
    anienne_liste = []
    liste_actuelle = [1] 
    fin = False
    L,M,casesconnues = setupgrille(taille,nbr_mines,int(taille/2),int(taille/2))
    info_donnee_au_joueur = np.array([['X' for h in range(taille)]for k in range(taille)])
    update_info(info_donnee_au_joueur,casesconnues,M,taille)
    Xc,Yc = check_logique_elementaire(info_donnee_au_joueur)
    X_a_jouer,Y_a_jouer = compteur_drapeau(X_a_jouer,Y_a_jouer,info_donnee_au_joueur,taille)
    
    while (not Termine): # ou mettre fin == False and Nbre_de_boucles <= 40
        if not(fin == False and Nbr_de_repetition < 4):
            bloque = True
            #On sauve les meubles en jouant au hasard, a modifier a l'avenir
            a,b=maxindice(poids(info_donnee_au_joueur),info_donnee_au_joueur)
            #print("un coup va etre joué au hasard")
            #print(a,b)
            #print(info_donnee_au_joueur)
            mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'oui',a,b)
            tour += 1
            #print("apres coup au hasard")
            #print (info_donnee_au_joueur)
            if mort == True:
                return("Partie perdu",tour)
            else:
                #print ("allelluia")
                bloque = False
                Nbr_de_repetition = 0

        ancienne_liste = liste_actuelle
        for i in range(len(Xc)):
            for g in [-1,0,1]:
                for h in [-1,0,1]:
                    if valide(L,Xc[i]+ h, Yc[i] +g) == True and info_donnee_au_joueur[Xc[i]+ h][Yc[i] +g] == 'X':
                        mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'oui',Xc[i]+h,Yc[i]+g,)
                        tour += 1
                        if mort == True:
                            return("Partie perdu",tour)
                        #print(Xc[i]+h,Yc[i]+g,)
                        drapeaux_places += 1
                        #print(info_donnee_au_joueur)
                        
        for j in range(len(X_a_jouer)):
            for g in [-1,0,1]:
                for h in [-1,0,1]:
                    if valide(L,X_a_jouer[j]+h,Y_a_jouer[j]+g) == True and info_donnee_au_joueur[X_a_jouer[j]+ h][Y_a_jouer[j] +g] == 'X':
                        mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'non',X_a_jouer[j]+h,Y_a_jouer[j]+g)
                        tour += 1
                        if mort == True:
                            return("Partie perdu",tour)
                        #print(X_a_jouer[j]+h,Y_a_jouer[j]+g)
                        #print(info_donnee_au_joueur)

    
        #print(X_a_jouer,Xc)
        X_a_jouer = []
        Y_a_jouer = []
        X_a_jouer,Y_a_jouer = compteur_drapeau(X_a_jouer,Y_a_jouer,info_donnee_au_joueur,taille)
        
        Xc,Yc = check_logique_elementaire(info_donnee_au_joueur)
        
        if drapeaux_places == nbr_mines:
            for i in range(taille):
                for j in range(taille):
                    if info_donnee_au_joueur[i][j] == 'X':
                        mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'non',i,j)
                        tour += 1
                        #print(info_donnee_au_joueur)
                        
        liste_actuelle = X_a_jouer
        if liste_actuelle == ancienne_liste:
            Nbr_de_repetition += 1
        #print(info_donnee_au_joueur)

        if fin == True and mort == False:
            Termine = True
        elif fin == True and mort == True:
            return("Bombe",tour)
        
    if fin == False:
        #print(info_donnee_au_joueur)
        return("non aboutie",tour)
    else:
        return("grille resolue",tour)

def valide(L,i,j):
    if i >= 0 and i < len(L) and j>=0 and j < len(L):
        return True
    return False

def rajouter_cases_interessantes(info_donnee,Xc,Yc):# une case avec un chiffre
    for i in range(len(info_donnee)):
        for j in range(len(info_donnee)):
            if info_donnee[i][j] == '0' or info_donnee[i][j]=='f' or info_donnee[i][j]=='X':
                continue
            else:
                Xc = Xc + [i]
                Yc = Yc + [j]
    return(Xc,Yc)

def compteur_drapeau(X_a_jouer,Y_a_jouer,info_donnee,taille):
    X_compteur = []
    Y_compteur = []
    (X_compteur,Y_compteur) = rajouter_cases_interessantes(info_donnee,X_compteur,Y_compteur)
    for i in range(len(X_compteur)):
        compteur = 0
        drapeaux = 0
        for h in [-1,0,1]:
            for g in [-1,0,1]:
                if valide(info_donnee,X_compteur[i]+h,Y_compteur[i]+g):
                    if info_donnee[X_compteur[i]+h][Y_compteur[i]+g] == 'X':
                       compteur = compteur + 1
                    if info_donnee[X_compteur[i]+h][Y_compteur[i]+g] == 'f':
                        drapeaux += 1
              
        if drapeaux == int(info_donnee[X_compteur[i]][Y_compteur[i]]):
            X_a_jouer = X_a_jouer + [X_compteur[i]]
            Y_a_jouer = Y_a_jouer + [Y_compteur[i]]
            
    return(X_a_jouer,Y_a_jouer)
                   
                    

def check_logique_elementaire(info_donnee):
    Xc = []
    Yc = []
    cases_a_drapeaux_X = []
    cases_a_drapeaux_Y = []
    Xc,Yc = rajouter_cases_interessantes(info_donnee,Xc,Yc)
    for i in range(len(Xc)):
        compteur = 0
        for k in [-1,0,1]:
            for h in [-1,0,1]:
                if valide(info_donnee,Xc[i]+h,Yc[i]+k):
                    if info_donnee[Xc[i]+h][Yc[i]+k] == 'X' or info_donnee[Xc[i]+h][Yc[i]+k] == 'f':
                        compteur = 1 + compteur

        if compteur == int(info_donnee[Xc[i]][Yc[i]]) :
            cases_a_drapeaux_X = cases_a_drapeaux_X + [Xc[i]]
            cases_a_drapeaux_Y = cases_a_drapeaux_Y + [Yc[i]]
            
    return (cases_a_drapeaux_X,cases_a_drapeaux_Y)

def resoudre_alea(info_donnee_au_joueur,taille):
    Lix = []
    Liy = []
    for i in range(taille):
        for j in range(taille):
            if info_donnee_au_joueur[i][j] == 'X':
                Lix = Lix + [i]
                Liy = Liy + [j]
    a = rd.randint(0,len(Liy)-1)
    return(Lix[a],Liy[a])

# Trouver une condition de terminaison pour le while 
def jouer_machine(jeu_ordi,check_logique_elementaire,taille,nbr_mines):
    drapeaux_places = 0
    mort = False
    X_a_jouer = []
    Y_a_jouer = []
    Bloque = False
    Termine = False
    Nbr_de_repetition = 0
    anienne_liste = []
    liste_actuelle = [1] 
    fin = False
    L,M,casesconnues = setupgrille(taille,nbr_mines,int(taille/2),int(taille/2))
    info_donnee_au_joueur = np.array([['X' for h in range(taille)]for k in range(taille)])
    update_info(info_donnee_au_joueur,casesconnues,M,taille)
    Xc,Yc = check_logique_elementaire(info_donnee_au_joueur)
    X_a_jouer,Y_a_jouer = compteur_drapeau(X_a_jouer,Y_a_jouer,info_donnee_au_joueur,taille)
    
    while (not Termine): # ou mettre fin == False and Nbre_de_boucles <= 40
        if not(fin == False and Nbr_de_repetition < 4):
            bloque = True
            #On sauve les meubles en jouant au hasard, a modifier a l'avenir
            #print("un coup a ete joue au hasard")
            Lx = []
            Ly = []
            for i in range(taille):
                for j in range(taille):
                    if info_donnee_au_joueur[i][j] == 'X':
                        Lx += [i]
                        Ly += [j]
            a = rd.randint(0,len(Lx)-1)
            mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'non',Lx[a],Ly[a])
            print (info_donnee_au_joueur)
            #print (Lx[a],Ly[a])
            #alea jacta est
            if mort == True:
                return "Partie perdu"
            else:
            #    print "allelluia"
                bloque = False
                Nbr_de_repetition = 0
                
        ancienne_liste = liste_actuelle
        for i in range(len(Xc)):
            for g in [-1,0,1]:
                for h in [-1,0,1]:
                    if valide(L,Xc[i]+ h, Yc[i] +g) == True and info_donnee_au_joueur[Xc[i]+ h][Yc[i] +g] == 'X':
                        mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'oui',Xc[i]+h,Yc[i]+g,)
                        drapeaux_places += 1
                        #print(info_donnee_au_joueur)
        X_a_jouer = []
        Y_a_jouer = []
        X_a_jouer,Y_a_jouer = compteur_drapeau(X_a_jouer,Y_a_jouer,info_donnee_au_joueur,taille)
        
        Xc,Yc = check_logique_elementaire(info_donnee_au_joueur)
        
        if drapeaux_places == nbr_mines:
            for i in range(taille):
                for j in range(taille):
                    if info_donnee_au_joueur[i][j] == 'X':
                        mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'non',i,j)
                        
        liste_actuelle = X_a_jouer
        if liste_actuelle == ancienne_liste:
            Nbr_de_repetition += 1
        #print(info_donnee_au_joueur)

        if fin == True and mort == False:
            Termine = True
        elif fin == True and mort == True:
            return "ERREUR"
        
    if fin == False:
        #print(info_donnee_au_joueur)
        return("non aboutie")
    else:
        return("grille resolue")


def jouer_machine_plus(jeu_ordi,check_logique_elementaire,taille,nbr_mines):
    drapeaux_places = 0
    mort = False
    X_a_jouer = []
    Y_a_jouer = []
    Bloque = False
    Termine = False
    Nbr_de_repetition = 0
    anienne_liste = []
    liste_actuelle = [1] 
    fin = False
    L,M,casesconnues = setupgrille(taille,nbr_mines,int(taille/2),int(taille/2))
    info_donnee_au_joueur = np.array([['X' for h in range(taille)]for k in range(taille)])
    update_info(info_donnee_au_joueur,casesconnues,M,taille)
    Xc,Yc = check_logique_elementaire(info_donnee_au_joueur)
    X_a_jouer,Y_a_jouer = compteur_drapeau(X_a_jouer,Y_a_jouer,info_donnee_au_joueur,taille)
    
    while (not Termine): # ou mettre fin == False and Nbre_de_boucles <= 40
        if not(fin == False and Nbr_de_repetition < 4):
            bloque = True
            #On sauve les meubles en jouant au hasard, a modifier a l'avenir
            #print("un coup a ete joue au hasard")
            a,b=minindice(poids(info_donnee_au_joueur),info_donnee_au_joueur)
            #print(a,b)
            mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'non',a,b)
            #print (info_donnee_au_joueur)
            #print ("alea jacta est")
            if mort == True:
                return "Partie perdu"
            else:
                #print ("allelluia")
                bloque = False
                Nbr_de_repetition = 0
                
        ancienne_liste = liste_actuelle
        for i in range(len(Xc)):
            for g in [-1,0,1]:
                for h in [-1,0,1]:
                    if valide(L,Xc[i]+ h, Yc[i] +g) == True and info_donnee_au_joueur[Xc[i]+ h][Yc[i] +g] == 'X':
                        mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'oui',Xc[i]+h,Yc[i]+g,)
                        drapeaux_places += 1
                        #print(info_donnee_au_joueur)
                        
        for j in range(len(X_a_jouer)):
            for g in [-1,0,1]:
                for h in [-1,0,1]:
                    if valide(L,X_a_jouer[j]+h,Y_a_jouer[j]+g) == True and info_donnee_au_joueur[X_a_jouer[j]+ h][Y_a_jouer[j] +g] == 'X':
                        mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'non',X_a_jouer[j]+h,Y_a_jouer[j]+g)
                        #print(info_donnee_au_joueur) 

        X_a_jouer = []
        Y_a_jouer = []
        X_a_jouer,Y_a_jouer = compteur_drapeau(X_a_jouer,Y_a_jouer,info_donnee_au_joueur,taille)
        
        Xc,Yc = check_logique_elementaire(info_donnee_au_joueur)
        
        if drapeaux_places == nbr_mines:
            for i in range(taille):
                for j in range(taille):
                    if info_donnee_au_joueur[i][j] == 'X':
                        mort,casesconnues,info_donnee_au_joueur,fin = jeu_ordi(L,M,casesconnues,info_donnee_au_joueur,taille, 'non',i,j)
                        
        liste_actuelle = X_a_jouer
        if liste_actuelle == ancienne_liste:
            Nbr_de_repetition += 1
        #print(info_donnee_au_joueur)

        if fin == True and mort == False:
            Termine = True
        elif fin == True and mort == True:
            return "ERREUR"
        
    if fin == False:
        #print(info_donnee_au_joueur)
        return("non aboutie")
    else:
        return("grille resolue")
        
def jeu_ordi(L, M, casesconnues, info_donnee_au_joueur,taille, d, i, j):
    mort = False
    fin = False 
    info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin,mort = faire_un_coup(info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin,mort)
    revele(M,i,j,casesconnues)
    update_info(info_donnee_au_joueur,casesconnues,M,taille)
    bombes = 0
    points = 0
    remplie = True
    for s in range(taille):
        for d in range(taille):
            if L[s][d] == 1:
                bombes += 1
            if info_donnee_au_joueur[s][d] == 'f' and L[s][d] == 1:
                points += 1
            if info_donnee_au_joueur[s][d] == 'X':
                remplie = False
            
    if points == bombes and remplie == True:
            fin = True
            
    return (mort,casesconnues, info_donnee_au_joueur, fin)

def minesacote(L):               #renvoie, pour une grille, le nombre de mines a cote de chaque case
    M = np.array([[0 for i in range(np.shape(L)[0])] for j in range(np.shape(L)[0])])
    for i in range(0,np.shape(L)[0]):
        for j in range(0,np.shape(L)[0]):
            a=0
            for u in [i-1,i,i+1]:
                for v in[j-1,j,j+1]:
                    if valide(L,u,v) and L[u][v]==2:
                        M[u][v]=9
                    elif valide(L,u,v) and (u,v)!=(i,j) and L[u][v]==1:
                        a=a+1
            M[i][j]=a
    return M

def acote(L,i,j):
    A=[]
    for u in [i-1,i,i+1]:
        for v in[j-1,j,j+1]:
            if valide(L,u,v) and (u,v) != (i,j):
                A=A+[u]+[v]
    return A

def setupgrille(n,m,a,b):

    
    casesconnues = np.array([[0 for i in range(n)] for j in range(n)])
    minesacote = np.array([[0 for i in range(n)] for j in range(n)])
    grille =  np.array([[0 for i in range(n)] for j in range(n)])   #génération des grilles
    
    for u in [a-1,a,a+1]:
        for v in[b-1,b,b+1]:
            if valide(grille,u,v):
                grille[u][v]=2
    for i in range(n):
        grille[a][b]=2
        z=rd.randint(-1,1)
        if valide(grille,a+z,b+1-abs(z)):
            (a,b)=(a+z,b+1-abs(z))   #génération des espaces libres

    j=0
    while j<m:
        x=rd.randint(0,n-1)
        y=rd.randint(0,n-1)
        if valide(grille,x,y) and grille [x][y]==0:
                grille[x][y]=1
                for p in range ((int(len(acote(grille,x,y))))//2):
                    minesacote [acote(grille,x,y)[2*p]] [acote(grille,x,y)[2*p+1]] +=1
                j=j+1   #génération et comptage des mines
                
    for i in range (n):
        for j in range(n):
            if grille[i][j]==2:
                casesconnues[i][j] = 1
                grille[i][j]+=-2#génération de casesconnues
        
    for i in range(n):
        for j in range(n):
            if casesconnues[i][j]== 1:
                revele(minesacote,i,j,casesconnues)   #révèle sur la grille de départ

    return(grille, minesacote, casesconnues)

def deplacebombe(L,M,i,j,taille):

    for c in range(taille):

        for v in range(taille):

            if L[c][v] == 0 and (c != i and v != j):

                L[c][v] = 1

                L[i][j] = 0

                for k in [-1,0,1]:
                    for l in [-1,0,1]:
                        if k == l and k == 0:
                            continue
                        
                        elif valide(M,c+k,v+l)== True:
                            M[c+k][v+l] = M[c+k][v+l] +1
                            
                        if k == l and l == 0:
                            continue
                        
                        elif valide(M,i+k,j+l)== True:
                            M[i+k][j+l] = M[i+k][j+l] -1
                            
                for k in range(taille):

                    for l in range(taille):

                        gennbrvoisin(L,M,k,l,taille)            

                return L,M


    


def casescheck(L,M,i,j):
    Ni = []
    Nj = []
    for h in [-1,0,1]:
        for g in [-1,0,1]:
            if i == j and j == 0:
                continue
            elif valide(L,i+h,j+g) == True:
                if M[i+h][j+g] == 0:
                    Ni = Ni + [i+h]
                    Nj = Nj + [j+g]
    return(Ni,Nj)



def gennbrvoisin(L,M,i,j,taille):

    a= 0

    for h in [-1,0,1]:

        for g in [-1,0,1]:

            if i+h < taille and i+h >=0 and j+g < taille and j+g>=0:

                if L[i+h][j+g] == 1:

                    a = a +1

    M[i][j] = a

    return M

                    

def grille(taille, nbrmines): # 0: pas de mine, 1: mine

    L = np.array([[0 for i in range(taille)]  for j in range(taille)])

    for i in range(0,nbrmines):

        a = rd.randint(0,taille-1)

        b = rd.randint(0,taille-1)
        
        L[a][b] = 1

    M = np.array([[0 for i in range(taille)]for j in range(taille)])

    for k in range(taille):

        for l in range(taille):

            gennbrvoisin(L,M,k,l,taille)

    return L,M


def rajoute_voisin(i,j,M,Xc,Yc,casesconnues):
    if M[i][j] != 0 or casesconnues[i][j]==9:
        return (Xc,Yc)
    else:
        for a in [-1,0,1]:
            for b in [-1,0,1]:
                if a == b and b == 0:
                    continue
                elif valide(M,i+a,j+b) == True and casesconnues[i+a][j+b] == 0:
                    casesconnues[i+a][j+b] = 1
                    
                    Xc = Xc + [i+a]
                    Yc = Yc + [j+b]
        
        return(Xc,Yc)
        
def revele(M,i,j,casesconnues):
    Xc = []
    Yc = []
    Xc,Yc = rajoute_voisin(i,j,M,Xc,Yc,casesconnues)
    if len(Xc) != 0:
        continuer = True
    else:
        continuer = False
        
    while continuer == True:
        a = Xc[0]
        b = Yc[0]
        Xc,Yc = rajoute_voisin(a,b,M,Xc,Yc,casesconnues)
        Xc = Xc[1:]
        Yc = Yc[1:]
        if len(Xc) != 0:
            continuer = True
        else:
            continuer = False
    return casesconnues
            
        

def premiercoup(L,M,taille,nbrmines,i,j): # nbr de mines < taille au carree
    casesconnues = np.array([[0 for i in range(taille)]for j in range(taille)])
    if valide(L,i,j)== True:
        if L[i][j] == 1:
            L,M = deplacebombe(L,M,i,j,taille)
            casesconnues[i][j] = 1
            casesconnues = revele(M,i,j,casesconnues)
        else:
            casesconnues[i][j] = 1# 0: pas connue, 1: connue
            casesconnues = revele(M,i,j,casesconnues)

    return casesconnues

def premiercoup_aleatoire(L,M,taille,nbrmines): # nbr de mines < taille au carree
    i = rd.randint(0,len(L)-1)
    j = rd.randint(0,len(L)-1)
    casesconnues = np.array([[0 for i in range(taille)]for j in range(taille)])
    if valide(L,i,j)== True:
        if L[i][j] == 1:
            L,M = deplacebombe(L,M,i,j,taille)
            casesconnues[i][j] = 1
            casesconnues = revele(M,i,j,casesconnues)
        else:
            casesconnues[i][j] = 1# 0: pas connue, 1: connue
            casesconnues = revele(M,i,j,casesconnues)

    return(L,M,casesconnues)

def faire_un_coup(info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin,mort):
    if valide(L,i,j) == False or casesconnues[i][j] == 2 or casesconnues[i][j] == 1:
        return(info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin,mort)
    elif casesconnues[i][j] == 9 and (d == "non" or d == "n"):
        casesconnues[i][j] = 0
        return(info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin,mort)
    elif L[i][j] == 1 and (d == "non" or d == "n"):
        fin = True
        mort = True
        return (info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin,mort)
    elif (d == "oui" or d =="o"):
        casesconnues[i][j] = 9
        return(info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin,mort)
    elif L[i][j] == 0 and (d == "non" or d == "n"):
        casesconnues[i][j] = 1
        return(info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin,mort)
        
def gen_info_fournis_au_joueur(taille):
    info_donnee_au_joueur = np.array([['X' for i in range(taille)]for j in range(taille)])
    return info_donnee_au_joueur

def update_info(info_donnee_au_joueur,casesconnues,M,taille):
    for i in range(taille):
        for j in range(taille):
            if casesconnues[i][j] == 1:
                info_donnee_au_joueur[i][j] = M[i][j]
            if casesconnues[i][j] == 9:
                info_donnee_au_joueur[i][j] = 'f'
            if casesconnues[i][j] == 0:
                info_donnee_au_joueur[i][j] = 'X'

def jouer(taille,nbrmines): #9 pour drapeau
    victoire = False
    fin = False
    i = int(input("ligne"))
    j = int(input("colonne"))
    L,M = setupgrille(taille,nbrmines,i,j)
    casesconnues = premiercoup(L,M,taille,nbrmines,i,j)
    revele(M,i,j,casesconnues)
    info_donnee_au_joueur = gen_info_fournis_au_joueur(taille)
    update_info(info_donnee_au_joueur,casesconnues,M,taille)
    print(info_donnee_au_joueur)
    #print(L)
    #print(M)
    #print(casesconnues)
    
    while fin != True:
        i = int(input("ligne"))
        j = int(input("colonne"))
        d = input("drapeau,oui ou non")
        info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin = faire_un_coup(info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin)
        revele(M,i,j,casesconnues)
        update_info(info_donnee_au_joueur,casesconnues,M,taille)
        bombes = 0
        points = 0
        for s in range(taille):
            for d in range(taille):
                if casesconnues[s][d] == 9 and L[s][d] == 0:
                    points = taille**2 + 1
                elif casesconnues[s][d] != 9 and L[s][d] == 1:
                    bombes = bombes + 1
                elif casesconnues[s][d] == 9 and L[s][d] == 1:
                    points = points + 1
                    bombes = bombes + 1
                    
        if points == bombes:
            fin = True
            victoire = True
        print(info_donnee_au_joueur)
        #print(L)
        #print(M)
        print(casesconnues)
        
    if victoire == True:
        print("Bravo, vous avez gagné")
    else:
        print("Raté,vous avez perdu")



def resolution_aleatoire(taille,nbrmines): #9 pour drapeau
    nombredecoups = 0
    victoire = False
    fin = False
    L,M = grille(taille,nbrmines)
    L,M,casesconnues = premiercoup_aleatoire(L,M,taille,nbrmines)
    info_donnee_au_joueur = gen_info_fournis_au_joueur(taille)
    update_info(info_donnee_au_joueur,casesconnues,M,taille)

    
    while fin != True:
        i = rd.randint(0,len(L)-1)
        j = rd.randint(0,len(L)-1)
        r = rd.randint(0,1)
        if r==0 :
            d='n'
        else:
            d='o'

        info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin = faire_un_coup(info_donnee_au_joueur,L,M,casesconnues,i,j,d,fin)
        if casesconnues[i][j]==0:
            nombredecoups = nombredecoups + 1
        revele(M,i,j,casesconnues)
        update_info(info_donnee_au_joueur,casesconnues,M,taille)
        bombes = 0
        points = 0
        for s in range(taille):
            for d in range(taille):
                if casesconnues[s][d] == 9 and L[s][d] == 0:
                    points = taille**2 + 1
                elif casesconnues[s][d] != 9 and L[s][d] == 1:
                    bombes = bombes + 1
                elif casesconnues[s][d] == 9 and L[s][d] == 1:
                    points = points + 1
                    bombes = bombes + 1
                    
        if points == bombes:
            fin = True
        
    return nombredecoups
        
        
def reussite(p,n,m):
    s=0
    for i in range (0,p):
        s=s+resolution_aleatoire(n,m)
    return s/p

def premier_coup_ordi(i,j):
    return setupgrille(15,20,i,j)

def inconnu(info_donnee_au_joueur,i,j):
    Xlibre=[]
    Ylibre=[]
    n=0
    for u in [i-1,i,i+1]:
        for v in[j-1,j,j+1]:
            if valide(info_donnee_au_joueur,u,v) and (u,v)!=(i,j):
                if info_donnee_au_joueur[u][v]=='X':
                    n=n+1
                    Xlibre=Xlibre+[u]
                    Ylibre=Ylibre+[v]
    return Xlibre,Ylibre,n

def connu(info_donnee_au_joueur,i,j):
    Xlibre=[]
    Ylibre=[]
    n=0
    for u in [i-1,i,i+1]:
        for v in[j-1,j,j+1]:
            if valide(info_donnee_au_joueur,u,v) and (u,v)!=(i,j):
                if info_donnee_au_joueur[u][v]!='X'and info_donnee_au_joueur[u][v]!='f':
                    n=n+1
                    Xlibre=Xlibre+[u]
                    Ylibre=Ylibre+[v]
    return Xlibre,Ylibre,n

def flag(info_donnee_au_joueur,i,j):
    n=0
    for u in [i-1,i,i+1]:
        for v in[j-1,j,j+1]:
            if valide(info_donnee_au_joueur,u,v) and (u,v)!=(i,j):
                if info_donnee_au_joueur[u][v]=='f':
                    n=n+1
    return n
    
    
            
def poids(info_donnee_au_joueur):
    C=np.array([[0.0 for i in range(np.shape(info_donnee_au_joueur)[0])] for j in range(np.shape(info_donnee_au_joueur)[0])])
    for i in range(np.shape(info_donnee_au_joueur)[0]):
        for j in range (np.shape(info_donnee_au_joueur)[0]):
            if info_donnee_au_joueur[i][j]!='X' and info_donnee_au_joueur[i][j]!='f':
                K,J,n=inconnu(info_donnee_au_joueur,i,j)
                if n!=0:
                    for k in range (n):
                        #print(info_donnee_au_joueur[i][j])
                        #print(flag(info_donnee_au_joueur,i,j))
                        #print(n)
                        C[K[k]][J[k]]=C[K[k]][J[k]]+((int(info_donnee_au_joueur[i][j])-int(flag(info_donnee_au_joueur,i,j)))/int(n))
                    C[i][j]=int(10*C[i][j])/10
                    
    return C

def maxindice(L,info_donnee_au_joueur):
    M=L[0][0]
    a,b=0,0
    for i in range(np.shape(L)[0]):
        for j in range(np.shape(L)[0]):
            if L[i][j]>M:
                M=L[i][j]
                a,b=i,j
                
    if M == L[0][0]:
        Lx = []
        Ly = []
        for i in range(np.shape(L)[0]):
            for j in range(np.shape(L)[0]):
                if info_donnee_au_joueur[i][j] == 'X':
                    Lx = Lx + [i]
                    Ly = Ly + [j]
        if Lx == []:
            print(info_donnee_au_joueur)
            print("l'erreur est la")
        c = rd.randint(0,len(Lx)-1)
        a,b = Lx[c],Ly[c]
    return a,b

def minindice(L,info_donnee_au_joueur):
    M=10
    a,b=0,0
    for i in range(np.shape(L)[0]):
        for j in range(np.shape(L)[0]):
            if L[i][j]<M and L[i][j] != 0:
                M=L[i][j]
                a,b=i,j
    if M == 10:
        Lx = []
        Ly = []
        for i in range(np.shape(L)[0]):
            for j in range(np.shape(L)[0]):
                if info_donnee_au_joueur[i][j] == 'X':
                    Lx = Lx + [i]
                    Ly = Ly + [j]
        if Lx == []:
            print(info_donnee_au_joueur)
            print("l'erreur est la")
        c = rd.randint(0,len(Lx)-1)
        a,b = Lx[c],Ly[c]
    return a,b

if __name__ == "__main__":
    statistiques_resolution(20, 100, 1000)