import pandas as pd
import statsmodels.api as sm 
import re

#Read in the data on happiness
happy_data = pd.read_excel(r'C:\Users\mattc\OneDrive\Desktop\Econometrics\Econometrics Project\Happiness Data Based on Cantril Ladder Survey Conducted by Gallup and Reported in teh World Happiness Survey.xlsx')
#print(happy_data.head())

#Read in data on culture
culture_data = pd.read_excel(r'C:\Users\mattc\OneDrive\Desktop\Econometrics\Econometrics Project\6 Dimmensions of Culture.xls')
#print(culture_data.head())

#####################################################################################################################################################################
#DATA PREP

#below is the data prep. I imagine there are issues related to effiecnelty allocating memory with the data frames.
#I was explicit in not removing prior versions of data frames in case I would need them later.

#Culture Data Prep:
#remove na values and unncessary columns in culture data. Fill in United States and United Kingdom(United States is U.S.A and United Kingdom is Great Britain in culture data)
culture_data.dropna(inplace = True)
culture_data.drop('ctr', 1, inplace = True)
culture_data.replace(to_replace= "U.S.A.", value = "United States", inplace = True)
culture_data.replace(to_replace="Great Britain", value = "United Kingdom", inplace = True)
culture_data.set_index('country', inplace = True)
#print('The new head of the data:')
#print(culture_data.head())
#print('The shape of the new dataframe:', culture_data.shape)

#give labels to the happiness data and remove plus signs
happy_data.columns = ['country', 'Happy Score']
happy_data['country'] = happy_data['country'].str.replace(r"\[.*\]", "")
happy_data.set_index('country', inplace = True)
#print(happy_data.head())

#create a new data frame that has all culure data and happiness data on matching countries
model_data = culture_data.copy()
model_data.index = model_data.index.str.strip()
happy_data.index = happy_data.index.str.strip()
final_data_1 = pd.merge(happy_data, model_data, left_index=True, right_index=True)
#print(final_data_1)
#print(final_data_1.shape)

#############################################################################################################################
#Below is a preliminary model not accounting for endoginous variables
print('Model 1, No Added Covariates:')
X = final_data_1[['pdi','idv','mas','uai','ltowvs','ivr']]
Y = final_data_1['Happy Score']
model1 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print(model1.summary())

#############################################################################################################################
#The following is the data preparation for the successive models. Risk index, considered in the initial model I produced, will be included with 
#the log of gdp/capita. The rational for including these data is that they both likely effect happiness. In particular, I theorized that gdp per cap
# effected individuatlity and risk index effected unceratainty avoiadance. Soviet Sattalite Data, the third variable included in the original model to combat endogeneity, will be removed from consideration. 
# The rational is that the effect of being a soviet sattalite likely is cultural which we are interested in. Also, a second model will be included that includes predictors
#identified by gallup as explaining happiness for the sake of removing all potential endogeneity. 

#Again, I imagine there is inefficency in all the dataframes i created, i did this to make sure i wasnt losing
#anything i used for a prior model.

#Risk Data
risk_data = pd.read_excel(r'C:\Users\mattc\OneDrive\Desktop\Econometrics\Econometrics Project\Risk Data.xlsx')
risk_data.drop(['ISONumeric', 'ISOAlpha', 'Rank', 'Exposure', 'Vulnerability', 'Susceptibility', 'Lack of coping capacities', 'Lack of adaptive capacities'], axis = 1, inplace = True)
risk_data.replace(to_replace= "Viet Nam", value = "Vietnam", inplace = True)
risk_data.replace(to_replace="Iran (Islamic Republic of)", value = "Iran", inplace = True)
risk_data.set_index('Country', inplace = True)
#print(risk_data)
#Add risk data to the set
final_data_2 = pd.merge(final_data_1, risk_data, left_index=True, right_index=True)
final_data_2['WorldRiskIndex'] = final_data_2['WorldRiskIndex'].astype(float)

