#python 

import pandas as pd
import csv as csv
from urllib import urlopen
import time


df = pd.read_csv("EvolutionPopUSA_MainData.csv", usecols=[0, 1, 2, 3], header=0)


song_id=df_sample['recording_id'].tolist()
artist_list=df_sample['artist_name'].tolist()
song_list=df_sample['track_name'].tolist()

lyric_list=[]
song2_list=[]
artist2_list=[]


headers=['recording_id', 'artist_name','track_name','lyrics_artist', 'lyrics_track', 'lyrics']
f = open("scraped_lyrics.tsv", 'wt')
writer = csv.writer(f, delimiter='\t')
writer.writerow(headers)
f.close()


for a in range(len(artist_list)):
    
    time.sleep(20)
    
    artist=artist_list[a].replace(" ", "%20").lower()
    #clean up artist name
    if artist.find('%20ft%20')!=-1:
      artist=artist[0:artist.find('%20ft%20')]
    if artist.find('%20featuring%20')!=-1:
      artist=artist[0:artist.find('%20featuring%20')]
    if artist.find('%20with%20')!=-1:
      artist=artist[0:artist.find('%20with%20')]    

    song=song_list[a].replace(" ", "%20").lower()
    #clean up song name
    #if song.find('(')!=-1:
      #pre=song[:song.find('(')]
      #post=song[song.find(')')+1:]
      #song=pre+post

    song_url='http://api.chartlyrics.com/apiv1.asmx/SearchLyric?artist='+artist+'&song='+song
    urlout=urlopen(song_url).read()
    
    if urlout.find('<LyricChecksum>')<>-1:
          lyricchecksum=urlout[urlout.find('<LyricChecksum>')+15:urlout.find('</LyricChecksum>')]
          lyricid=urlout[urlout.find('<LyricId>')+9:urlout.find('</LyricId>')]
                  
          time.sleep(20)
          
          lyric_url='http://api.chartlyrics.com/apiv1.asmx/GetLyric?lyricId='+lyricid+'&lyricCheckSum='+lyricchecksum
          urlout2=urlopen(lyric_url).read()
          lyrics=urlout2[urlout2.find('<Lyric>')+7:urlout2.find('</Lyric>')]
          lyrics_track=urlout2[urlout2.find('<LyricSong>')+11:urlout2.find('</LyricSong>')]
          lyrics_artist=urlout2[urlout2.find('<LyricArtist>')+13:urlout2.find('</LyricArtist>')]
          
    
    if urlout.find('<LyricChecksum>')==-1:
          lyrics="Lyrics Not found"
          lyrics_track="Lyrics Not Found"
          lyrics_artist="Lyrics Not Found"
    
    out_list=[song_id[a],artist_list[a],song_list[a],lyrics_track,lyrics_artist,lyrics]          
    f = open("scraped_lyrics.tsv", 'a')
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(out_list)
    f.close()




