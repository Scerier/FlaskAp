create table if not exists mainmenu (
id integer primary key autoincrement,
title text not null,
url text not null
);

create table if not exists posts (
id integer primary key autoincrement,
title text not null,
url text not null,
text text not null,
time integer not null
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB DEFAULT NULL,
time integer NOT NULL
);

