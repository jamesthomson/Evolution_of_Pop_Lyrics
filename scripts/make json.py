
import pandas as pd
import numpy as np


#import filter to found lyrics

lyrics=pd.DataFrame.from_csv('scraped_lyrics.tsv', sep='\t', index_col=False)
found_lyrics=lyrics[lyrics['lyrics']!='Lyrics Not found']

df = pd.read_csv("/Users/home/Documents/data/Evolution of Pop/EvolutionPopUSA_MainData.csv", usecols=[0, 6, 10], header=0)

song_list=pd.merge(df, found_lyrics, how='inner', on=['recording_id', 'recording_id'])
genres=np.array(song_list['cluster'])

#load topics

doc_topic=np.load('/Users/home/Documents/data/Evolution of Pop/doc_topic.npy')
main_topic=np.load('/Users/home/Documents/data/Evolution of Pop/main_topic.npy')

doc_topic_df=pd.DataFrame(doc_topic)
main_topic_df=pd.DataFrame(main_topic)
main_topic_df.columns=['main_topic']

#join together

song_list_topics=song_list.join(doc_topic_df) 
song_list_topics_mt=song_list_topics.join(main_topic_df)

#all combinations of year and topics

dat={'year': range(1960,2010) * 25, 'main_topic': np.repeat(np.array(range(0,25)),50)}
topic_years=pd.DataFrame(dat,columns=['year', 'main_topic'])


main_topic_by_year=song_list_topics_mt.groupby(['main_topic', 'year']).size()
main_topic_by_year=main_topic_by_year.reset_index()

topic_year_final=pd.merge(topic_years, main_topic_by_year, how='left', on=['main_topic', 'year'])
topic_year_final=topic_year_final.fillna(0)

#json for stream graph version 1 - main topic frequency

json="var data=["
for i in range(0, len(topic_year_final)):
    topic=topic_year_final['main_topic'][i] 
    year=topic_year_final['year'][i] 
    freq=topic_year_final[0][i] 
    temp="{\"key\":\"Topic " + str(topic+1) + "\",\"date\":\"01/01/" + str(year) + "\",\"value\":\"" + str(freq) + "\"},"
    json=json+temp
print(json)


#json for stream graph version 2 - sum of topic percentages


topics_by_year=song_list_topics_mt.groupby(['year'])[range(0,25)].agg(['sum'])
topics_by_year=topics_by_year.reset_index()
topics_by_year

json="var data=["
for t in range(0,25):
    for y in range(0,50):
        year=topics_by_year['year'][y]
        value=topics_by_year[t]['sum'][y]
        temp="{\"key\":\"Topic " + str(t+1) + "\",\"date\":\"01/01/" + str(year) + "\",\"value\":\"" + str(value) + "\"},"
        json=json+temp
print(json)










#json for wordcloud
top_words=np.array(clean_vocab)[np.argsort(np.array(sums))][:-200:-1]
top_words_freq=np.array(sums)[np.argsort(np.array(sums))][:-200:-1]

json="var all = ["
for i in range(0,len(top_words)):
    temp= "{\"text\":\"" + top_words[i] + "\",\"size\":" + str(top_words_freq[i]/200) + "},"
    json=json+temp
json = json[:-1]    
json = json + "];"
print(json)



import math 
topic_word=np.load('/Users/home/Documents/data/Evolution of Pop/topic_word.npy')
n_top_words = 100
json=""
for i, topic_dist in enumerate(topic_word):
    temp_json="var t" + str(i+1) + " = ["
    topic_words = np.array(clean_vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
    topic_freq = np.array(topic_dist)[np.argsort(topic_dist)][:-n_top_words:-1]
    scalar= math.sqrt(topic_freq[0]/sum(topic_freq))*200/topic_freq[0]
    for w in range(0,len(topic_words)):
            temp= "{\"text\":\"" + topic_words[w] + "\",\"size\":" + str(round(topic_freq[w]*scalar)) + "},"
            temp_json=temp_json+temp
    temp_json = temp_json[:-1]
    temp_json = temp_json + "];\n"        
    json=json + temp_json   
print(json)   