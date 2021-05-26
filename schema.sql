drop table if exists users;
    create table users (
    id integer primary key autoincrement,
    name varchar(50) not null,
    username varchar(255) not null,
    password varchar(50) not null
);