#Factors to explain happiness (includes log gdp for the second model)
factor_data = pd.read_excel(r'C:\Users\mattc\OneDrive\Desktop\Econometrics\Econometrics Project\WHR2018Chapter2OnlineData.xls')
factor_columns = list(factor_data.columns.values)
#print(factor_columns)
rel_factor = ['country', 'year','Log GDP per capita','Social support','Healthy life expectancy at birth','Freedom to make life choices','Generosity','Perceptions of corruption', 'Confidence in national government']
to_drop = [n for n in factor_columns if n not in rel_factor]
factor_data.drop(to_drop, axis = 1, inplace = True)
#print(factor_data.head())
#only include rows where year is 2017
factor_data = factor_data[factor_data['year']==2017]
#print(factor_data.head())
factor_data.set_index('country', inplace = True)
factor_data.drop('year', axis =1, inplace = True)
#print(factor_data.head())
final_data_3 = pd.merge(final_data_2, factor_data, left_index=True, right_index=True)
#print(final_data_3)
#############################################################################################################################
#I commented out a lot of this section. Basically, when I included more covariates in successive models, some entries
#were not included for prior variables so they were removed. So, the following analysis seeks to understand if data
#was dropped due to differences in spelling and ultimately creates different data frames that handle the n/a
#entries through deletion and through filling with the mean to compare effects in model building


#The following code seeks to understand the dimmensions of the 3 data sets as the number of entries changed between them.
#This is useful information to understand in the context of the analysis and also could lend way to changes to the data to 
#register data that should be considered the same observation

#Examine shape of the sets
#print(final_data_1.shape)
#print(final_data_2.shape)
#print(final_data_3.shape)

#Four countries are dropped when risk data is included, then 3 are dropped when additional factors are included. Examine which
drop_1 = [n for n in final_data_1.index.values if n not in final_data_2.index.values]
#print(drop_1)
#Vietnam has wierd spelling in risk data
#Iran has wierd spelling
#no hong kong 
#no taiwan
#will redo code to fix first two

#the drops between sets 2 and 3
drop_2 = [n for n in final_data_2.index.values if n not in final_data_3.index.values]
#print(drop_2)



#Canada has no 2017 data
#Niether does Malaysia
#Nor Venezuala

#Count number of missing values
#print('The number of entries with na values:',final_data_3.shape[0] - final_data_3.dropna().shape[0])
#print('The entries with missing values includes:')
missing = [n for n in final_data_3.index.values if n not in final_data_3.dropna().index.values]
#print(missing)
#How should I handle these missing values?
#If only a few things are missing, maybe use imputation with mean, median, or mode
#If many are missing, remove.
#print('The entries including missing values:')
#print(final_data_3.loc[['China', 'Iran', 'Lithuania', 'Morocco', 'Poland', 'Vietnam'],['Social support','Freedom to make life choices','Generosity','Perceptions of corruption', 'Confidence in national government']])

#Vietnam has 5, will remove
#Poland, Lithuania, Morcoco, Iran have 1, use average
#China has 2. 
#THIS PRESENTS A BIAS IN THE MODEL. 

#For the final model with all factors, I will include 2 models, one with the na's all remove, the other with averages replacing na's except vietnam
final_data_3_noNA = final_data_3.dropna()
#print(final_data_3[['Perceptions of corruption', 'Confidence in national government',]].mean(skipna = True))

av_cor = final_data_3[['Perceptions of corruption', 'Confidence in national government']].mean(skipna = True).loc['Perceptions of corruption']
conf_gov = final_data_3[['Perceptions of corruption', 'Confidence in national government']].mean(skipna = True).loc['Confidence in national government']

