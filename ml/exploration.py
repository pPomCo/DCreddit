from preprocessing import *
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

#E: Les donnees en data frame
#F: Créer la matrice de var covar pour nos données et l'afficher
#S: Rien (fonction d'affichage)
def mcov(df):
	
	csv = pd.read_csv('jultxt.csv',sep='\t', names=['id','body'])
	
	csv['body'] = csv['body'].apply(lambda x: len(x))
	
	df.drop(['downs','archived'],axis=1,inplace=True)
	
	print(df.columns, csv.columns)
	print(df['id'])
	df=df.merge(csv,on='id')
	
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
	
	corr = df.corr()
	
	mask = np.zeros_like(corr, dtype=np.bool)
	mask[np.triu_indices_from(mask)] = True
	
	f, ax = plt.subplots(figsize=(11, 9))
	
	cmap = sns.diverging_palette(220, 10, as_cmap=True)
	
	sns.heatmap(corr, cmap=cmap, mask=mask, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
	
	sns.pairplot(df)
	
	plt.show()
	
	return

def main():
	df = get_data_db("../projet reddit/sample.sqlite")
	mcov(df)
	return

if __name__ == '__main__':
    main()
