# -*- coding: utf-8 -*-

import pandas as pd
from .OOPapproach import *
from .SongRecommendation import *
import base64
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def genresearch():
    res = ""
    song_df_normalised = pd.read_csv("song_df_normalised.csv")
    genre_list = song_df_normalised['playlist_subgenre'].unique().tolist()
    res += "Choose your Genre<br />"
    j = 0
    for i in genre_list:
        j += 1
        res += str(j) + ". " + i + "<br />"
    return res


def genre_recommend(option):
    res = ""
    song_df_normalised = pd.read_csv("song_df_normalised.csv")
    genre_list = song_df_normalised['playlist_subgenre'].unique().tolist()
    if option.isdigit():
        if int(option)-1 not in range(len(genre_list)):
            res += "Sorry, invalid choice :("
        else:
            genre_name = genre_list[int(option) - 1]

            res += "Top songs for <u>" + genre_name + "</u><br /><br />"

            genre_song_df = song_df_normalised[song_df_normalised['playlist_subgenre'] == genre_name]
            genre_song_df = genre_song_df.sort_values('track_popularity', ascending=False)
            genre_list = genre_song_df['track_name'].to_list()
            genre_artist_list = genre_song_df['track_artist'].to_list()

            genre_song_list = [i + " by " + j for i, j in zip(genre_list, genre_artist_list)]

            n = len(genre_song_list)
            if n > 10:
                n = 5
            for i in range(n):
                c = i + 1
                res += str(c) + " : " + genre_song_list[i]
                x = song_df_normalised[(song_df_normalised['track_name'] == genre_list[i]) & (
                        song_df_normalised['track_artist'] == genre_artist_list[i])]['links'].tolist()[0]
                res += "<iframe width = \"100%\"height = \"100\"src = \"https://w.soundcloud.com/player/?url=" + x + "&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true\" ></iframe><br />"
            genre_song_list.clear()
    else:
        res+="Invalid choice :( (Give choice in numbers)"

    return res


def main():
    genresearch()


if __name__ == '__main__':
    main()
