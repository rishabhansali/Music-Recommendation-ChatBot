import sqlite3 as sql


def insertUser(name, username, password):
    con = sql.connect("MARC")
    cur = con.cursor()
    cur.execute("INSERT INTO users (name, username,password) VALUES (?,?,?)", (name, username, password))
    con.commit()
    con.close()


def retrieveUsers():
    con = sql.connect("MARC")
    cur = con.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    con.close()
    return users


def insertUserHist(user_id, song, sentiment):
    con = sql.connect("MARC")
    cur = con.cursor()
    cur.execute("INSERT INTO history(user_id, song , sentiment, htime) VALUES (?,?,?, datetime('now','localtime'))",
                (user_id, song, sentiment))
    con.commit()
    con.close()


def retrieveSentiment(user_id):
    con = sql.connect("MARC")
    cur = con.cursor()
    cur.execute("SELECT * FROM history where user_id=?", (user_id,))
    users = cur.fetchall()
    con.close()
    return users


def retrieveUserHistory(id):
    con = sql.connect("MARC")
    cur = con.cursor()
    cur.execute("SELECT name, song, sentiment, htime FROM history uh, users u where uh.user_id=u.id and uh.user_id=?",
                (id,))
    users = cur.fetchall()
    con.close()
    return users


def set_list(id, userinput, list):
    if list:
        con = sql.connect("MARC")
        cur = con.cursor()
        cur.execute("INSERT INTO input(user_id, userinput) VALUES (?,?)", (id, userinput))
        for i in list:
            cur.execute("insert into list values (?, ?)", (id, i))
        con.commit()
        con.close()


def get_list(id):
    con = sql.connect("MARC")
    cur = con.cursor()
    cur.execute("SELECT userinput FROM input where user_id=?", (id,))
    userinput = cur.fetchall()
    cur.execute("SELECT list FROM list where user_id=?", (id,))
    list = cur.fetchall()
    cur.execute("delete from input where user_id=?", (id,))
    cur.execute("delete from list where user_id=?", (id,))
    con.commit()
    con.close()
    return userinput, list