final_data_3_fillNa = final_data_3.copy()
final_data_3_fillNa = final_data_3_fillNa.set_value('China', 'Perceptions of corruption', av_cor)
final_data_3_fillNa = final_data_3_fillNa.set_value('China', 'Confidence in national government', conf_gov)
final_data_3_fillNa = final_data_3_fillNa.set_value('Iran', 'Confidence in national government', conf_gov)
final_data_3_fillNa = final_data_3_fillNa.set_value('Lithuania', 'Perceptions of corruption', av_cor)
final_data_3_fillNa = final_data_3_fillNa.set_value('Morocco', 'Confidence in national government', conf_gov)
final_data_3_fillNa = final_data_3_fillNa.set_value('Poland', 'Perceptions of corruption', av_cor)
final_data_3_fillNa.dropna(inplace = True)

#############################################################################################################################
#Model with Risk Data and GDP included: Use final_data_3
print('Model 2, Risk Index and Log GDP Added:')
X = final_data_3[['pdi','idv','mas','uai','ltowvs','ivr', 'Log GDP per capita', 'WorldRiskIndex']]
Y = final_data_3['Happy Score']
model2 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print(model2.summary())

#############################################################################################################################
#Model with Risk Data, GDP, and other factors included. Run for dropped na and filled na data sets.

#First Model, with N/A factors deleted
print('The Final Model: Includes Previous Covariates Plus Added Happiness Predictors, N/A Factors Deleted')
X = final_data_3_noNA[['pdi','idv','mas','uai','ltowvs','ivr', 'Log GDP per capita', 'WorldRiskIndex','Social support','Healthy life expectancy at birth','Freedom to make life choices','Generosity','Perceptions of corruption', 'Confidence in national government']]
Y = final_data_3_noNA['Happy Score']
model3 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print(model3.summary())

#Second Model, N/A filled
print('The Final Model: Includes Previous Covariates Plus Added Happiness Predictors, N/A Factors Filled with Mean Values, No Vietnam')
X = final_data_3_fillNa[['pdi','idv','mas','uai','ltowvs','ivr', 'Log GDP per capita', 'WorldRiskIndex','Social support','Healthy life expectancy at birth','Freedom to make life choices','Generosity','Perceptions of corruption', 'Confidence in national government']]
Y = final_data_3_fillNa['Happy Score']
model4 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print(model4.summary())

#############################################################################################################################
#Rational for the different models reiterated:

# Initial model is just happiness factors and an intercept

#Second Model: A replication of the one I previously developed for class, includes World Risk Index as a proxy for natural disaster exposure and 
#GDP thinking that these factors could effect relevant cultural factors. Risk would be a non cultural factor that could impact uncertainty 
#avoidance and long term orientation. GDP could have some of the effect of individuality and indulgence (theoretically). 

#Final Model: seeks to remove all endogeniety. Includes factors listed in the world happiness report as contributing to happiness. The goal of 
#the model is to see if a particular culture effects happiness, not the concrete realities that contribute to the culture or are the effect of that culture.

#############################################################################################################################
#Analysis of Variance
#Standard error becomes very high in the latter two models especially and is high for the covariates in the 
#first few models as well. So, I will analyze the relevant contribtuors to this variance.

#High variance amongst control variables is irrelevant. I do not care to estimate these effects. The
#model is only interested in estimating culture's effects. Thus, I will first examine the distribution of each of 
#the culture's data, which effects variance in each of the respective parameters, as well as the distribution of 
#the happiness data, which is an estimate of the variance in y and thus the variance in the errors.

