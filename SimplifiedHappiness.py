import pandas as pd
import statsmodels.api as sm 
import re
pd.set_option('display.max_columns', None)
#Read in the data on happiness
happy_data = pd.read_excel(r'C:\Users\mattc\OneDrive\Desktop\Econometrics\Econometrics Project\Happiness Data Based on Cantril Ladder Survey Conducted by Gallup and Reported in teh World Happiness Survey.xlsx')

#Read in data on culture
culture_data = pd.read_excel(r'C:\Users\mattc\OneDrive\Desktop\Econometrics\Econometrics Project\6 Dimmensions of Culture.xls')
#####################################################################################################################################################################
#DATA PREP FOR INITIAL MODEL

#below is the data prep for the initial model that just includes happiness data regressed on culture data. I imagine there are issues related to effiecnelty allocating memory with the data frames.
#I was explicit in not removing prior versions of data frames in case I would need them later.

#Culture Data Prep:
#remove na values and unncessary columns in culture data. Fill in United States and United Kingdom(United States is U.S.A and United Kingdom is Great Britain in culture data)
culture_data.dropna(inplace = True)
culture_data.drop('ctr', 1, inplace = True)
culture_data.replace(to_replace= "U.S.A.", value = "United States", inplace = True)
culture_data.replace(to_replace="Great Britain", value = "United Kingdom", inplace = True)
culture_data.set_index('country', inplace = True)

#give labels to the happiness data and remove plus signs
happy_data.columns = ['country', 'Happy Score']
happy_data['country'] = happy_data['country'].str.replace(r"\[.*\]", "")
happy_data.set_index('country', inplace = True)

#create a new data frame that has all culure data and happiness data on matching countries
model_data = culture_data.copy()
model_data.index = model_data.index.str.strip()
happy_data.index = happy_data.index.str.strip()
final_data_1 = pd.merge(happy_data, model_data, left_index=True, right_index=True)
#############################################################################################################################
#MODEL 1
print('Model 1, No Added Covariates:')
X = final_data_1[['pdi','idv','mas','uai','ltowvs','ivr']]
Y = final_data_1['Happy Score']
model1 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print(model1.summary())
#############################################################################################################################
#DATA PREP FOR SUCCESSIVE MODELS

#Risk Data
risk_data = pd.read_excel(r'C:\Users\mattc\OneDrive\Desktop\Econometrics\Econometrics Project\Risk Data.xlsx')
risk_data.drop(['ISONumeric', 'ISOAlpha', 'Rank', 'Exposure', 'Vulnerability', 'Susceptibility', 'Lack of coping capacities', 'Lack of adaptive capacities'], axis = 1, inplace = True)
risk_data.replace(to_replace= "Viet Nam", value = "Vietnam", inplace = True)
risk_data.replace(to_replace="Iran (Islamic Republic of)", value = "Iran", inplace = True)
risk_data.set_index('Country', inplace = True)
#Add risk data to the set
final_data_2 = pd.merge(final_data_1, risk_data, left_index=True, right_index=True)
final_data_2['WorldRiskIndex'] = final_data_2['WorldRiskIndex'].astype(float)

