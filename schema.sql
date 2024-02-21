create table posts (
    id serial primary key,
    author varchar(15) not null,
    content varchar(256),
    place point
    time timestamp with time zone not null default current_timestamp
);

create table posts2 (
    id serial primary key,
    user_id int,
    content varchar(256),
    img bytea,
    geog geography,
    time timestamp with time zone not null default current_timestamp,
    foreign key (user_id) references users (id)
);

create table users (
    id serial primary key,
    name varchar(15) not null,
    email text,
    img text
);