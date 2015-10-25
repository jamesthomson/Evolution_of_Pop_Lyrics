import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.cross_validation import train_test_split
from sklearn.lda import LDA
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import average_precision_score

#import filter to found lyrics

lyrics=pd.DataFrame.from_csv('scraped_lyrics.tsv', sep='\t', index_col=False)
found_lyrics=lyrics[lyrics['lyrics']!='Lyrics Not found']


df = pd.read_csv("/Users/home/Documents/data/Evolution of Pop/EvolutionPopUSA_MainData.csv", usecols=[0, 6, 10], header=0)

song_list=pd.merge(df, found_lyrics, how='inner', on=['recording_id', 'recording_id'])

genres=np.array(song_list['cluster'])

#load output from tpoics modelling

doc_topic=np.load('/Users/home/Documents/data/Evolution of Pop/doc_topic.npy')
total_words=np.load('/Users/home/Documents/data/Evolution of Pop/total_words.npy')
song_vocab=np.load('/Users/home/Documents/data/Evolution of Pop/song_vocab.npy')
main_topic=np.load('/Users/home/Documents/data/Evolution of Pop/main_topic.npy')

doc_topic_df=pd.DataFrame(doc_topic)
main_topic_df=pd.DataFrame(main_topic)
main_topic_df.columns=['main_topic']
total_words_df=pd.DataFrame(preprocessing.scale(np.array(total_words, dtype=float)))
song_vocab_df=pd.DataFrame(preprocessing.scale(np.array(song_vocab, dtype=float)))




song_list_topics=song_list.join(doc_topic_df) 
song_list_topics_mt=song_list_topics.join(main_topic_df)



#top songs per topic (for use in word clouds)
top_songs=pd.DataFrame()
for i in range(0,25):
    temp=song_list_topics[['artist_name_x','track_name_x', i]].sort([i], ascending=[0]).head(3)
    temp.columns = ['artist', 'song', 'perc_top']
    temp['topic']=i
    top_songs=pd.concat([top_songs,temp])
top_songs.to_csv("/Users/home/Documents/data/Evolution of Pop/top_songs_per_topic.tsv", sep='\t')
top_songs 


#join datasets

m1=pd.merge(doc_topic_df, total_words_df, left_index=True, right_index=True)
m2=pd.merge(m1, song_vocab_df, left_index=True, right_index=True)

predictors=np.array(m2) 


#split into train and test set
y_train, y_test, x_train, x_test = train_test_split(genres, predictors, test_size=0.33)


#perform lda on train set
clf = LDA()
clf.fit(x_train, y_train)
#predict on test set
y_pred=clf.predict(x_test)

#measure accuracy of test predictions
cm = confusion_matrix(y_test, y_pred)
accuracy_score(y_test, y_pred, normalize=False)





