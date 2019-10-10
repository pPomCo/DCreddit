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

#E: Les donnees en data frame
#F: Créer la matrice de var covar pour nos données et l'afficher
#S: Rien (fonction d'affichage)
def mcov(df):
	
	###Taille des mots
	(a,b) = df.shape
	print(a)
	if a<15000:
		csv = pd.read_csv('jultxt.csv',sep='\t', names=['id','taille_body'])

		csv['taille_body'] = csv['taille_body'].apply(lambda x: len(( " ".join(eval(x)) ).strip())) 

		df = df.merge(csv,on='id')
	
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
	
	###Date
	df_heure = df[['id','created_utc']]
	
	df_heure['heure'] = df_heure['created_utc'].apply(lambda x:datetime.utcfromtimestamp(x).hour)
	df_heure.drop('created_utc',  axis=1, inplace=True)
	
	df=df.merge(df_heure,on='id')
	
	###tfxidf
	
	###Affichage
	
	df.drop(['downs','archived'],axis=1,inplace=True)

	corr = df.corr()
	
	mask = np.zeros_like(corr, dtype=np.bool)
	mask[np.triu_indices_from(mask)] = True
	
	f, ax = plt.subplots(figsize=(11, 10))
	
	cmap = sns.diverging_palette(220, 10, as_cmap=True)
	
	cmap2 = sns.cubehelix_palette(as_cmap=True)
	
	sns.heatmap(corr, cmap=cmap, mask=mask, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
	
	df['upsNormalize'] = df['ups'].apply(lambda x: len(str(x)))
	sns.pairplot(df, diag_kind="kde", markers="+",hue='upsNormalize')
	
	plt.show()
	
	return
	
#E: Le dataframe de nos donnees
#F: Ajoute la representation vectorielle du body au data frame
#S: Le dataframe modifié
def bodyVectorise(df):

	cols = [i for i in range(201)]
	cols[200]='id'
	csv = pd.read_csv('jultxtVec.csv',sep='\t',names=cols)
	x = df.merge(csv,on='id')
	
	uselessFeatures =['subreddit_id', 'link_id', 'name', 
	'author_flair_css_class', 'author_flair_text', 
	'subreddit', 'id', 'removal_reason', 'author', 
	'body', 'distinguished', 'parent_id']
	
	x.drop((uselessFeatures),axis=1,inplace=True)
	print(x)

	y = x['ups']
	print(y)
	x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.70, random_state=42)
		
	#AJOUT DE CROSS VALIDATION CAR SURAPPRENTISSAGE	
	
	model = XGBRegressor(random_state=42,eval_metric="mae")
	model.fit(x_train,y_train)
	
	y_pred = model.predict(x_test)
	mae = mean_absolute_error(y_test,y_pred)
	print(mae)
	return
	
def main():
	#La premiere heure
	df = get_data_db("../projet reddit/sample.sqlite")
	#Les 3 premiers jours
	#df = get_data_db("../projet reddit/sample_3days.sqlite")
	bodyVectorise(df)
	#mcov(df)
	return

if __name__ == '__main__':
    main()
