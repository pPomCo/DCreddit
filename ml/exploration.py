import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as pl
from preprocessing import *
from datetime import datetime
from dateutil import tz
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as pl
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold
from cleantext import clean_text
from sklearn.decomposition import PCA

#E: Les donnees en data frame 
#F: Ajoute la feature de la taille du body
#S: Le dataframe modifié
def addTailleBody(df):
    
    df['taille_body'] = df['body'].apply(lambda x : clean_text(x))
    
    df['taille_body'] = df['taille_body'].apply(lambda x: len(x)) 
    
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
    
    df = df.merge(csv,left_on='id',right_on='comment_id')
    
    return df
    
#E: Les donnees en data frame
#F: Ajoute la feature du ups du pere
#S: Le dataframe modifié
def addParentUps(df):
    
    df2 = df[['ups','id']].copy().set_index('id')

    listeId = df2.index.values.tolist()
    
    df['parentUps'] = df['parent_id'].apply(lambda x: 1 if x not in listeId else df2.loc[x,'ups'])
    
    return
    

#E: Les donnees en data frame
#F: Créer la matrice de correlation pour nos données et l'afficher avec des nouvelle features
#S: Rien (fonction d'affichage)
def mcor(df):
    
    ###Clean Data
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
    
    df.drop(['downs','archived'],axis=1,inplace=True)
    
    ###Affichage

    corr = df.corr()
    
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    
    fig = pl.figure()
    pl.subplots(figsize=(11, 10))
    #pl.savefig('temp.png')
    #f, ax = pl.subplots(figsize=(11, 10))
    
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    
    sns.heatmap(corr, cmap=cmap, mask=mask, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
    
    pl.savefig("Correlation matrice.png", bbox_inches='tight')
    
    fig = pl.figure() 
    
    df['upsNormalize'] = df['ups'].apply(lambda x: len(str(abs(x))))
    
    palette = sns.color_palette("hls", 8)
    
    sns.pairplot(df, diag_kind="kde", markers="+",hue='upsNormalize',palette=palette)
    
    #pl.show()
    #Les plt.savefig sont uniquement pour l'execution sur Osirim
    pl.savefig("Affichage Donnees.png", bbox_inches='tight')
    
    return
    
#E: Le dataframe de nos donnees
#F: Affiche la mae pour un xgboost regressor des données avec le word embeding
#S: Le dataframe modifié
def bodyVectorise(x):
    
    uselessFeatures =['subreddit_id', 'link_id', 'name', 
    'author_flair_css_class', 'author_flair_text', 
    'subreddit', 'id', 'removal_reason', 'author', 
    'body', 'distinguished', 'parent_id','score_hidden',
    'score','downs','archived']
    
    x.drop((uselessFeatures),axis=1,inplace=True)
        
    #x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

    kf = KFold(n_splits=2, random_state=42)
    
    errors=[]
    
    cpt = 0
    
    for train_index, test_index in kf.split(x):
        x_train =  x.iloc[train_index]
        x_test = x.iloc[test_index]
        
        y_train = x_train['ups']
        y_test = x_test['ups']
        
        x_train.drop(['ups'],axis=1,inplace=True)
        x_test.drop(['ups'],axis=1,inplace=True)
        
        
        model = XGBRegressor(random_state=42,eval_metric="mae")
        model.fit(x_train,y_train)
    
        y_pred = model.predict(x_test)
        
        fig = pl.figure()		

        pl.scatter(y_test, y_pred,marker='+')
        pl.xlabel("True Values")
        pl.ylabel("Predictions")
        pl.savefig("Valeur - Predictions"+str(cpt)+".png", bbox_inches='tight')
        #pl.show()
    
        mae = mean_absolute_error(y_test,y_pred)
        errors.append(mae)
        
        cpt = cpt +1
    
    print("##################################")
    print("Les attributs utilisés pour la regression")
    print(x.axes)
    print("##################################")
    print("Erreur moyenne : ",np.mean(errors))
    print("#################################")

    return

#E: Le dataframe de nos donnees
#F: Realise l'acp de nos donnees sur les features de word embeding
#S: Le dataframe modifié
def acp(df):
    n_components = 10
    pca = PCA(n_components=n_components)
    
    uselessFeatures =['subreddit_id', 'link_id', 'name', 
    'author_flair_css_class', 'author_flair_text', 
    'subreddit', 'id', 'removal_reason', 'author', 
    'body', 'distinguished', 'parent_id','score_hidden',
    'downs','score','edited','controversiality','created_utc'
    ,'ups','archived','gilded','retrieved_on','heure','taille_body']
    
    df2 = df.drop((uselessFeatures),axis=1)
    
    principalComponents = pca.fit_transform(df2)
    
    principalDf = pd.DataFrame(data = principalComponents
             , columns = [
             'component '+str(i+1) for i in range(n_components)
             ])
    
    df = pd.concat([df,principalDf], axis = 1)
    
    wordFeatures = [i for i in range(200)]
    
    df.drop((wordFeatures),axis=1,inplace=True)
    
    return df
    
    
def main():
    #Csv des word embeding de la premiere heure
    #csv2 = 'jultxtVec.csv'
    #Csv des word embedings des 3M de premiers post
    csv = "/projets/M2DC/team_JJJP/embeddings/textVec.csv"
    
    #Les donnees de la premiere heure
    #df = get_data_db("../projet reddit/sample.sqlite")
    #Des 3 premiers jours
    #df2 = get_data_db("../projet reddit/sample_3days.sqlite")
    #Chemin de la base de données entiere sur osirim jhuteau
    df = get_data_db("/projets/M2DC/data/database.sqlite")
    
    #Ajout de features :
    df = addTailleBody(df)
    
    df = addHour(df)
    
    #df = addParentUps(df)
    
    df = addWordEmbeding(df,csv)
    
    #Modification des features de word embedings
    #df = acp(df)
        
    #mcor(df)

    bodyVectorise(df)
    
    return

if __name__ == '__main__':
    main()