#Variance in a data set inversely corelates with variance in the feature's parameter.
#Coefficent of Variation is calculated to show standard deviation in context of the mean
print('Analysis of Cultural Predictor Distributions:')
print('PDI:',)
print('mean:',final_data_1.pdi.mean())
print('standard deviation',final_data_1.pdi.std())
print('Coefficent of Variation',final_data_1.pdi.std()/final_data_1.pdi.mean())
print('IDV:',)
print('mean:',final_data_1.idv.mean())
print('standard deviation',final_data_1.idv.std())
print('Coefficent of Variation',final_data_1.idv.std()/final_data_1.idv.mean())
print('MAS:',)
print('mean:',final_data_1.mas.mean())
print('standard deviation',final_data_1.mas.std())
print('Coefficent of Variation',final_data_1.mas.std()/final_data_1.mas.mean())
print('UAI:',)
print('mean:',final_data_1.uai.mean())
print('standard deviation',final_data_1.uai.std())
print('Coefficent of Variation',final_data_1.uai.std()/final_data_1.uai.mean())
print('LTOWVS:',)
print('mean:',final_data_1.ltowvs.mean())
print('standard deviation',final_data_1.ltowvs.std())
print('Coefficent of Variation',final_data_1.ltowvs.std()/final_data_1.ltowvs.mean())
print('IVR:',)
print('mean:',final_data_1.ivr.mean())
print('standard deviation',final_data_1.ivr.std())
print('Coefficent of Variation',final_data_1.ivr.std()/final_data_1.ivr.mean())
print('\n')
print('Analysis of Happiness Data Distribution')
print('mean:',final_data_1['Happy Score'].mean())
print('standard deviation',final_data_1['Happy Score'].std())
print('Coefficent of Variation',final_data_1['Happy Score'].std()/final_data_1['Happy Score'].mean())

#what follows is the r squared of each explanatory variable regressed on the other explanatory variables.
#R squared of a variable regressed on the other independent variables varies directly with variance of the parameter
print('\n')
print('R^2 Coefficents:')
X = final_data_1[['idv','mas','uai','ltowvs','ivr']]
Y = final_data_1['pdi']
model5 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print('PDI:',model5.rsquared)
X = final_data_1[['pdi','mas','uai','ltowvs','ivr']]
Y = final_data_1['idv']
model6 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print('IDV:',model6.rsquared)
X = final_data_1[['pdi','idv','uai','ltowvs','ivr']]
Y = final_data_1['mas']
model7 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print('MAS:', model7.rsquared)
X = final_data_1[['pdi','mas','idv','ltowvs','ivr']]
Y = final_data_1['uai']
model8 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print('UAI:', model8.rsquared)
X = final_data_1[['pdi','mas','uai','idv','ivr']]
Y = final_data_1['ltowvs']
model9 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print('LTOWVS:', model9.rsquared)
X = final_data_1[['pdi','mas','uai','ltowvs','idv']]
Y = final_data_1['ivr']
model10 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print('IVR:', model10.rsquared)

#Also, UAI shoots way up. Why?

#could have to do with the dropped countries dramatically effecting UAI. 
#-write model with data from the latest set
print('First Model with Last Data')
X = final_data_3_noNA[['pdi','idv','mas','uai','ltowvs','ivr']]
Y = final_data_3_noNA['Happy Score']
model11 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print(model11.summary())


print('First Model with Last Data fill na')
X = final_data_3_fillNa[['pdi','idv','mas','uai','ltowvs','ivr']]
Y = final_data_3_fillNa['Happy Score']
model12 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print(model12.summary())

#UAI does go up, but not as substaintially as into the second model

print('Original Model with second data set ')
X = final_data_3[['pdi','idv','mas','uai','ltowvs','ivr']]
Y = final_data_3['Happy Score']
model13 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print(model13.summary())

#the drop in data is almost signifigant. Why does adding variables increase the coefficents?




#I began to lose focus in the direction of the analysis but i think i am back on track. The high condition number implies
#multicolinearity which implies high variance in the parameter estimates driven by high R2 between coeffeicents.
#However, R2 coefficents were examined, and while 2 were around .5, all the others are less than .35. Further, 
#between models the standard errors do not change much, with all standard erros fluctuating between 0.03 and 0.05.
#This impies that there is not an issue with variance due to multicolinearity. 

#Independent of the multicolinearity concern, there is variablility in statistical signifigance between models.
#The other contributers to parameter standard error were thus analyzed. 3 had a coefficent of variation close to .5,
#implying that variance in the feature data may present variance issues. this and multicolinearity would be the 
#cause of variation as the coefficent of variation among the happiness data, the final contributer to parameter
#standard error, was quite low at 0.137.

