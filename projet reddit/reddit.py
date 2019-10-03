#partie 2 The Reddit Project

import numpy as np
import sklearn as sk
import pandas as pd

#Recupération des donnees
#Récupérons les labels 
#Clean data

#E: Des données 
#F: Retourne les données préparés
#S: Des données
#Procedure Source :
#https://towardsdatascience.com/the-art-of-cleaning-your-data-b713dbd49726
def clean_data(df):
	# Missing data (generalement ont les enlèves):
	df.dropna(axis=0, how='any')
	# Outliers (ont regarde les 100 premiers et derniers):
	lower_limit = np.percentille(df.ups,0.0002)
	upper_limit = np.percentille(df.ups,0.00098)
	print(lower_limit)
	print()
	print(upper_limit)
		#potentiel transfo de x en enlevant ces 100 valeurs ovnies
	# Irrevelant features (Obliger score + down):
	df.drop('downs', axis=1)
	df.drop('score_hidden', axis=1)
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
	feature_groups = {}
	data=[]
	for i in range(len(tab)):
		feature_group[i]=', '.join(tab[i])
		data.append(df[tab[i]])
	return (data,feature_group)

#E: Nos données (de test) ainsi que nos predictions de ups
#F: Calcul la precision de notre modele sur 1 éssais
#S: Un float représentant la preécision (0 si echec)
def mae(df,predict):
        ups = df["ups"].tolist()
        n = len(ups)
        if n==len(predict):
                #addition commutative
                return (1/n)*abs(sum(ups)-sum(predict))
        return 0.0 

# Au cas ou split en train / test / validation
# Train 70 Test 20% Validation 10%
#x_train, x_b, y_train, y_b = train_test_split(x, y, train_size=0.80, random_state=42)
#x_test, x_ validation, y_test, y_validation(x_b, y_b, train_size=0.66 random_state=42)

#On retient la méthode Naive Bayes
#E: les données
#F: Execute un classifier naive bayes
#S: Retourne la prediction de ups
def classifier(df_train,df_test):
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

        
df = sample.sqlite
print(df)

