-- FLIGHT BOOKING

CREATE TABLE public.fly_booking
(
    id varchar NOT NULL,
    client_name varchar NOT NULL,
    fly_number varchar NOT NULL,
    "from" varchar NOT NULL,
    "to" varchar NOT NULL,
    "date" date NULL,
    CONSTRAINT fly_booking_pk PRIMARY KEY (id)
);
CREATE UNIQUE INDEX fly_booking_id_idx ON public.fly_booking (id);


INSERT INTO public.fly_booking
    (id,client_name,fly_number,"from","to","date")
VALUES
    ('124g', 'Ihor', 'mh10', 'Lviv', 'Obroshyno', '2020-03-01');

-- HOTEL BOOKING
CREATE TABLE public.hotel_booking
(
    id varchar NOT NULL,
    client_name varchar NOT NULL,
    hotel_name varchar NOT NULL,
    arrival date NOT NULL,
    depature date NOT NULL,
    CONSTRAINT hotel_booking_pk PRIMARY KEY (id)
);
CREATE UNIQUE INDEX hotel_booking_id_idx ON public.hotel_booking (id);


INSERT INTO public.hotel_booking
    (id,client_name,hotel_name,arrival,depature)
VALUES
    ('Abracad', 'Ihor', 'Hilton', '2020-03-01', '2020-03-01');

-- ACCOUNT

CREATE TABLE public.account
(
    id varchar NOT NULL,
    client_name varchar NOT NULL,
    amount int NOT NULL,
    CONSTRAINT account_pk PRIMARY KEY(id),
    CONSTRAINT account_check CHECK (amount>=0)
);
CREATE UNIQUE INDEX account_id_idx ON public.account (id);

INSERT INTO public.account
    (id,client_name,amount)
VALUES
    ('grego', 'Ihor', 150);
ON CONFLICT (id) 
DO
    UPDATE
    SET amount=100

UPDATE public.account
SET amount=100
WHERE id='grego';


