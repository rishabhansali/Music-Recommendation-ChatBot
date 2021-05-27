# -*- coding: utf-8 -*-
"""
Created on Tue May  4 21:15:40 2021
"""

import pandas as pd
from .OOPapproach import *
import base64
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')


def getSong(userinput):
    song_artist_list = []
    user_search_list = []
    # score = SentimentIntensityAnalyzer().polarity_scores(mood)
    # if score['compound'] >= 0.05:
    #     # st.success('Positive Sentiment Detected')
    #     sentiment = 'Positive'
    # elif -0.05 < score['compound'] < 0.05:
    #     # st.info('Neutral Sentiment Detected')
    #     sentiment = 'Neutral'
    # elif score['compound'] <= -0.05:
    #     # st.error('Negative Sentiment Detected')
    #     sentiment = 'Negative'

        # userinput = st.text_input("Enter a song you would like to get recommendations for: ")
    userinput = userinput.lower()
    res = ("Your song is: " + userinput + "<br />")

    song_df_normalised = pd.read_csv("song_df_normalised.csv")

    try:
        song_name = \
            song_df_normalised[song_df_normalised['song_artist'].str.contains(userinput)]['song_artist'].tolist()[0]

    except IndexError:
        # print("Sorry!! We couldnt get any results for", userinput, " :( ")
        string = "Sorry!! We couldn't get any results for " + str(userinput) + " :("
        res += string

    else:
        result = 'success'
        song_artist_list = []
        artist_list = []
        song_name_list = song_df_normalised[song_df_normalised['song_artist'].str.contains(userinput)][
            'track_name'].tolist()
        artist_list = song_df_normalised[song_df_normalised['song_artist'].str.contains(userinput)][
            'track_artist'].tolist()

        # for i in range(len(song_name_list)):
        #    song_artist_list.append(song_name_list[i]+" by "+artist_list[i])
        user_search_list = [i + " by " + j for i, j in zip(song_name_list, artist_list)]
        song_artist_list = [i + " -> " + j for i, j in zip(song_name_list, artist_list)]
        res += "Choose your song: <br />"
        j = 0
        for i in user_search_list:
            j += 1
            res += str(j) + ". " + i + "<br />"
    return res, song_artist_list, user_search_list


def songrecommender(track, userinput, id, song_artist_list):
    # print(sentiment)
    song_name_list = song_df_normalised[song_df_normalised['song_artist'].str.contains(userinput)][
        'track_name'].tolist()
    artist_list = song_df_normalised[song_df_normalised['song_artist'].str.contains(userinput)][
        'track_artist'].tolist()
    if track.isdigit():
        x = int(track) - 1
        # print(x)
        if x not in range(len(song_name_list)):
            res = "Sorry, invalid choice :("
        else:
            song_name = song_name_list[x]

            res = "Song from dataset: " + song_name + "<br />"
            artist_name = artist_list[x]
            res += "Artist name: " + artist_name + "<br />"

            genre = song_df_normalised[
                (song_df_normalised['track_name'] == song_name) & (song_df_normalised['track_artist'] == artist_name)][
                'playlist_genre'].tolist()[0]

            subgenre = song_df_normalised[
                (song_df_normalised['track_name'] == song_name) & (song_df_normalised['track_artist'] == artist_name)][
                'playlist_subgenre'].tolist()[0]
            sentiment = song_df_normalised[
                (song_df_normalised['track_name'] == song_name) & (song_df_normalised['track_artist'] == artist_name)][
                'sentiment'].tolist()[0]
            #st.info(sentiment)

            x = song_df_normalised[
                (song_df_normalised['track_name'] == song_name) & (song_df_normalised['track_artist'] == artist_name)][
                'links'].tolist()[0]
            res += "<iframe width = \"100%\"height = \"150\"src = \"https://w.soundcloud.com/player/?url=" + x + "&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true\" ></iframe>"

            sentiment = streamhistory(id, song_artist_list[int(track) - 1], sentiment)
            getartistsongs(artist_name, song_name)

            getsongsgenre(genre, song_name)
            getsongsubgenre(subgenre, song_name)

            getsimilarsongs(song_name)
            output = display()
            # outputlist = list(set(output))

            artist_list2 = []
            for i in range(len(output)):
                artist_list2.append(
                    song_df_normalised[song_df_normalised['track_name'] == output[i]]['track_artist'].tolist()[0])

            song_artist_output = [i + " by " + j for i, j in zip(output, artist_list2)]

            sentiment_list = []
            popularity_list = []
            links = []

            for i in range(len(output)):
                sentiment_list.append(song_df_normalised[(song_df_normalised['track_name'] == output[i]) & (
                        song_df_normalised['track_artist'] == artist_list2[i])]['sentiment'].tolist()[0])
                popularity_list.append(song_df_normalised[(song_df_normalised['track_name'] == output[i]) & (
                        song_df_normalised['track_artist'] == artist_list2[i])]['track_popularity'].tolist()[0])
                links.append(song_df_normalised[(song_df_normalised['track_name'] == output[i]) & (
                        song_df_normalised['track_artist'] == artist_list2[i])]['links'].tolist()[0])

            d = {'songs': song_artist_output, 'sentiment': sentiment_list, 'popularity': popularity_list, 'links': links}
            song_sentiment = pd.DataFrame(data=d)
            # print(song_sentiment)

            if sentiment == 'Positive':
                song_sentiment.sort_values(by=['sentiment', 'popularity'], ascending=[False, False], inplace=True)
            if sentiment == 'Negative':
                song_sentiment.sort_values(by=['sentiment', 'popularity'], ascending=[True, False], inplace=True)

            # print(song_sentiment)
            song_artist_output = song_sentiment['songs'].tolist()
            n = len(song_artist_output)
            res += "<br /><br /><center><u><b>RECOMMENDATIONS FOR YOU</b></u></center>"
            c = 0
            for i in range(song_sentiment.shape[0]):
                c += 1
                res += "<br /><p>" + str(c) + " : " + song_sentiment.at[i, 'songs'] + "</p>"
                res += "<iframe width = \"100%\"height = \"100\"scrolling = \"no\"frameborder = \"no\"allow = " \
                       "\"autoplay\"src = \"https://w.soundcloud.com/player/?url=" + \
                       song_sentiment.at[
                           i, "links"] + "&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true" \
                                         "&show_user=true&show_reposts=false&show_teaser=true&visual=true\" > </iframe>" \
                       + "<br /> "
            # print(res)
            clearlist()
    else:
        res = "Invalid choice :("
    return res


def main():
    songrecommender()


if __name__ == '__main__':
    main()