#Factors to explain happiness (includes log gdp for the second model)
factor_data = pd.read_excel(r'C:\Users\mattc\OneDrive\Desktop\Econometrics\Econometrics Project\WHR2018Chapter2OnlineData.xls')
factor_columns = list(factor_data.columns.values)
rel_factor = ['country', 'year','Log GDP per capita','Social support','Healthy life expectancy at birth','Freedom to make life choices','Generosity','Perceptions of corruption', 'Confidence in national government']
to_drop = [n for n in factor_columns if n not in rel_factor]
factor_data.drop(to_drop, axis = 1, inplace = True)
#only include rows where year is 2017
factor_data = factor_data[factor_data['year']==2017]
factor_data.set_index('country', inplace = True)
factor_data.drop('year', axis =1, inplace = True)
final_data_3 = pd.merge(final_data_2, factor_data, left_index=True, right_index=True)
#############################################################################################################################
#FIX DIFFERING VALUES
#the following code in the full version found some entries to have common names and deals with missing data between the concatenated sets.
#The full code defines 2 data sets, one that deletes na values and one that fills values with means
#Analysis related to finding entries spelled differently and and data frame with filled na values was removed from this script
#Later analysis reveals that the 2 data sets don't change which relevant covariates are statistically signifigant
final_data_3_noNA = final_data_3.dropna()
#############################################################################################################################
#Model 2 with Risk Data and GDP included: Use final_data_3
print('Model 2, Risk Index and Log GDP Added:')
X = final_data_3[['pdi','idv','mas','uai','ltowvs','ivr', 'Log GDP per capita', 'WorldRiskIndex']]
Y = final_data_3['Happy Score']
model2 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print(model2.summary())
#############################################################################################################################
#Model with Risk Data, GDP, and other factors included
print('The Final Model: Includes Previous Covariates Plus Added Happiness Predictors, N/A Factors Deleted')
X = final_data_3_noNA[['pdi','idv','mas','uai','ltowvs','ivr', 'Log GDP per capita', 'WorldRiskIndex','Social support','Healthy life expectancy at birth','Freedom to make life choices','Generosity','Perceptions of corruption', 'Confidence in national government']]
Y = final_data_3_noNA['Happy Score']
model3 = sm.OLS(Y,sm.add_constant(X, has_constant='add')).fit()
print(model3.summary())
#############################################################################################################################
#Full version includes an analysis of the distributions of the relevant covariates. This is because the condition number
#appeared high for every model. The analysis suggested that the R2 values were low between parameters so multicolinearity likely
#is not a problem. There was some decent variability in some of the factors, so there could be variability in the parameters
#for new data due t some corelation between parameters and variability in relevant feature data.
#############################################################################################################################
#FUNCTIONS TO ANALYZE ENDOGENEITY
#The following set of functions seeks to use the progression between different models to understand through which
#externalized factors cultural data are relevant, as well as which become signifigant after controlling for other variables.
#this is relevant because the first model has almost all covariates as signigigant which changes in successive models

#This function simply returns a list of variables that are signifgant in a given model
def sig(model):
    slist = []
    for i in model.params.index:
        if model.tvalues[i]>=2 or model.tvalues[i]<=-2:
            if model.params[i]>0:
                entry = 'POS'
            else:
                entry = 'NEG'   
            entry = entry +' '+i  
            slist.append(entry)
    return slist

#This Function Takes 2 model fits and returns a tuple of lists, one of variables that gain signigance, one that loses
#(t stat>2 defined as signifigant)
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
#in a data frame table
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
    #add columns to show percentages
    for i in result.columns:
        result[str(i) + '%'] = result[str(i)].div(m1.params[str(i)])
    return result

#This function returns a table showing the total bias percentage for all signifigant percentages, meaning greater than 10%
def sigBias(endResult):
    per = []
    for i in endResult.columns:
        if re.search(r"%$", str(i)): 
            per.append(i)
    for i in per:        
        for j in endResult.index:
            if endResult.loc[j,i]<.1:
                endResult.loc[j,i] = None
    return endResult.loc[:, per]

#A function that is some way uses all prior functions to show effect of enodgeniety for a particular variables passed to the function
def exBias(m1, m2,data, var):
    if m2.tvalues[var]> 2:
        gain = True
    else:
        gain = False
    t = endogCheck(m1,m2,data)
    t_ = t.copy(deep = True)
    endTable = sigBias(t)
    end = []
    for i in endTable.index:
        if endTable.loc[i, var+'%'] != None and i !='Total':
            end.append(i)
    ind = ['Case #', 'Bias Correlation', 'Bias Endogenous Parameter', 'Total Bias %', 'The Effect of Inclusion']
    tab = pd.DataFrame(index = ind, columns = end)
    for j in end:
        Y = data[j]
        X = data[var]
        d = sm.OLS(Y, sm.add_constant(X, has_constant = 'add')).fit().params[var]
        tab.loc['Bias Correlation', j] = d
        b = m2.params[j]
        tab.loc['Bias Endogenous Parameter', j] = b
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
        if t_.loc[j, var+'%']<0:
            tab.loc['The Effect of Inclusion',j] = 'Increase'
        else:
            tab.loc['The Effect of Inclusion',j] = 'Decrease'
 
    print('Endogenous Effect Analysis for',var, "Gain is", gain)
    return tab
#############################################################################################################################
#ANALYSIS OF ENOGENEITY THROUGH USE OF FUNCTIONS
#The following is simply a list of the variables that were signifigant in each model
print('Below are the statistically signifigant parameters and their signs in each model. POS denotes positive, NEG denotes negetive')
print('The signifigant paramters in model 1:',sig(model1))
print('The signifigant paramters in model 2:',sig(model2))
print('The signifigant paramters in model 3:',sig(model3))

#Model 1 to 2, iterate through all variables that changed in signifigance and produce an analysis of endogenous effects
print('Transition from Model 1 to Model 2')
sig, lost = sigChange(model1, model2)
change = sig +lost
if 'const' in change: change.remove('const')
for var in change:
    print(exBias(model1, model2 , final_data_3, var))
