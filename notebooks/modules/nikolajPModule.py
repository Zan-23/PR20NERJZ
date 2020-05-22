
import matplotlib
from math import isnan
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from scipy.stats import multivariate_normal as mvn
import scipy.cluster.hierarchy as sch
import pandas as pandas
import os
import sys
import json
import numpy as np
import math
import random
import matplotlib.pyplot as pltnk
# here you put your functions

def test_nikolaj():
    print("How you doin")

def read_csv():
    reader = pd.read_csv(r"..\podatki\US_gripa.csv")
    virus_array = reader.get_values()    #create array of data
    reader.head()
    Geop = reader["geoid"]
    Regija = reader["Region"]
    State = reader["State"]
    season = reader["season"]
    smr_g = reader["Deaths from influenza"]
    smr_pl = reader["Deaths from pneumonia"]
    smr_gp = reader["Pecent of deaths due to pneumonia or influenza"]
    smr_t = reader["All Deaths"]
    return smr_t,smr_gp,smr_pl,smr_g,season,State

def read_population_by_spol():
    rows_to_skip = [i for i in range(0, 16)]
    rows_to_skip.extend([i for i in range(17, 272)])   # odstranjevanje vrstic ki bi delale probleme
    rows_to_skip.extend([i for i in range(362, 377)])
    names  =["Region-Country", "Date", "0-4", "5-9",  "10-14", "15-19", "20-24", "25-29",
             "30-34", "35-39", "40-44", "45-49", "50-54", "55-59",  "60-64", "65-69", "70-74", "75-79",
             "80-84", "85-89", "90-94", "95-99", "100+"]

    main_set = pandas.read_excel('../podatki/POPULATION_BY_AGE_BOTH_SEXES.xlsx',
                                 usecols=(2, 7, 8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28),
                                    skiprows=rows_to_skip,
                                    names=names)
    main_set["population_sum"] = np.NaN
    main_set["avg_age"] = np.NaN

    for index, row in main_set.iterrows():
        temp_sum = 0
        for num_range, num in row[2:-2].iteritems():
            temp_sum += num

        main_set.loc[index,"population_sum"] = float(temp_sum)

        pop_age = 0        # mogoče zamenji z mediano
        age_range = 2
        for num_range, num in row[2:-2].iteritems():
            pop_age += (num / temp_sum) * age_range
            age_range += 5
        main_set.loc[index,"avg_age"] = float(pop_age)
    return main_set
