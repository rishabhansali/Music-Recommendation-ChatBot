import re
import pandas as pd
from flask import Flask, render_template, jsonify, request, url_for, redirect, session, g

from ArtistSearch import artistsearch, getArtist
from GenreSearch import genresearch, genre_recommend
from Playlist import personalplaylist
from SongRecommendation import getSong, songrecommender
from database import retrieveSentiment, retrieveUsers, retrieveUserHistory, insertUserHist, insertUser, set_list, \
    get_list
from processor import chatbot_response
import sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = 'enter-a-very-secretive-key-3479373'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

con = sqlite3.connect('MARC')
cur = con.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS users(id integer primary key autoincrement,name varchar(50) not null,username varchar(255) not null,password varchar(50) not null);")
cur.execute(
    "CREATE TABLE IF NOT EXISTS history(id integer primary key autoincrement, user_id integer not null, song text not null,sentiment varchar(50) not null, htime datetime, FOREIGN KEY (user_id) REFERENCES users(id));")
cur.execute(
    "create table if not exists input(user_id integer, userinput text, FOREIGN KEY (user_id) REFERENCES users(id));")
cur.execute("create table if not exists list(user_id integer, list text, FOREIGN KEY (user_id) REFERENCES users(id));")

con.commit()
con.close()


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'flag' not in session:
        session["flag"] = 0
        return redirect(url_for('login'))

    elif session['flag'] == 1:
        session["flag"] = 0
        return redirect(url_for('login'))
    else:
        con = sqlite3.connect('MARC')
        cur = con.cursor()
        if 'username' not in session:
            msg = ''
            redirect(url_for('login'))
            if request.method == 'POST' and 'username' in request.form and 'pass' in request.form:
                username = request.form['username']
                password = request.form['pass']
                print(request.form)
                if username == "admin" and password == "admin":
                    session['username'] = username
                    cur.execute("select count(*) FROM users")
                    rows = cur.fetchall()
                    # print(rows)
                    return render_template("/dash.html", data=rows[0][0])
                else:
                    con = sqlite3.connect('MARC')
                    cur = con.cursor()
                    cur.execute("select * FROM users WHERE username=? and password=?", (username, password))
                    rows = cur.fetchall()
                    if rows:
                        session['loggedin'] = True
                        session['id'] = rows[0][0]
                        session['name'] = rows[0][1]
                        session['username'] = username
                        session['songs'] = 0
                        session['artist'] = 0
                        session['genre'] = 0
                        session['text'] = 0
                        session['track'] = 0
                        session['option'] = 0
                        session['play'] = 0
                        session['choose'] = 0
                        msg = 'Logged in successfully !'
                        return render_template('index.html', msg=msg, data=session['name'])
                    else:
                        msg = 'Incorrect username / password !'
            return render_template('login.html', msg=msg)
        elif session['username'] == "admin":
            session['username'] = "admin"
            cur.execute("select count(*) FROM users")
            rows = cur.fetchall()
            # print(rows)
            return render_template("/dash.html", data=rows[0][0])
        con.close()
        session['songs'] = 0
        session['artist'] = 0
        session['genre'] = 0
        session['text'] = 0
        session['track'] = 0
        session['option'] = 0
        session['play'] = 0
        session['choose'] = 0
        return render_template('index.html', data=session['name'])
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session['flag'] == 1:
        session["flag"] = 0
        return redirect(url_for('login'))
    else:
        if 'username' not in session:
            msg = ''
            if request.method == 'POST' and 'username' in request.form and 'pass' in request.form and 'name' in request.form:
                name = request.form['name']
                validate = re.fullmatch('[A-Za-z]{2,25}( [A-Za-z]{2,25})*', name)
                username = request.form['username']
                password = request.form['pass']
                # print(username)
                request.form = {}
                con = sqlite3.connect('MARC')
                cur = con.cursor()
                cur.execute("select * FROM users WHERE username=?", (username,))
                rows = cur.fetchall()
                con.close()
                if rows:
                    msg = 'Account already exists !'
                elif not re.fullmatch(r'[A-Za-z]{2,25}( [A-Za-z]{2,25})*', name):
                    msg = 'Name must contain only characters!'
                elif not re.match(r'[A-Za-z0-9]+', username):
                    msg = 'Username must contain only characters and numbers !'
                elif not username or not password or not name:
                    msg = 'Please fill out the form !'
                else:
                    insertUser(name, username, password)
                    success = 'You have successfully registered. Please Login!'
                    return render_template('login.html', success=success)
            elif request.method == 'POST':
                msg = 'Please fill out the form !'
            return render_template('register.html', msg=msg)
        return redirect(url_for('login'))
    return render_template('register.html', msg=msg)


@app.route("/users", methods=['GET', 'POST'])
def users():
    if session['flag'] == 1:
        session["flag"] = 0
        return redirect(url_for('login'))
    elif 'username' in session:
        if session["username"] == "admin":
            users = retrieveUsers()
            print(request.args)
            if 'id' in request.args:
                print(request.args.get('id'))
                hist = retrieveUserHistory(request.args.get('id'))
                return render_template("tables.html", data=users, hist=hist)
            return render_template("tables.html", data=users)
    return redirect(url_for('login'))


