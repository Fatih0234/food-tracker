drop table if exists log_date;
drop table if exists food_log;
drop table if exists food;

create table log_date (
    id integer primary key autoincrement, 
    entry_date datetime default current_timestamp
);

create table food (
    id integer primary key autoincrement,
    name text not null,
    protein integer not null,
    carbohydrates integer not null,
    fat integer not null,
    calories integer not null
);

create table food_log (
    log_id integer not null ,
    food_id integer not null,
    primary key(log_id, food_id)
);
