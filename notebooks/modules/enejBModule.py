# here you put your functions
# linearna(pop_by_sex) #how to call function
def priprava(avg_age_all_df,country,pop_by_sex):
    #priprava podatkov za starost
    avg_age_all_df = pop_by_sex.loc[:, ['Date','Region-Country', 'avg_age']] #avg_age_date_region-country
    avg_age_df = avg_age_all_df.loc[avg_age_all_df['Region-Country'] == country]
    avg_age_df_2020 = avg_age_df.loc[avg_age_df['Date'] == 2020]
    avg_age_df_spain = avg_age_df_2020.loc[avg_age_df['Region-Country'] == country]

    #priprava podatkov za corono
    corona_smrti_koeficient = pandas.read_csv(r"podatki\corona_latest.csv")
    corona_smrti_koeficient = corona_smrti_koeficient.loc[corona_smrti_koeficient['year'] == 2020]
    corona_smrti_koeficient = corona_smrti_koeficient.loc[corona_smrti_koeficient['countriesAndTerritories'] == country]
    corona_final1 = corona_smrti_koeficient.loc[:, ['deaths','popData2018']]
    corona_final_koeficient = corona_final1
    corona_final_koeficient['koeficient'] = ((corona_final_koeficient['deaths']*100)/corona_final_koeficient['popData2018']) *10000
    smrti_koeficienti = corona_final_koeficient.loc[:, ['koeficient']]
    smrti_koeficienti = smrti_koeficienti[smrti_koeficienti["koeficient"]!=0] #razlicen od 0
    smrti_koeficienti = smrti_koeficienti[smrti_koeficienti["koeficient"]>1] #vecji od 1
    smrti =smrti_koeficienti['koeficient'].mean()
    smrti
    smrt=[smrti]
    skupenDF2=avg_age_df_spain
    skupenDF2['koeficient']=smrt
    skupenDF2
    return skupenDF2

def iteracija_drzave(avg_age_all_df,pop_by_sex):
    drzave_df = avg_age_all_df.loc[:, ['Region-Country']]
    drzave_df = drzave_df['Region-Country'].unique()

    df_countries = priprava(avg_age_all_df,drzave_df[0],pop_by_sex)
    length = len(drzave_df) 
    i = 1
    # Iterating using while loop 
    while i < length: 
        df_countries = df_countries.append(priprava(avg_age_all_df,drzave_df[i],pop_by_sex))
        i += 1

    df_countries = df_countries.dropna()
    return df_countries
    #df_countries = df_countries[df_countries["koeficient"]!=0]
def linearna(pop_by_sex):
    avg_age_all_df = pop_by_sex.loc[:, ['Date','Region-Country', 'avg_age']]
    df_countries = iteracija_drzave(avg_age_all_df,pop_by_sex)
    X = df_countries.iloc[:, 2].values.reshape(-1, 1) # values converts it into a numpy array
    Y = df_countries .iloc[:, 3].values.reshape(-1, 1) # -1 means that calculate the dimension of rows, but have 1 column
    linear_regressor = LinearRegression()
    linear_regressor.fit(X, Y)
    Y_pred = linear_regressor.predict(X)
    plt.scatter(X, Y)
    plt.plot(X, Y_pred, color='red')
    plt.xlabel("Starost")
    plt.ylabel("Koeficient smrti")
    plt.show()

linearna(pop_by_sex)