print('###############################################################################################################################')
#Model 2 to 3, iterate through all variables that changed in signifigance and produce an analysis of endogenous effects
print('Transition from Model 2 to Model 3')
sig, lost = sigChange(model2, model3)
change = sig +lost
if 'const' in change: change.remove('const')
for var in change:
    print(exBias(model2, model3 , final_data_3_noNA, var))

###############################################################################################################################################
#SUMMARY OF CONCLUSIONS

#Model 1 to 2
#Between model 1 and model 2 idv lost signifigance. It lost 60% of its value due to the inclusion of gdp, and it seem that this effect 
#is driven by the slight corelation but high effect that gdp holds on happiness. 

#Between model 1 and model 2 ltowvs lost signifigance. it lost 34% of its value through gdp, again driven by the slight corelation
#but high effect that gdp has on happiness.

#Model 2 to 3
#(UAI becomes positive in model 2)
#Uai gained in signifigance. it was underestimated by 60% through social support, 270% through freedom to make life choices,  495% through genorosity,
#1472% through perceptions of coruption. It was also overstimated by 48% through life expectancy and 663% through confidence in national
#government

#UAI moves opposite social support. This also has a strong coefficent. So, including social support in the model increases uai
#UAI moves opposite freedom to make life choices. Freedom to make life choices has a strong coefficent, so by including it, all the negetive effect from not having life choice is removed
#UAI moves opposite Generosity. It has a reletively strong negetive corelation and the parameter on genorosity is strong. so, including
#genorosity in the model causes uai to fall because its negetive corelation with uai is accounted for

#The strongest effect by far is through perceptions of coruption. UAI varies positively through coruption by a decent amount. 
#peceptions of coruption also has a very strong negetive coefficent. So, uai had basically been a proxy for perception of coruption
#so once it was included in the model, all the negetive effect through perception of corruption was removed from the variable.

#UAI moves opposite life expectancy. Life expectancy also has a negetive parameter. so, its inclusion descreses uai
#UAI moves with opposite national government. Confidence in national government also (surprisingly) has a strong negetive paramter.
#So, the inclusion in the model decreases uai.

#PDI lost signifigance.
#This was mainly driven through perceptions of coruption. A decently strong corelation with a very strong negetive parameter for
#that variable resulted in overestimating the negetive pdi parameter by 173%

#MAS lost signifigance
#There was not a clear overwhelming effect as in the case of the prior two variables. There were a few strong ones though. MAS is biased
#by social support by 16%, freedom to make life choices by 16%, and perception of coruption by 55%

#MAS corelated negetively with social support which has a positive effect on happiness. By including social support, the strong effect 
#of social support effectively runs through mas negetively due to the negetive corelation.

#MAS is negetively corelated with freedom to make life choices which has a strong positive effect on happiness. In the same story as social
#support, this causes the strong effect of freedom to make life choices to run through masculinity negetively due to the negetive 
#corelation.

#The largest effect is through perceptions of coruption. Masculine countries tend to have higher perceptions of coruption. Perception
#of coruption carries a strong negetive parameter. So, masculinity includes some of the effect of perception of corruption
#varying negetively with happiness until it is included in the model.

##########################################################################################################################################
#Succinct Conlusion
#Model one includes many signifigant cultural covariates. Individuality, Long term Orientation, and Indulgence all are statistically signifigant positvely corelated coefficents.
#Power Distance and Masculinity are statiscially signifigant negetive covariates. The only one not statistically sinigigant is Uncertainty Avaoidance
#Model 2 sees individuality and longterm orientation lose signifigance. This can be explained through the inclusion of gdp, as both of
#these covariates corelate with gdp which strongly predicts happiness.
#Model 3 sees interesting changes from model 2. It sees Uncertainty Avoiadance gain in signifigance, which had not been signifigant until this point. 
#It also sees Masculinity and Power Distance lose signifigance. Uncertainity avaoidance gains signifigant because it is heavilty biased by many
#variables due to decently strong coreelation with variables with strong effects. Most notably, Uncertainty positively corelates
#with perceptions of coruption,which has a strong negetive effect on happiness. 
#Masulinity is modertaly biased by 3 effects, most strongly perceptions of coruption. It tends to vary directly with perceptions of coruption, 
#which negetively effects happiness. 
#Power Distance falls in signifigance through perceptions of coruption as well. the negetive parameter had a strong corelation with the
#negetive perception of corruption.


#Indulgence is the only variable signifigant in all models. Uncertainty is signifigant in the final model after controlling for 
#many things that negetively corelate with happiness that were operating through it. 
