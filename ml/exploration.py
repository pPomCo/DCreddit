from preprocessing import *
from datetime import datetime
from dateutil import tz
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

#E: Les donnees en data frame
#F: Créer la matrice de var covar pour nos données et l'afficher
#S: Rien (fonction d'affichage)
def mcov(df):
	
	###Taille des mots
	csv = pd.read_csv('jultxt.csv',sep='\t', names=['id','taille_body'])
	
	csv['taille_body'] = csv['taille_body'].apply(lambda x: len(x))
	
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

def main():
	
	df = get_data_db("../projet reddit/sample_3days.sqlite")
	mcov(df)
	
	return

if __name__ == '__main__':
    main()