def matricaRead():
    matrica = []
    america = []
    with open('../podatki/corona_latest.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
                matrica.append(row)
                if row[-5] == 'United_States_of_America':
                    america.append(row)
    return matrica,america
def PripravaZaGripo(season,smr_g,smr_pl):
    dfg = defaultdict(list)
    dfp = defaultdict(list)
    leta = set()
    for y,sg,sp in zip(season,smr_g,smr_pl):
        if not isnan(sg) and not isnan(sp):
            dfg[y].append(float(sg))
            dfp[y].append(float(sp))
            leta.add(y)
    leta = list(leta)
    return leta,dfg,dfp
def PripravaZaClusteing(main_set):
    sez = np.array(main_set)
    nmatrix = []
    labels = []
    brez = ["NORTHERN AMERICA","Western Europe","Southern Europe","Russian Federation","Eastern Europe","EUROPE","EUROPE AND NORTHERN AMERICA","OCEANIA (EXCLUDING AUSTRALIA AND NEW ZEALAND)","AUSTRALIA/NEW ZEALAND","Central America","LATIN AMERICA AND THE CARIBBEAN","Lao People's Democratic Republic","South-Eastern Asia","Eastern Asia","EASTERN AND SOUTH-EASTERN ASIA","CENTRAL AND SOUTHERN ASIA","Western Sahara",
    "Northern Africa","NORTHERN AFRICA AND WESTERN ASIA","Western Africa","Southern Africa","Sao Tome and Principe","Central African Republic","Middle Africa","Eastern Africa","SUB-SAHARAN AFRICA","Oceania","Northern America","Latin America and the Caribbean","Europe","Asia","Africa"]
    ali = ["Slovenia","Italy","Sweden","United Kingdom","Serbia","Spain","France","Germany"]
    for x in sez:
        if x[0] not in brez and int(x[1])==2020:
                kolk = [int(str(i).replace(".","")) for i in x[2:-2]]
                suma = sum(kolk)
                nmatrix.append([k/suma for k in kolk])
                labels.append(x[0]+"/"+str(x[1]))
    return nmatrix,labels
def PripravaSmrtnosti(matrica):
    prvad = "Afghanistan"
    smrtnost =  defaultdict(float)
    smrtinapreb = defaultdict(float)
    death = 0
    case = 0
    folk = 0
    TOTAL_D = 0
    TOTAL_C = 0
    matrica = matrica[1:]
    for x in matrica:
        if(x[6]==prvad):
            TOTAL_D += int(x[5])
            TOTAL_C += int(x[4])
            death += int(x[5])
            case += int(x[4])
        if x[-2] != "" and x[6]==prvad:
            folk = int(x[-2])
        if x[6]!=prvad:
            smrtnost[prvad] = death/case*100
            if folk != 0:
                smrtinapreb[prvad] = death/folk
            folk = 0
            prvad = x[6]
            death = int(x[5])
            case = int(x[4])
    smt = smrtnost
    return TOTAL_D,TOTAL_C,smrtinapreb,smrtnost

def PripravaParamSmrt(smrtnost):
    ignore = ["United_Republic_of_Tanzania","Saint_Vincent_and_the_Grenadines","Western_Sahara","Uzbekistan","United_States_Virgin_Islands","United_Republic_of_Tanzania","Turks_and_Caicos_islands","Taiwan","Tajikistan","Thailand","Timor_Leste","Togo","Sri_Lanka",
              "Sudan","Suriname","South_Sudan","Somalia","Sint_Maarten","Seychelles","Sao_Tome_and_Principe","Saint_Kitts_and_Nevis","Saint_Lucia","Saint_Vincent_and_the_Grenadines","Peru","Philippines","Papua_New_Guinea","Palestine",
    "Panama","Oman","Northern_Mariana_Islands","Nicaragua","Niger","Mozambique","Myanmar","Namibia","Nepal","Mongolia","New_Caledonia","Mauritania",
    "Mauritius","Malta","Madagascar","Malawi","Malaysia","Maldives","Liechtenstein","Lithuania","Luxembourg","Kyrgyzstan","Jersey","Jamaica","Isle_of_Man","Indonesia","Guinea_Bissau","Guyana","Haiti","Holy_See","Guatemala",
    "Guernsey","Grenada","Guam","Gambia","French_Polynesia","Falkland_Islands_(Malvinas)","Faroe_Islands","Bahamas","Anguilla","Eswatini","El_Salvador","Antigua_and_Barbuda",
    "Aruba","Equatorial_Guinea","Eritrea","Belize","Benin","Bangladesh","Barbados","Djibouti","Dominica","Comoros","Chad","Cape_Verde",
    "Cases_on_an_international_conveyance_Japan","Bonaire, Saint Eustatius and Saba","Bermuda","Bhutan","Cayman_Islands",
    "Central_African_Republic","Burkina_Faso","Burundi","Cambodia","British_Virgin_Islands","Brunei_Darussalam","Botswana","Lesotho"]
    smrtnosti = []
    smnapreb = []
    drzave = []
    for drz,dm in smrtnost.items():
        if drz not in ignore:
            smrtnosti.append(dm)
            smnapreb.append(dm)
            drzave.append(drz)
    return smrtnosti,smnapreb,drzave

def PripravaLetaDGP(dfg,dfp,leta):
    leta.sort()
    #trois seznames
    dg = []
    dp = []
    for x in leta:
        dg.append(sum(dfg[x]))
        dp.append(sum(dfp[x]))
    return dg,dp,leta

def years(leta, dg):
    y_pos = np.arange(len(leta))
    plt.rcdefaults()
    fig, ax = plt.subplots()
    ax.barh(y_pos, dg, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(leta)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Smrti')
    ax.set_title('Smrti zaradi gripe')
    plt.show()

def plucnca(leta,dp):
    y_pos = np.arange(len(leta))

    plt.rcdefaults()
    fig, ax = plt.subplots()
    ax.barh(y_pos, dp, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(leta)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Smrti')
    ax.set_title('Smrti zaradi pljucnice')
    plt.show()

def PljuvnivaSmrtiDrzava(State,smr_gp,smr_t):
    total = defaultdict(int)
    pneum = defaultdict(int)
    stejt = []
    for kraj,grip,vsi in zip(State,smr_gp,smr_t):
        if not isnan(grip) and not isnan(vsi):
            stejt.append(kraj)
            total[kraj] += int(grip)
            pneum[kraj] += int(vsi)
    stejt  = list(set(stejt))
    grp = []
    vs = []
    for x in stejt:
        grp.append(total[x])
        vs.append(pneum[x])
    return grp,stejt,vs

def smrtiZaradiP(stejt,grp):
    y_pos = np.arange(len(stejt))
    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(20,20))
    matplotlib.rc('xtick', labelsize=0.2)
    ax.figsize=(35, 35)
    ax.barh(y_pos, grp, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(stejt)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Smrti')
    ax.set_title('Smrti zaradi pljucnice')
      # labels read top-to-bottom
    plt.show()

def Clutr(nmatrix,labels):
    L1 = sch.linkage(nmatrix, method="average", metric="cityblock")
    t = 0.7
    plt.figure(figsize=(15, 30))
    predictions1 = sch.fcluster(L1, t=t, criterion="distance").ravel()
    D = sch.dendrogram(L1, labels=labels,orientation="left")
    plt.plot([0, 100], [t, t], "k--")
    plt.ylabel("Razdalje")
    plt.show()


def DeathUsaCovid():
    suma1 = 0
    okuzb = 0
    for m in america:
        if int(m[3]) == 2020:
            suma1 += int(m[5])
            okuzb += int(m[4])
    smrti1 = dg
    ns = [suma1 for deathm in range(len(dg))]
    return smrti1,ns,okuzb
def CorgRip(leta,ns,smrti):
    x = np.arange(len(leta))  # the label locations
    width = 0.38  # the width of the bars
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, ns, width, label='Korona')
    rects2 = ax.bar(x + width/2, smrti1, width, label='Gripa')
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Scores')
    plt.xticks(rotation=45)
    matplotlib.rc('xtick', labelsize=5)
    ax.set_title('Smrti po letih koronavirus vs gripa')
    ax.set_xticks(x)
    ax.set_xticklabels(leta)
    ax.legend()
    plt.show()

def printaj(TOTAL_D,TOTAL_C):
    print(f"Skupna smrtnost po vseh drzavah: {TOTAL_D/TOTAL_C*100}%")

def CoMort(drzave,smrtnosti):
    y_pos = np.arange(len(drzave))
    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(60,60))
    ax.barh(y_pos, smrtnosti, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(drzave)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Smrti')
    ax.set_title('Procent mrtvih za coivd')
    plt.show()

def CntRY(drzave,smnapreb):
    y_pos = np.arange(len(drzave))
    plt.rcdefaults()
    fig, ax = plt.subplots(figsize=(60,60))
    ax.barh(y_pos,  smnapreb, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(drzave)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Smrti')
    ax.set_title('Procent mrtvih za coivd')
    plt.show()


def Ocena_statistike(smrtnosti):
    data = smrtnosti
    data = [date for date in data]
    # Ocenimo parametre normalne (Gaussove) porazdelitve
    n = len(data)
    mu = np.mean(data)              # ocena sredine
    sigma2 = (n-1)/n * np.var(data) # ocena variance
    return n,mu,sigma2,data

def risi(data):
    plt.figure()
    counts, bins, _ = plt.hist(data, normed=True, label="vzorec", bins=10)
    pdf = [mvn.pdf(x, mu, sigma2) for x in bins]
    plt.plot(bins, pdf, "-", label="model", linewidth=2.0)
    plt.xlabel("povprečna ocena (X)")
    plt.ylabel("P(X)")
    plt.legend(loc=2);

def p_val(qx,n,mu,sigma2):
    # Izračunamo P(x) za dovolj velik interval
    xr    = np.linspace(0, 100, 10000)
    width = xr[1] - xr[0]       # sirina intervala
    Px = [mvn.pdf(x, mu, sigma2) * (xr[1]-xr[0])   for x in xr]


    # Vse vrednosti, ki so manjše ali enake od qx
    ltx     = xr[xr <= qx]

    # Množimo s širino intervala, da dobimo ploščino pod krivuljo
    P_ltx = [mvn.pdf(x, mu, sigma2) * width for x in ltx]

    # p-vrednost: ploscina pod krivuljo P(x) za vse vrednosti, manjse od qx
    p_value = np.sum(P_ltx)

    # Graf funkcije

    return p_value

def Dobre(smrtnost,n,mu,sigma2):
    alpha = 0.05
    for drzave,smrti in smrtnost.items():
        if p_val(smrti,n,mu,sigma2) < alpha:
            print(drzave)

def Slabe(smrtnost,n,mu,sigma2):
    alpha = 0.85
    for drzave,smrti in smrtnost.items():
        if p_val(smrti,n,mu,sigma2) > alpha:
            print(drzave)
