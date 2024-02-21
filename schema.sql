create table posts (
    id serial primary key,
    author varchar(15) not null,
    content varchar(256),
    place text,
    time timestamp with time zone not null default current_timestamp
);
