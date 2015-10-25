
import pandas as pd
import re
from stop_words import get_stop_words
import numpy as np
import lda

#import filter to found lyrics

lyrics=pd.DataFrame.from_csv('scraped_lyrics.tsv', sep='\t', index_col=False)
found_lyrics=lyrics[lyrics['lyrics']!='Lyrics Not found']


#data prep
#cleaning

#lower case
clean= found_lyrics['lyrics'].str.lower()

#reference to verse and chorus
clean = clean.str.replace('chorus:','')
clean = clean.str.replace('verse:','')

#new line breaks
clean = clean.str.replace('\n', ' ')
clean = clean.str.replace('\r', ' ')

#untranslated symbols
clean = clean.str.replace('amp', ' ')
clean = clean.str.replace('quot', ' ')

#stuff like repeat 5x
clean = clean.str.replace(r'[\d]x','')

#verse and chorus references
clean = clean.str.replace(r'verse [\d]','')

#keep words whitespace and '
clean = clean.str.replace(r'[^\w\s\']','')

clean=clean.str.replace(r'[\d]','')


#split lyrics into words
words=clean.str.split()




#clean out stop words, perform stemming? and form vocab
stop_words_eng=get_stop_words('english')
stop_words_fr=get_stop_words('french')
stop_words_sp=get_stop_words('spanish')

stop_words=stop_words_eng+stop_words_fr+stop_words_sp


NOISE_WORDS = [
    "a","an", "an'", "about","above","ain't","aint", "all","along","also","although","am","an","any","are","aren't", "away",
    "as","at","ay", "back", "be","because","'cause","cause", "bit", "been","but","by","can", "can't", "cant","cannot","could","couldn't","come","comes","cuase", "chorus", 
    "did","didn't","do","does","doesn't","don't","dont", "em'","else", "e.g.","either","etc","etc.","even","ever","every",
    "for","from","further","get","gets","give", "gives","going", "goin'", "goes", "go","gonna", "gotta", "got","had","hardly","has","hasn't","having","he",
    "hence","her","here","hereby","herein","hereof","hereon","hereto","herewith","him",
    "his","how","however","i","i'll", "ill", "im'","im", "i.e.","if","into","it","it's","its","just", "know", "ic", "lyricchecksum", "lyricid", "like","let", "make", "me","more","most",
    "mr","my","near","nor","now","of", "ok","on", "one","onto","other","our","out","over","put", "really",
    "said","same", "say","see", "she","should","shouldn't","since","so","some","such","take", "than","that","thats", "that's",
    "the","their","them","then","there","thereby","therefore","therefrom","therein","tell",
    "thereof","thereon","thereto","therewith","these","they","this","those","through", "thing","try",
    "thus","to","too","under","until","till'", "unto","upon","us","very","viz","want", "was", "wasn't", "wanna", "whatcha", "way",
    "we","went","were","what","when","where","whereby","wherein","whether","which","while", "will", "well", "wit",
    "who","whom","whose","why","with","without","would","x", "you","your","you're", "youre", "y'all", "verse", "repeat", "chorus"
]

lyricisms=["oh","ohh","ooh", "ah", "ahh", "yeah","yes", "u", "mmm", "uh", "hey", "la", "na", "yo", "ya", "yeh", 
"woah","whoa", "huh", "woah", "yea", "doo", "de", "nah", "da", "ha", "ba", "wo", "wow", "woo", "ooo", "dee", "dum", "hmm"]

remove_words=stop_words+NOISE_WORDS+lyricisms


filtered_words=[]
vocab=[]
total_words=[]
song_vocab=[]

#for each song
for i in words.index:
    #extract all words
    word_list=words[i]
    #find total number of words in song
    total_words.append(len(word_list))
    #find distinct words i.e. vocab of song
    song_vocab.append(len(list(set(word_list))))
    #filter out the stop words   
    filtered = [word for word in word_list if word not in remove_words]
    #filter out the stop words and stem - i didn't like the stemming
    #filtered = [stem(word) for word in word_list if word not in remove_words]
    #store words for later processing
    filtered_words.append(filtered)
    #identify unique list
    unique=list(set(filtered))
    #add to a total list of vocabulary for whole corpus
    new_words = [word for word in unique if word not in vocab]
    vocab=vocab+new_words
vocab=sorted(vocab)

clean_vocab=vocab[622:]


#transpose and count freq
words_freq=[]
for l in range(0,len(filtered_words)):
    word_list=filtered_words[l]
    freq=[]
    for v in clean_vocab:
        count=word_list.count(v)
        freq.append(count)
    words_freq.append(freq)

word_freq_array=np.array(words_freq)     


clean_vocab=tuple(clean_vocab)
titles = tuple(lyrics['track_name'])


#popular lyrics - useful to improve my remove_words list
sums=[sum(i) for i in zip(*words_freq)]
np.array(clean_vocab)[np.argsort(np.array(sums))][:-200:-1]



#modeling part how many topics

for topics in range(1,41):
    #define and fit model
    print(topics)
    model = lda.LDA(n_topics=topics, n_iter=1500, random_state=1)
    model.fit(word_freq_array)

    #work out top words in each topic
    topic_word = model.topic_word_
    n_top_words = 20
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(clean_vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
        print('Topic {}: {}'.format(i, ' '.join(topic_words)))





#modeling part

#define and fit final model
model = lda.LDA(n_topics=25, n_iter=1500, random_state=1)
model.fit(word_freq_array)


#work out top words in each topic
topic_word = model.topic_word_
n_top_words = 20
for i, topic_dist in enumerate(topic_word):
    topic_words = np.array(clean_vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
    print('Topic {}: {}'.format(i, ' '.join(topic_words)))


#work out top topics in each document
#doc topic will be main info for output. join against time and produce graphs
doc_topic = model.doc_topic_
n_top_topics=4
topic_num_list=range(0,20)
for i in range(10):
    top_topics=np.array(topic_num_list)[np.argsort(doc_topic[i])][:-n_top_topics:-1]
    perc=sorted(doc_topic[i]*100)[:-n_top_topics:-1]
    perc_form = ["%.0f" % member for member in perc]
    print("{} (top topics: {})(topic_perc: {})".format(titles[i], top_topics, perc_form)) 


#main topic per song
main_topic=[]
topic_num_list=range(0,25)
for i in range(len(filtered_words)):
    main_temp=np.array(topic_num_list)[np.argsort(doc_topic[i])][:-2:-1]
    main_topic.append(main_temp[0])
main_topic  


#song ids
song_id=np.array(found_lyrics.index)

#save results
np.save('doc_topic', doc_topic)
np.save('total_words', np.array(total_words))
np.save('song_vocab', np.array(song_vocab))
np.save('main_topic', np.array(main_topic))
np.save('song_id', song_id)
np.save('topic_word', topic_word)
np.save('word_freq_array', word_freq_array)
np.save('clean_words', clean_words)





  




































