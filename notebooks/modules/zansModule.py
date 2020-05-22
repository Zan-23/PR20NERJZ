import pandas as pandas
import os
import json
import numpy as np
import math
import matplotlib.pyplot as plt
from IPython.display import clear_output
from ipywidgets      import Dropdown
from bqplot          import Lines, Figure, LinearScale, DateScale, Axis
from ipyleaflet      import Map, GeoJSON, WidgetControl
from ipywidgets import IntSlider, ColorPicker, jslink


def read_population_by_sex():
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

        pop_age = 0        # mogo�e zamenji z mediano 
        age_range = 2
        for num_range, num in row[2:-2].iteritems():
            pop_age += (num / temp_sum) * age_range
            age_range += 5
        main_set.loc[index,"avg_age"] = float(pop_age)
    return main_set
	

def draw_bar_chart_pop(year_and_pop_ar, country):
    # takes in an array of tuples on which the first index is a year and second num of people
    fig=plt.figure(figsize=(10, 4), dpi= 100, facecolor='w')
    plt.bar([i[0] for i in year_and_pop_ar], [i[1] for i in year_and_pop_ar], 
            color='royalblue', alpha=0.7, width=3)
    #plt.grid(color='#95a5a6', linestyle='--', linewidth=2, axis='y', alpha=0.7)
    plt.xlabel('Years')
    plt.ylabel('Number in thousands')
    plt.title(country + ' population growth graph')
    plt.show()
    
def draw_scatter_pop_growth(year_and_pop_ar, country):
    # takes in an 2d array on which the first index is a year and second num of people
    fig=plt.figure(figsize=(10, 4), dpi= 100, facecolor='w')
    date_arr  = [i[0] for i in year_and_pop_ar]
    pop_arr = [i[1] for i in year_and_pop_ar]
    max_pop = max(pop_arr)
    step = int(math.ceil(max_pop / 1000.0)) * 1000 / 10

    plt.plot(date_arr, pop_arr)
    plt.scatter(date_arr, pop_arr, color=(0.1, 0.9, 1, 0.90))
    plt.yticks(np.arange(0,  max_pop + step*2, step))
    plt.xlabel('Years')
    plt.ylabel('Number in thousands')
    plt.title(country + ' population growth graph')
    plt.show()
    
def get_sum_population_array(data_set, country):
    # generates array for the county, fist element in the tuple is the year second is population in thousand
    year_pop_array = []
    
    for date in range(1960, 2021, 5):
        pop = float(data_set[(data_set['Region-Country'] == country) & (data_set["Date"] == date)]["population_sum"].values)
        year_pop_array.append((date, pop))
    return year_pop_array 


def my_round(x, base=5):
    return base * round(x/base)

def get_age_distribution_array(data_set, country, date):  # works only for multiples of 5, from 1950 - 2020
        distribution_array = []
        country_pop = data_set[(data_set['Region-Country'] == country) & (data_set["Date"] == date)]
        temp_sum = country_pop.iloc[:, 2:-2]
        for age, value in temp_sum.iteritems():
            distribution_array.append((age, value.iloc[0]))

        return distribution_array

def draw_bar_chart_distribution(year_and_pop_ar, country):
    # takes in an array on which the first index is a year and second num of people, also a country
    fig=plt.figure(figsize=(10, 6), dpi= 100, facecolor='w')
    plt.barh([i[0] for i in year_and_pop_ar], [i[1] for i in year_and_pop_ar], 
            color='royalblue', alpha=0.7)
    #plt.grid(color='#95a5a6', linestyle='--', linewidth=2, axis='y', alpha=0.7)
    plt.xlabel('Number in thousands')
    plt.ylabel('Years')
    plt.title(country + ' population age distribution')
    plt.show()


def draw_age_dist_for_all(data_set):
    only_2020_data = data_set.copy()
    for index, row in only_2020_data.iterrows():
        if row[1] != 2020:
            only_2020_data = only_2020_data.drop(index)

    only_2020_data = only_2020_data.sort_values(by=["avg_age"])
    avg_age_distribution = only_2020_data[["Region-Country", "avg_age"]]

    temp_avg = avg_age_distribution.set_index("Region-Country")
    dict_avg_age = temp_avg.to_dict()["avg_age"]


    fig=plt.figure(figsize=(10, 40), dpi= 100, facecolor='w')
    plt.barh(list(dict_avg_age.keys()), list(dict_avg_age.values()), 
            color='royalblue', alpha=0.7)
    plt.xlabel('Avg age')
    plt.ylabel('Countries')
    plt.title("Average age distribituion for all countries")
    plt.savefig('Japan.png')
    plt.margins(y=0)
    plt.show()

def death_count_country_year(country, year):
    col_names = ["Country", "Year", "Area", "Month", "Record Type", "Reliability", "Source Year", "Value", "Value Footnotes"]
    months_arr = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    deaths_data = pandas.read_csv('../podatki/unData_deaths_per_month.txt', sep=";", header=0, names=col_names)

    country_data = deaths_data.loc[(deaths_data["Country"] == country) & (deaths_data["Year"] == str(year))]
    month_death_dict = dict()

    for idx, row in country_data.iterrows():
        if row["Month"] != "Total":
            month_death_dict[row["Month"]] = row["Value"]


    if month_death_dict == {} and not all(month in month_death_dict for month in months_arr):
        print("Try another year data missing for this one !" + str(month_death_dict))
        return None
    # print("keys " + str(month_death_dict.keys()))
    month_death_dict = {my_month: month_death_dict[my_month] for my_month in months_arr}
    return month_death_dict


def month_deaths(deaths_dict):
    if deaths_dict is not None:
        sum_deadth = 0
        keys = list(deaths_dict.keys())
        if len(keys) != 12:
            print("Dates must contain 12 months !!")
        
        else:
            for key in keys:
                sum_deadth += deaths_dict[key]
            avg = sum_deadth / 12.0
            return avg
    else:
        return "(No data)"
    

def draw_bar_chart_mortality(year1, year2, country): 
    year1 = str(year1)
    year2 = str(year2)
    month_num_dict_1 = death_count_country_year(country, year1)
    month_num_dict_2 = death_count_country_year(country, year2)
    if month_num_dict_1 is not None and month_num_dict_2 is not None:
        x_ticks_1 = sorted(month_num_dict_1.keys())
        x_ticks_2 = sorted(month_num_dict_2.keys())
        
        if x_ticks_1 == x_ticks_2:        
            fig = plt.figure(figsize=(14, 6), dpi= 100, facecolor='w')
        
            plt.plot(list(month_num_dict_1.keys()), list(month_num_dict_1.values()), color=(0.3, 0.8, 0.2, 0.70),
                    label=(country + " " + str(year1) + " leto"))
            plt.plot(list(month_num_dict_2.keys()), list(month_num_dict_2.values()), color='royalblue',
                    label=(country + " " + str(year2) + " leto"))         
            # plt.gcf().autofmt_xdate()
            # plt.margins(x=0)
            plt.xlabel('Months')
            plt.ylabel('Number of deaths')
            plt.title(country + ' mortality')
            plt.legend()
            plt.show()
        else:
            print("Dates do not match")
            print(x_ticks_1)
            print(x_ticks_2)