# "http://i.stack.imgur.com/SBv4T.gif"
# songs = 0
# artist = 0
# genre = 0
# text = 0
# track = 0
# option = 0
# play = 0
# choose = 0
# userinput = ""
# sentiment = ""
# list = []
# l = []


@app.route('/chatbot', methods=["GET", "POST"])
def chatbotResponse():
    response = ""
    if request.method == 'POST' and 'chatbox' in request.form:
        postData = request.form
        # print(request.form)
        if request.form.getlist('reload'):
            session['songs'] = 0
            session['artist'] = 0
            session['genre'] = 0
            session['text'] = 0
            session['track'] = 0
            session['option'] = 0
            session['play'] = 0
            session['choose'] = 0
            return redirect(url_for('chatbotResponse'))
        else:
            g.question = request.form['chatbox']
            the_question = g.question
            # if track == 1:
            the_question = the_question.strip()

            if the_question.lower() == "search artist":
                session['artist'] = 1
                response = "Enter artist name"
            elif the_question.lower() == "search similar songs":
                session['songs'] = 1
                response = "Enter the song you want recommendations for"
            elif the_question.lower() == "search genre":
                session['genre'] = 1
                response = genresearch()
            elif the_question.lower() == "create playlist":
                session['text'] = 1
                response = personalplaylist(session['id'])
            elif the_question.lower() == "search song":
                session['play'] = 1
                response = "Enter song name"
            elif session['artist'] == 1:
                session['artist'] = 0
                response = getArtist(the_question)
                if response.find("No result :(") > -1:
                    session['option'] = 0
                else:
                    session['option'] = 1
            elif session['option'] == 1:
                session['option'] = 0
                response = artistsearch(the_question)
            elif session['genre'] == 1:
                session['genre'] = 0
                response = genre_recommend(the_question)
            elif session['songs'] == 1:
                session['songs'] = 0
                # global userinput
                userinput = the_question
                session['track'] = 1
                response, list, l = getSong(userinput)
                if response.find("Sorry!! We couldn't get any results for") > -1:
                    session['track'] = 0
                else:
                    set_list(session['id'], userinput, list)
            elif session['track'] == 1:
                userinput, list = get_list(session['id'])
                uinput=""
                l = []
                for i in userinput[0]:
                    uinput = i
                c=0
                print(the_question)
                for i in list:
                    print(c, i[0])
                    l.append(i[0])
                    c+=1

                response = songrecommender(the_question, uinput, session['id'], l)
                # response += "<div class=\"alert alert-info\"><strong>Enter 'Y' to get recommendations for another song.</strong>"
                session['track'] = 0
            elif session['play'] == 1:
                session['play'] = 0
                print("hi")
                session['choose'] = 1
                response, list, l = getSong(the_question)
                userinput = the_question
                if response.find("Sorry!! We couldn't get any results for") > -1:
                    session['choose'] = 0
                else:
                    set_list(session['id'], userinput, list)
            elif session['choose'] == 1:
                session['choose'] = 0
                userinput, list = get_list(session['id'])
                print(userinput)
                uinput=""
                for i in userinput[0]:
                    uinput = i
                song_df_normalised = pd.read_csv("static/song_df_normalised.csv")
                song_name_list = song_df_normalised[song_df_normalised['song_artist'].str.contains(uinput)][
                    'track_name'].tolist()
                artist_list = song_df_normalised[song_df_normalised['song_artist'].str.contains(uinput)][
                    'track_artist'].tolist()
                if the_question.isdigit():
                    x = int(the_question) - 1
                    # print(x)
                    if x not in range(len(song_name_list)):
                        response = "Sorry, invalid choice :("
                    else:
                        song_name = song_name_list[x]
                        print(list[0])
                        chosenSong = ""
                        for i in list[x]:
                            chosenSong = i
                        response = "Song from dataset: " + song_name + "<br />"
                        artist_name = artist_list[x]
                        sentiment = song_df_normalised[
                            (song_df_normalised['track_name'] == song_name) & (
                                    song_df_normalised['track_artist'] == artist_name)][
                            'sentiment'].tolist()[0]
                        insertUserHist(session["id"], chosenSong, sentiment)
                        response += "Artist name: " + artist_name + "<br />"
                        x = song_df_normalised[
                            (song_df_normalised['track_name'] == song_name) & (
                                    song_df_normalised['track_artist'] == artist_name)][
                            'links'].tolist()[0]

                        response += "<iframe width = \"100%\"height = \"200\"src = \"https://w.soundcloud.com/player/?url=" + x + "&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true\" ></iframe>"
                else:
                    response = "Invalid choice :("
            else:
                # print(the_question)
                response = chatbot_response(the_question)
            # print(response)
    else:
        session['songs'] = 0
        session['artist'] = 0
        session['genre'] = 0
        session['text'] = 0
        session['track'] = 0
        session['option'] = 0
        session['play'] = 0
        session['choose'] = 0
    del request.form
    return jsonify({"response": response})


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session['flag'] = 1
    session.pop('songs', None)
    session.pop('artist', None)
    session.pop('genre', None)
    session.pop('text', None)
    session.pop('track', None)
    session.pop('mood', None)
    session.pop('option', None)
    session.pop('play', None)
    session.pop('choose', None)
    return redirect(url_for('login'))


def getApp():
    return app


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
