create table categories (
	id int,
	category text
);

create table vocabulary (
	categoryid int references category(id),
	lang1translation text,
	lang2translation text
);