#So, if new data was collected, there could be variability due to some high corelation between parameters and
#variation in the feature data itself.

#However, data used between models was constant, with some variation to only include entries that had data for the 
#new features added. this is consistent with the standard errors of the coefficents remaining largely constant. 
#Thus, the data changes between models does not seem to be a huge deal. Further, when the first model was run
#with data from the latter models, the standard error held between .003 and .005. 

#So, changes in statistical signifigance between models are due to changes in the parameters calculated between models. 
#Going through the model progressing and examining changes in the parameters is an intuitive next step of
#analysis. this is because it allows for the discovery of links of endogeneity primarly, and also could lead to 
#other conclusions as well.

##########################################################################################################################
#Analysis of changes in statistical signifigance:
#My next step was to understand WHY statistical signifigance changed for relevant coefficents between the models.

#Return Parameters who have a statistical signifiance fall below 2 between models or rise above 2 between models.
#(a t stat of 2 is considered as the threshold of statistical signifigance)
def sigChange (m1, m2):
    tseries1 = m1.tvalues
    tseries2 = m2.tvalues
    sig = []
    lost =[]
    for i in tseries1.index:
            if abs(tseries1[i]) <2 and abs(tseries2[i])>2:
                sig.append(i)
            elif abs(tseries1[i])>2 and abs(tseries2[i])<2:
                lost.append(i)
    return sig, lost

#Model 1 to model 2
#sig, lost = sigChange(model1, model2)
#print('The list that became signifigance')
#print(sig)
#print('The list that lost signifigance')
#print(lost)

#idv and ltowvs lost signifigance. The natural assumption is that through gdp the effect of idv and ltowvs
#went down. I believe this can be tested through quanitifying the amount idv and ltowvs would be biased
#if gdp, or maybe even also risk index, were not included. Ill read up on this and get back to it

#Model 2 to model 3
#sig, lost = sigChange(model2, model3)
#print('The list that became signifigance')
#print(sig)
#print('The list that lost signifigance')
#print(lost)

#PDI, MAS, and Log GDP per capita lost signifigance. I can now define a function that returns all signifigant
#Covariates and intuitive understandings of the relationships could be derived, or alternatively 
#I could read about quantify how much the precencse of endogenous variables effects other variables to understand
#the relationship quantitatively. I like the latter.

#Also, uai gains signifigance. I need to better understand why this is the case. Lastly, I will see if 
#signifigance changes between the 3d and 4th model to see if data changes have an effect

#Model 3 to model 4
#sig, lost = sigChange(model3, model4)
#print('The list that became signifigance')
#print(sig)
#print('The list that lost signifigance')
#print(lost)

#only controls gain and lost signifigance between the 3d and 4th models. So, the focus is now on

#1.) quantifying endogeneity to tell a story: to understand the relationships
#2.) Understand why UAI gained signifigance, why the coeffecient increased, in the latter models.


#Write a function that defines bias between model for changes between signifigant terms

#takes two models, gets variables signigigance changed between the two models, checks bias in first model from not adding
#variables of second model

#a function that returns variables added to the second model not in the first
def changeVar(m1, m2):
    var1 = m1.tvalues.index
    var2 = m2.tvalues.index
    new = []
    for i in var2:
        add = True
        for j in var1:
            if i == j:
                add = False
        if add:
            new.append(i)
    return new


#A function that takes 2 models and returns bias in simplier model from exclusion of each variable added to the second model
def endogCheck(m1, m2, data):
    #get variables that changed sig, remove constant
    sig, lost = sigChange(m1, m2)
    change = sig + lost
    if 'const' in change: change.remove('const')
    #get the variables added to second model
    new = changeVar(m1, m2)
    rTable = []
    result = pd.DataFrame(index = new, columns = change)
    #the parameters of the second model, relevant to find bias
    par = m2.params
    #Iterate over change and get r squared on new variables, placing in list
    for i in change:
        X = data[str(i)]
        r =[]
        for j in new:
            p = par[str(j)]
            Y = data[str(j)]
            s = sm.OLS(Y, sm.add_constant(X, has_constant = 'add')).fit().params[str(i)]
            bias = p*s
            r.append(bias)
        rTable.append(r)
    #create the dataframe
    for q in range(len(rTable)):
        result.iloc[:,q] = rTable[q]
    #add a row to calculate total bias
    result.loc['Total', :] = result.sum()
    #add columns to shoe percentages
    for i in result.columns:
        result[str(i) + '%'] = result[str(i)].div(m1.params[str(i)])
    return result

