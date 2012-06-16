drop table if exists tags;
drop table if exists quotes;
drop table if exists connections;

create table tags (
  id integer primary key autoincrement,
  tag string unique not null
);

create table quotes (
  id integer primary key autoincrement,
  quote string unique not null
);

create table connections (
  id integer primary key autoincrement,
  qid integer not null,
  tid integer not null
);
