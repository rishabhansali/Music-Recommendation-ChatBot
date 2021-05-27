# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import pandas as pd
import random
from statistics import mode
from statistics import StatisticsError
from scipy.sparse import csr_matrix
from .database import insertUserHist, insertUser, retrieveUserHistory, retrieveUsers, retrieveSentiment
import pickle


def personalplaylist(user_id):
    response = ""
    pickle_in = open("nn_model2.pkl", "rb")
    model_nn = pickle.load(pickle_in)
    # history = pd.read_csv("datasets/streaminghistory.csv")
    song_df_normalised = pd.read_csv('static/song_df_normalised.csv')

    history = retrieveSentiment(user_id)
    # in case user is new, then we dont let them access this feature until they serach for a song
    #    try:
    #        sentiment_history =history[history['user'] == username]['song_sentiment'].tolist()[0]

    #    except IndexError:
    #        st.info("please play a few songs before accessing this feature")
    #    else:
    #        sentiment_history = sentiment_history.split(",")

    #        try:
    #            mode(sentiment_history)
    #        except StatisticsError:
    #            print('Positive')
    #            sentiment = 'Positive'
    #        else:
    #            print(mode(sentiment_history))
    #            sentiment =  mode(sentiment_history)

    if history:
        # print(history)

        playlist = []
        sentiment_list = []
        song_artist_list = []
        timestamp_list = []
        for i in history:
            # print(user)
            # song_list = user[0][2]
            sentiment_list.append(i[3])
            song_artist_list.append(i[2])
            timestamp_list.append(i[4])
        # print("Hello:", sentiment_list)

        try:
            mode(sentiment_list[-3:])
        except StatisticsError:
            # print('Neutral')
            sentiment_history = 'Neutral'
        else:
            # print(mode(sentiment_list[:3]))
            sentiment_history = mode(sentiment_list[-3:])

        song_artist_list_freq = []
        for w in song_artist_list:
            song_artist_list_freq.append(song_artist_list.count(w))
        song_freq = []

        for i in range(len(list(zip(song_artist_list, song_artist_list_freq)))):
            if list(zip(song_artist_list, song_artist_list_freq, timestamp_list))[i] not in song_freq:
                song_freq.append(list(zip(song_artist_list, song_artist_list_freq, timestamp_list))[i])
        # print(song_freq)
        song_freq.sort(key=lambda x: (x[1], x[2]), reverse=True)
        # print(song_freq)
        unique_songs = []
        for i in song_freq:
            u = []
            for j in unique_songs:
                u.append(j[0])
            if i[0] not in u:
                unique_songs.append((i[0], i[1], i[2]))
        # print("Hi: ",unique_songs)
        song_freq = unique_songs

        # song_freq = sorted(song_freq, key = lambda x:(x[1],x[2]), reverse=True)
        # sorted(unsorted, key=lambda element: (element[1], element[2]))

        song_list = []
        song_artist = []
        song = ""
        artist = ""
        a = 0
        for i in range(len(song_freq[:3])):
            print(song_freq[i][0])
            song_list.append(song_freq[i][0].split("->")[0].strip())
            song_artist.append(song_freq[i][0].split("->")[1].strip())
        song_by_artist = [i + " " + j for i, j in zip(song_list, song_artist)]

        # recommending similar songs based on songs listened by user

        for i in range(len(song_by_artist)):
            # song_df_normalised = song_df_normalised[song_df_normalised['sentiment'] == sentiment]
            # print(len(song_by_artist))
            song_features = song_df_normalised.set_index("song_artist")
            # song_features.drop("Unnamed: 0",axis=1,inplace=True)
            song_features.drop(['track_artist', 'lyrics', 'track_album_name', 'track_popularity',
                                'playlist_name', 'playlist_genre', 'playlist_subgenre', 'language', 'sentiment',
                                'track_name', 'links'], axis=1, inplace=True)
            # song_features.head()
            song_features_csr = csr_matrix(song_features.values)
            # model_nn = NearestNeighbors(metric='cosine',algorithm='brute')
            model_nn.fit(song_features_csr)

            temp = song_features.copy()
            temp.reset_index(inplace=True)
            # print(temp)
            print(song_by_artist)
            songsearch = song_by_artist[i]
            songsearch = songsearch.lower()
            # print(song_by_artist[i], i)
            if temp[temp['song_artist'] == song_by_artist[i]] is not None:
                song_index = temp.index[temp['song_artist'] == song_by_artist[i]].tolist()[0]
                # print(song_index)
                # print(song_features.index[song_index])
                distances, indices = model_nn.kneighbors(X=song_features.iloc[song_index, :].values.reshape(1, -1),
                                                         n_neighbors=11)

                for i in range(1, 11):
                    if song_features.index[indices.flatten()[i]] not in playlist:
                        playlist.append(song_features.index[indices.flatten()[i]])

                ## DEALING WITH ARTISTS
                artist_list = []
                artist_freq = []
                for i in range(len(song_artist_list)):
                    artist_list.append(song_artist_list[i].split('->')[1].strip())

                for w in artist_list:
                    artist_freq.append(artist_list.count(w))

                artist_freq_count = []

                for i in range(len(list(zip(artist_list, artist_freq)))):
                    if list(zip(artist_list, artist_freq, timestamp_list))[i] not in artist_freq_count:
                        artist_freq_count.append(list(zip(artist_list, artist_freq, timestamp_list))[i])
                artist_freq_count.sort(key=lambda x: x[1], reverse=True)
                # print(artist_freq_count)
                unique_songs = []
                for i in artist_freq_count:
                    u = []
                    for j in unique_songs:
                        u.append(j[0])
                    if i[0] not in u:
                        unique_songs.append((i[0], i[1], i[2]))
                # print(unique_songs)
                artist_freq_count = unique_songs
                # print(artist_freq_count)

        for i in range(len(artist_freq_count[:3])):
            df = song_df_normalised[(song_df_normalised['track_artist'] == artist_freq_count[i][0])].sort_values(
                'track_popularity',
                ascending=False)
            playlist = playlist + df['song_artist'].tolist()[:10]
            # print(playlist)

        random.shuffle(playlist)
        c = 0
        response += "<br /><center><u><b>YOUR PERSONALIZED PLAYLIST  </u></center><br />"
        for i in playlist:
            if c < 10:
                c = c + 1
                response += str(c) + " : " + i
                # print(response)
                x = song_df_normalised[(song_df_normalised['song_artist'] == i)]['links'].tolist()[0]
                response += "<iframe width = \"100%\"height = \"120\"scrolling = \"no\"frameborder = \"no\"allow = " \
                            "\"autoplay\"src = \"https://w.soundcloud.com/player/?url=" + \
                            x + "&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true" \
                                "&show_user=true&show_reposts=false&show_teaser=true&visual=true\" > </iframe>" \
                            + "<br /> "
            else:
                break
    else:
        response = "Play a few songs before you can access this feature"
    return response


def main():
    personalplaylist()


if __name__ == '__main__':
    main()