#print('The Parameters of Model 2')
#print(model2.params)

#Rresult = endogCheck(model1, model2, final_data_3)
#print(Rresult)

#check change and see if reasonable

#print('idv',model1.params['idv'] - model2.params['idv'])
#print('ltowvs', model1.params['ltowvs'] - model2.params['ltowvs'] )
#They are close, remember the first model's parameters are based on different data so that is also an effect

#If I could also have a column showing fraction of the the original parameter that could be very
#helpful to contextual the understanding of what the bias means bc it varies by the magnititude of 
#the parameter
#####################################################################################################################
#ANALYSIS OF ENDOGENEITY:
#This section i was analyzing the effects of enogeneity and it funneled my analysis further. it is disorganized 
#but i didnt want to delete it because it shows the development of my thought process to this point.


#The next section aims to look through models to understand why statistical signifigance changed for different
#features through models. The aim of this analysis is to understand through which factors various culture factors 
#of happiness operate through, as in the initial all are statistically signifigant except uai, which then later becomes signifigant.
#The following analysis seeks to understand these changes, to say which cultural factors occur through other means
#and which are relevant in their own right.

#ANALYSIS OF PROGRESSION FROM MODEL 1 TO MODEL 2
#Variables that gained and lost signifigance
sig, lost = sigChange(model1, model2)
print('The list that became signifigance')
print(sig)
print('The list that lost signifigance')
print(lost)

#The list of variables added to second model:
print('The variables added to the second model:')
print(changeVar(model1, model2))

#The table showing cause of bias for each variables from first model
print('Table Showing Bias: (columns are biased variables, rows are ommited variables)')
print(endogCheck(model1, model2, final_data_3))

#Conclusions:
#idv loses 0ver 60% of its values by including gdp in the model. This suggests the idv's effect on
#happiness occurs largely through gdp. Ltowvs loses 34% of its value through including gdp, suggesting
#that a lot of the effect of long term orientation is through gdp, which makes sense, countries with
#a higher longterm orientation likely tend to have stronger economies.

#ANALYSIS OF PROGRESSION FROM MODEL 2 TO MODEL 3, no na
#Variables that gained and lost signifigance
sig, lost = sigChange(model2, model3)
print('The list that became signifigance')
print(sig)
print('The list that lost signifigance')
print(lost)

#The list of variables added to second model:
print('The variables added to the second model:')
print(changeVar(model2, model3))

#The table showing cause of bias for each variables from first model
print('Table Showing Bias: (columns are biased variables, rows are ommited variables)')
print(endogCheck(model2, model3, final_data_3_noNA))

#The most striking example is the increase in uai. This is through 'case 3', where the true beta is positive
#and the endogenous variable and x are negetively corelated. 
#In the case of UAI, it was underesdtimated by more than 15X its value, most of this coming
#from perceptions of coruption. So, perceptions of coruption ans uai should be negetively corelated
X = final_data_3_noNA['uai']
Y = final_data_3_noNA['Perceptions of corruption']
s = sm.OLS(Y, sm.add_constant(X, has_constant = 'add')).fit().params['uai']
print('the coefficent between perception coruption and uai',s)
#OR perceptions of coruption should have a negetive coefficent
print('The coefficent on perceptions of corruption',model3.params['Perceptions of corruption'])
###################################################################################################################################################################3
#More bullshit of me reasoning through things from the previous analysis

