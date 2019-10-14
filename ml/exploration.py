from preprocessing import *
from datetime import datetime
from dateutil import tz
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as pl
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold

#E: Les donnees en data frame, Un data frame comprenant l'id et le tableau du body 
#F: Ajoute la feature de la taille du body
#S: Le dataframe modifié
def addTailleBody(df,csv):
	csv = pd.read_csv(csv,sep='\t', names=['id','taille_body'])
	
	csv['taille_body'] = csv['taille_body'].apply(lambda x: len(( " ".join(eval(x)) ).strip())) 
	
	df = df.merge(csv,on='id')
	
	return df

#E: Les donnees en data frame 
#F: Ajoute la feature de l'heure (plus interessant que UTC)
#S: Le dataframe modifié
def addHour(df):
	df_heure = df[['id','created_utc']]
	
	df_heure['heure'] = df_heure['created_utc'].apply(lambda x:datetime.utcfromtimestamp(x).hour)
	df_heure.drop('created_utc',  axis=1, inplace=True)
	
	df=df.merge(df_heure,on='id')
	
	return df

#E: Les donnees en data frame, les embeding des donnees 
#F: Ajoute la feature des word embedding (glove)
#S: Le dataframe modifié
def addWordEmbeding(df,csv):
	cols = [i for i in range(201)]
	cols[200]='id'
	csv = pd.read_csv(csv,sep='\t',names=cols)
	df = df.merge(csv,on='id')
	return df

#E: Les donnees en data frame
#F: Créer la matrice de var covar pour nos données et l'afficher avec des nouvelle features
#S: Rien (fonction d'affichage)
def mcov(df):
	
	object_columns = [
		'subreddit_id', 
		'link_id', 
		'name', 
		'author_flair_css_class',
		'author_flair_text',
		'subreddit',
		'id',
		'removal_reason',
		'author',
		'distinguished',
		'parent_id',
	]
	
	d = {
		col: 'None' for col in object_columns
	}
	
	df.fillna(d,inplace=True)
	
	###Affichage
	
	df.drop(['downs','archived'],axis=1,inplace=True)

	corr = df.corr()
	
	mask = np.zeros_like(corr, dtype=np.bool)
	mask[np.triu_indices_from(mask)] = True
	
	f, ax = pl.subplots(figsize=(11, 10))
	
	cmap = sns.diverging_palette(220, 10, as_cmap=True)
	
	cmap2 = sns.cubehelix_palette(as_cmap=True)
	
	sns.heatmap(corr, cmap=cmap, mask=mask, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
	
	df['upsNormalize'] = df['ups'].apply(lambda x: len(str(abs(x))))
	
	sns.pairplot(df, diag_kind="kde", markers="+",hue='upsNormalize')
	
	pl.show()
	
	return
	
#E: Le dataframe de nos donnees
#F: Affiche la mae pour un xgboost regressor des données avec le word embeding
#S: Le dataframe modifié
def bodyVectorise(df):
	
	uselessFeatures =['subreddit_id', 'link_id', 'name', 
	'author_flair_css_class', 'author_flair_text', 
	'subreddit', 'id', 'removal_reason', 'author', 
	'body', 'distinguished', 'parent_id','score_hidden',
	'downs','score']
	
	x.drop((uselessFeatures),axis=1,inplace=True)
		
	#x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

	kf = KFold(n_splits=2, random_state=42)
	
	errors=[]
	
	for train_index, test_index in kf.split(x):
		x_train =  x.iloc[train_index]
		x_test = x.iloc[test_index]
		
		y_train = x_train['ups']
		y_test = x_test['ups']
		
		model = XGBRegressor(random_state=42,eval_metric="mae")
		model.fit(x_train,y_train)
	
		y_pred = model.predict(x_test)
	
		pl.scatter(y_test, y_pred,marker='+')
		pl.xlabel("True Values")
		pl.ylabel("Predictions")
		pl.show()
	
		mae = mean_absolute_error(y_test,y_pred)
		errors.append(mae)
	
	print("Erreur moyenne : ",np.mean(errors))

	return
	
def main():
	#Csv de la premiere heure
	csv = 'jultxt.csv'
	csv2 = 'jultxtVec.csv'
	#La premiere heure
	df = get_data_db("../projet reddit/sample.sqlite")
	#Les 3 premiers jours
	#df = get_data_db("../projet reddit/sample_3days.sqlite")
	
	df = addTailleBody(df,csv)
	
	df = addHour(df)
	
	df = addWordEmbeding(df,csv2)
	
	print(df)
	
	#bodyVectorise(df)
	
	#mcov(df)
	return

if __name__ == '__main__':
    main()
