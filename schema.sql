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
    geog geography(point,4326),
    time timestamp with time zone not null default current_timestamp,
    foreign key (user_id) references users (id)
);

create table users (
    id serial primary key,
    name varchar(15) not null,
    email text,
    img text
);

insert into users (name, email, img) values (%s,%s,%s);

insert into posts2 (user_id, content, img, geog) values (%s, %s, %s, ST_MakePoint(%s,%s)),
 (id, fd["create-text"], imgBin, fd["create-long"], fd["create-lat"])

update users set name = %s, img = %s where email = %s;

select ST_AsText(geog) from posts2;

select id, user_id, content, encode(img::bytea, 'base64') as "img", (ST_X(ST_AsText(geog)), ST_Y(ST_AsText(geog))) as "geog", time from posts2;

select posts2.id, posts2.user_id, posts2.content, encode(posts2.img::bytea, 'base64') as "img", (ST_X(ST_AsText(posts2.geog)), ST_Y(ST_AsText(posts2.geog))) as "geog", posts2.time, users.name from posts2 inner join users on posts2.user_id=users.id order by posts2.time desc;

select posts2.id, posts2.user_id, posts2.content, encode(posts2.img::bytea, 'base64') as "img", (ST_X(ST_AsText(posts2.geog)), ST_Y(ST_AsText(posts2.geog))) as "geog", posts2.time, users.name from posts2 inner join users on posts2.user_id=users.id order by ST_Distance(posts2.geog,ST_MakePoint(%s,%s));