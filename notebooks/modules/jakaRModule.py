import pandas as pd
import random
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as sch

# Jaka Rizmal's module


def test_jaka():
    print("Jaka's module is here!")


def readGrowthData():
    # Reading data
    dataFrame = pd.read_table(
        "../podatki/corona_latest.csv", sep=",", usecols=[0, 4, 5, 6, 9])

    # Converting column to datetime dtype
    dataFrame["dateRep"] = pd.to_datetime(
        dataFrame["dateRep"], format="%d/%m/%Y")

    # Extracting min and max dates
    dateMin = dataFrame["dateRep"].min()
    dateMax = dataFrame["dateRep"].max()
    # Creating a weekly date range
    dateRange = pd.date_range(dateMin, dateMax, freq="W")

    # Getting all countries
    countries = dataFrame["countriesAndTerritories"].unique()

    # Return a tuple
    return(dataFrame, dateRange, countries)


def createWeeklyStatsDict(dataFrame, dateRange, countries):
    weeklyStats = dict()

    # Iterate through countries and calculate weekly cases and deaths
    for currentCountry in countries:
        weeklyStats[currentCountry] = []
        rows = dataFrame[dataFrame["countriesAndTerritories"]
                         == currentCountry]
        for i in range(len(dateRange)):
            if i >= len(dateRange)-1:
                break
            # Select rows between this and next dateRange item
            week = rows[(rows["dateRep"] >= dateRange[i]) &
                        (rows["dateRep"] < dateRange[i+1])]
            # Iterate through weeks and sum cases and deaths, add to weeklyStats
            weeklyStats[currentCountry].append(
                [week["cases"].sum(), week["deaths"].sum()])

    return weeklyStats


def createWeeklyCoefficientsDict(weeklyStats):
    weeklyCoefs = dict()

    # Calculate growth coefficients between weeks
    for country in weeklyStats.keys():
        weeks = weeklyStats[country]
        casesCoefs = []
        deathsCoefs = []
        for i in range(len(weeks)):
            if i >= len(weeks)-1:
                break
            if weeks[i][0] == 0:
                casesCoefs.append(0)
            else:
                casesCoefs.append(weeks[i+1][0]/weeks[i][0])
            if weeks[i][1] == 0:
                deathsCoefs.append(0)
            else:
                deathsCoefs.append(weeks[i+1][1]/weeks[i][1])
        weeklyCoefs[country] = []
        weeklyCoefs[country].append(casesCoefs)
        weeklyCoefs[country].append(deathsCoefs)

    return weeklyCoefs


def createMatricesAndLabels(weeklyCoefs, sampleSize=None):
    labels = weeklyCoefs.keys()

    if sampleSize:
        if not sampleSize > len(list(labels)):
            random.seed(66)
            labels = random.sample(labels,sampleSize)

    caseMatrix = []
    deathMatrix = []

    # Create a matrix of coefficients
    for country in labels:
        caseMatrix.append(weeklyCoefs[country][0])
        deathMatrix.append(weeklyCoefs[country][1])

    labels = list(weeklyCoefs.keys())

    return (caseMatrix, deathMatrix, labels)


def createLinkage(matrix):
    return sch.linkage(matrix, method="ward")


def drawDendrogram(linkage,labels,title="",ylabel="Država",xlabel="Razdalja"):
    plt.figure(figsize=(15, 40))
    dendogram = sch.dendrogram(linkage, labels=labels,orientation="left", leaf_font_size=20)
    # plt.plot([0, 100], [t, t], "k--")
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.show()


def readTotalPopulationData():
    populationFrame = pd.read_table("../podatki/total_population_by_sex.csv",sep=",",usecols=[1,4,8])
    populationFrame["PopTotal"] = populationFrame["PopTotal"]*1000
    populationFrame["PopTotal"] = pd.to_numeric(populationFrame["PopTotal"],downcast="signed")
    countryList = populationFrame["Location"].unique()
    return (populationFrame, countryList)


def getCountryPopulation(frame,year,country):
    return frame[(frame["Location"]==country)&((frame["Time"]==year))]["PopTotal"].iloc[0]


def readDeathData(year=2015):
    # Get death by month list
    # "Country or Area";"Year";"Month";"Value";
    deathFrame = pd.read_table("../podatki/unData_deaths_per_month.txt",sep=";",usecols=[0,1,3,7],skiprows=range(39282,39400))

    # Only use 2015 data
    deathFrame=deathFrame[deathFrame["Year"]==year]
    return deathFrame


def createMonthDeathDictionary(deathFrame,populationFrame,countryList,months):
    # Make a dictionary with country for key and array of deaths per each month per million eg. {"Slovenia": [2,3,5,2,4,2,4,5,3,2,4,5]}
    monthDeaths = dict()
    for cou in countryList:
        monthDeaths[cou]=[]
        population = getCountryPopulation(populationFrame,2015,cou)    
        for m in months:
            deathCount = deathFrame[(deathFrame["Country or Area"]==cou)&(deathFrame["Month"]==m)]["Value"]
            if not deathCount.empty:
                realCount = deathCount.iloc[0]
                monthDeaths[cou].append(realCount/population*1000)

    deaths = dict()
    # Remove empty values
    for c in monthDeaths.keys():
        if len(monthDeaths[c]) == 12:
            deaths[c] = monthDeaths[c]

    return deaths


def createMatrixAndLabels(dictionary):
    # Making a matrix
    labels = list(dictionary.keys())
    matrix = []
    for c in labels:
        matrix.append(dictionary[c])
    
    return (matrix, labels)