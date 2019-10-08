#partie 2 The Reddit Project

import numpy as np
import sklearn as sk
import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.ensemble.gradient_boosting import GradientBoostingRegressor

#Recupération des donnees
#Récupérons les labels 
#Clean data

#E: Des données 
#F: Retourne les données préparés
#S: Des données
#Procedure Source :
#https://towardsdatascience.com/the-art-of-cleaning-your-data-b713dbd49726
def clean_data(df):
	# Irrevelant features (Obliger score + down):
	df = df.drop(['downs','score'], axis=1)
	# Missing data (generalement ont les enlèves):
	#df = df.dropna(axis=0, how='any')
	# Outliers (ont regarde les 100 premiers et derniers):
	lower_limit = np.percentile(df.ups,0.0002)
	upper_limit = np.percentile(df.ups,0.00098)
	# potentiel transfo de x en enlevant ces 100 valeurs ovnies
	return df
	
#E: Des données, une liste de features
#F: Enlève les features de la liste a nos données
#S: Des données
def rmv_features(df,features):
	for i in range(len(features)):
		df.drop(features[i], axis=1)
	return df
	
#E: Des données, un tableau de features
#F: Regroupe les données par thème
#S: Des liste de données
def regroup(df,tab):
	data=[]
	for i in range(len(tab)):
		data.append(df[tab[i]])
	return data

#E: Nos données (de test) ainsi que nos predictions de ups
#F: Calcul la precision de notre modele sur 1 éssais
#S: Un float représentant la preécision (0 si echec)
def mae(df,predict):
        ups = df["ups"].tolist()
        n = len(ups)
        if n==len(predict):
                #addition commutative
                return (1/n)*abs(sum(ups)-sum(predict))
        return 9999999999.9999999999 

#On retient la méthode Naive Bayes
#E: les données
#F: Execute un classifier naive bayes
#S: Retourne la prediction de ups
def NVB(df_train,df_test):
        model = GaussianNB()
        df_train = clean_data(df_train)
        label = df_train["ups"]
        df_train = df_train.drop('ups', axis=1)
        #Entrainement du modele :
        model.fit(df_train,label)
        #Prediction :
        df_test = clean_data(df_test)
        df_test = df_test.drop('ups', axis=1)
        predict = model.predict(df_test)
        return predict

#E: Deux dataframe test train + leur label (test et train)
#F: Algo de gradiant boosting tree appliqué à nos données
#S: La liste des prédictions
def gbr(x_train,x_test,y_train):
	#Training Classifier
	reg = GradientBoostingRegressor(random_state=1)
	reg.fit(x_train, y_train)
	#Testing Classifier
	print(plt.plot(reg.predict(x_test)))			
	
#E: Un dataframe et une de ces feature en str
#F:	Modifie le data frame en transformant le chant feature en int
#S: Le dataframe modifié
def annexeMcov(df,feature):
	dictio = df[feature].to_dict()
	dictio2 = {}
	for i in range(len(dictio)):
		if not (dictio[i] in dictio2.keys()):
			dictio2[dictio[i]] = []
		dictio2[dictio[i]].append(i)
	clefs = list(dictio2.keys())
	li = [0]*10000
	for i in range(len(clefs)):
		L = dictio2[clefs[i]]
		for j in range(len(L)):
			li[L[j]]=i
	df = df.drop(feature, axis=1)
	df[feature]=li
	return df

#E: Les donnees en data frame, une liste de feature du dataframe str[]
#F: Créer la matrice de var covar pour nos données et l'afficher
#S: Rien (fonction d'affichage)
def Mcov(df,features):
	#Preparation du dataframe avec remplacement des string
	for i in range(len(features)):
		df = annexeMcov(df,features[i])
	print(df)
	#https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.corr.html
	cov = df.corr()
	print(cov)
	print("#####################")
	print("Ce qui nous interesse :")
	print(cov["ups"])
	
	#E: Une dataFrame
#F: Fonction de test du nettoyage des données
#S: Un entier
def test_clean(df):
	print(df)
	print()
	print("#####################################################################")
	print("Nettoyage des données")
	df=clean_data(df)
	print(df)
	print("#####################################################################")
	return 0
	
#E: Une dataFrame
#F: Fonction de test du regroupement des données
#S: Un entier
def test_regrp(df):
	datas = regroup(df,[['ups','parent_id'],['edited','body']])
	print(datas[0])
	print(datas[1])
	return 0

#E: Une dataFrame
#F: Fonction de test de la mae
#S: Un entier
def test_mae(df):
	ups = df.get('ups')
	L_ups = ups.values.tolist()
	print(mae(df,L_ups))
	L_ups.pop()
	print(mae(df,L_ups))
	return 0

#E: Une dataFrame
#F: Fonction de test du classifier
#S: Un entier
def test_classif(df):
	#x_train, x_ test, y_train, y_test = train_test_split(df, df[ups], train_size=0.70 random_state=42)
	#NVB(df)
	ups = df['ups']
	df = df.drop('ups', axis=1)
	x_train, x_test, y_train, y_test = train_test_split(df, ups, train_size=0.70, random_state=42)
	gbr(x_train, x_test, y_train)
	return 0
	
	
	
# Au cas ou split en train / test / validation
# Train 70 Test 20% Validation 10%
#x_train, x_b, y_train, y_b = train_test_split(x, y, train_size=0.80, random_state=42)
#x_test, x_ validation, y_test, y_validation(x_b, y_b, train_size=0.66 random_state=42)

def Main():
	cnx = sqlite3.connect('sample.sqlite')
	df = pd.read_sql_query("SELECT * FROM  May2015", cnx)
	features = ['subreddit_id','link_id','name','author_flair_css_class',
	'subreddit','id','removal_reason','author','distinguished','parent_id']
	Mcov(df,features)
	#test_classif(df)
	
	
Main()
