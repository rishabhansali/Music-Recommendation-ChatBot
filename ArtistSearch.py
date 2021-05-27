# -*- coding: utf-8 -*-

import pandas as pd
from .OOPapproach import *
from .SongRecommendation import *
import base64
from nltk.sentiment.vader import SentimentIntensityAnalyzer

artist_list = []


def getArtist(userinput):
    res = ""
    global artist_list
    userinput = userinput.lower()
    res += "Your artist is: " + userinput + "<br />"

    song_df_normalised = pd.read_csv("static/song_df_normalised.csv")

    try:
        artist = \
            song_df_normalised[song_df_normalised['track_artist'].str.contains(userinput)]['track_artist'].tolist()[0]

    except IndexError:
        res += "No result :("

    else:
        artist_list = song_df_normalised[song_df_normalised['track_artist'].str.contains(userinput)][
            'track_artist'].tolist()

        artist_list = list(set(artist_list))
        res += "Choose your artist:<br />"
        c = 0
        for i in artist_list:
            c += 1
            res += str(c) + ". " + i + "<br />"
    return res


def artistsearch(userinput):
    res = ""
    userinput = userinput.strip()
    if userinput.isdigit():
        if int(userinput) - 1 not in range(len(artist_list)):
            res += "Sorry, invalid choice :("
        else:
            artist_name = artist_list[int(userinput) - 1]

            res += "Top songs for <u>" + artist_name + "</u><br /><br />"

            artist_song_df = song_df_normalised[song_df_normalised['track_artist'] == artist_name]
            artist_song_df = artist_song_df.sort_values('track_popularity', ascending=False)
            artist_song_list = artist_song_df['track_name'].to_list()

            n = len(artist_song_list)
            if n > 10:
                n = 5
            for i in range(n):
                c = i + 1
                res += str(c) + " : " + artist_song_list[i]
                x = song_df_normalised[(song_df_normalised['track_name'] == artist_song_list[i]) & (
                        song_df_normalised['track_artist'] == artist_name)]['links'].tolist()[0]
                res += "<iframe width = \"100%\"height = \"100\"src = \"https://w.soundcloud.com/player/?url=" + x + "&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true\" ></iframe><br />"
            artist_song_list.clear()
    else:
        res += "Invalid choice :("
    return res


if __name__ == '__main__':
    main()