#The current function returns a table showing the magnitude of bias from each variable. It does not show WHY
#the variable is biased. 
#So the question becomes, what is relevant to understand? the overall magnitude is valuable, and knowing the case is 
#valuable, but is it valuble to know the effect of each?
#You don't need it for every omited varible, only the ones that are most signifigant. 

#(1)So you could define a function that finds signifigant bias
#(2)define a function that returns the case and maginitude of the components of the bias
#I will arbitarily define the percentage of initial value that sigfifies majoy bias as 10%
#Below shows the 4 different cases of bias:

#Case 1: If b3 > 0 and d31 > 0 then b3*d31 > 0 à E(b1_hat) > b1
#Case 2: If b3 < 0 and d31 < 0 then b3*d31 > 0 à E(b1_hat) > b1
#Case 3: If b3 > 0 and d31 < 0 then b3*d31 < 0 à E(b1_hat) < b1
#Case 4: If b3 < 0 and d31 > 0 then b3*d31 < 0 à E(b1_hat) < b1

#return a data frame with rows ommited variables and columns intereted variables
#each entry is case describing bias
#only include entries where there is signifigant bias

#Scratch that. 

#(1)a function that defines a list of variables that effect sigfigant bias from the previous function

#then in a loop call a function that for each situation with signifiganct bias produces a dataframe that:
#row 1 includes case # 
#row 2 includes magnitude corelation
#row 3 includes magnitude of the ommited paramter
#column includes each ommited variable
#the table as a whole is for one relevant variable to show the story of its bias
##########################################################################################################################

#This function returns a table showing the total bias percentage for all signifigant percentages, meaning greater than 10%
def sigBias(endResult):
    per = []
    for i in endResult.columns:
        if re.search(r"%$", str(i)): 
            per.append(i)
    print(per)
    for i in per:        
        for j in endResult.index:
            if endResult.loc[j,i]<.1:
                endResult.loc[j,i] = None
    return endResult.loc[:, per]

#A function that is some way uses all prior functions to show effect of enodgeniety for a particular variables
def exBias(m1, m2,data, var):
    t = endogCheck(m1,m2,data)
    t_ = t.copy(deep = True)
    endTable = sigBias(t)
    print(t)
    end = []
    for i in endTable.index:
        if endTable.loc[i, var+'%'] != None and i !='Total':
            end.append(i)
    ind = ['Case #', 'Bias Correlation', 'Bias Endogenous Parameter', 'Total Bias %']
    tab = pd.DataFrame(index = ind, columns = end)
    for j in end:
        Y = data[j]
        X = data[var]
        d = sm.OLS(Y, sm.add_constant(X, has_constant = 'add')).fit().params[var]
        tab.loc['Bias Correlation', j] = s
        b = m2.params[j]
        tab.loc['Bias Endogenous Parameter', j] = d
        #Now define case
        if b>0 and d>0:
            tab.loc['Case #', j] = 1
        elif b<0 and d<0:
              tab.loc['Case #', j] = 2
        elif b>0 and d<0:
              tab.loc['Case #', j] = 3
        elif b<0 and d>0:
              tab.loc['Case #', j] = 4
        tab.loc['Total Bias %', j] = t_.loc[j, var+'%']
        
    print('Endogenous Effect Analysis for',var)
    return tab
##############################################################################################################################
# the last section was really messy but i kept all my comments to show the development of my thought process
#in case is should need it later. this final section uses a loop to show the engoeniety effects for each variable
#that changed in signigigance for each model transition.

#Model 1 to 2, iterate through all variables that changed in signifigance and produce an analysis of endogenous effects
sig, lost = sigChange(model1, model2)
change = sig +lost
for var in change:
    print(exBias(model1, model2 , final_data_3, var))
#Model 2 to 3, iterate through all variables that changed in signifigance and produce an analysis of endogenous effects
sig, lost = sigChange(model2, model3)
change = sig +lost
for var in change:
    print(exBias(model2, model3 , final_data_3_noNA, var))



















#final_data_3_noNA
#final_data_3_fillNa