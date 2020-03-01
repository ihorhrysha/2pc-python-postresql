# main.py
import sys
import psycopg2
import datetime
import uuid

create_script = {
    'fly_booking': """CREATE TABLE public.fly_booking
(
    id varchar NOT NULL,
    client_name varchar NOT NULL,
    fly_number varchar NOT NULL,
    "from" varchar NOT NULL,
    "to" varchar NOT NULL,
    "date" date NULL,
    CONSTRAINT fly_booking_pk PRIMARY KEY(id)
);""",


    'fly_booking_index': """CREATE UNIQUE INDEX fly_booking_id_idx ON public.fly_booking(id)""",

    'hotel_booking': """CREATE TABLE public.hotel_booking
(
    id varchar NOT NULL,
    client_name varchar NOT NULL,
    hotel_name varchar NOT NULL,
    arrival date NOT NULL,
    depature date NOT NULL,
    CONSTRAINT hotel_booking_pk PRIMARY KEY(id)
)""",

    'hotel_booking_index': """CREATE UNIQUE INDEX hotel_booking_id_idx ON public.hotel_booking(id)""",

    'account': """CREATE TABLE public.account
(
    id varchar NOT NULL,
    client_name varchar NOT NULL,
    amount int NOT NULL,
    CONSTRAINT account_pk PRIMARY KEY(id),
    CONSTRAINT account_check CHECK (amount>=0)
);""",

    'account_index':  """CREATE UNIQUE INDEX account_id_idx ON public.account(id)""",

    'upsert_amount': """INSERT INTO public.account
    (id,client_name,amount)
VALUES
    ('grego', 'Ihor', %s)
ON CONFLICT (id)
DO
    UPDATE
    SET amount=EXCLUDED.amount"""
}


def connect_db(dbname, no_cursor=False):
    db_port = {
        "fly": '5431',
        "hotel": '5432',
        "account": '5433'
    }

    print('Connecting to '+dbname+'...')

    conn = psycopg2.connect(dbname=dbname, user='app',
                            password='secret', host='localhost', port=db_port.get(dbname))
    print('Connection esteblished')
    if(no_cursor):
        return conn
    else:
        return (conn, conn.cursor())


def close_connection(connection, cursor):
    print('Disconnecting fron '+connection.info.dbname+'...')
    cursor.close()
    connection.close()


def create_tables():
    create_table('fly', 'fly_booking')
    create_table('hotel', 'hotel_booking')
    create_table('account', 'account')


def create_table(db_name, table_name):
    (conn, cur) = connect_db(db_name)
    try:

        cur.execute(create_script.get(table_name))
        cur.execute(create_script.get(table_name + "_index"))

        conn.commit()
        print('Cleaning table ' + table_name + ' of ' + db_name)
    finally:
        close_connection(conn, cur)


def delete_tables():
    print('Connecting to all DB\'s')

    delete_table('fly', 'fly_booking')
    delete_table('hotel', 'hotel_booking')
    delete_table('account', 'account')


def delete_table(db_name, table_name):
    (conn, cur) = connect_db(db_name)
    try:
        cur.execute('DROP TABLE IF EXISTS public.'+table_name+';')
        conn.commit()
        print('Cleaning table ' + table_name + ' of ' + db_name)
    finally:
        close_connection(conn, cur)


def set_amount(amount):
    (conn, cur) = connect_db('account')
    cur.execute(create_script.get('upsert_amount'), (amount,))
    conn.commit()
    print(f'Amount has been set to {amount}')
    close_connection(conn, cur)


def get_amount():
    (conn, cur) = connect_db('account')
    cur.execute('SELECT amount FROM account WHERE id=%s LIMIT 1', ("grego",))
    amount = cur.fetchone()[0]
    print(f'Current amount - {amount}')
    close_connection(conn, cur)
    return int(amount)


def help():
    help_info = """

    Task 1 - Two phase commit

    --help
        show this info page

    --clean
        drop all tabels

    --migrate
        create all tables insert account with some amount

    --set-amount <sum>
        update/insert account's amount

    --get-amount
        gets test accout amount

    --book <sum>
        hotel and flight withdrawing sum
    
    --repair
        rolback all failed transaction

    --fail
        fail scenario
    """

    print(help_info)


def repair():
    repair_db('fly')
    repair_db('hotel')
    repair_db('account')


def repair_db(db_name):
    (conn, cur) = connect_db(db_name)
    for fail in conn.tpc_recover():
        print(f'Closing transaction with is {fail}')
        conn.tpc_rollback(fail)

    close_connection(conn, cur)


def book(withdraw, fail=False):

    new_flight = """INSERT INTO public.fly_booking
    (id,client_name,fly_number,"from","to","date")
        VALUES
    (%s, %s, %s, %s, %s, %s);"""

    new_hotel = """INSERT INTO public.hotel_booking
    (id,client_name,hotel_name,arrival,depature)
        VALUES
    (%s,%s,%s,%s,%s);"""

    def get_uid():
        return uuid.uuid4().hex

    # before all transactions start
    amount = get_amount()

    prepared = []

    print('-----------------------------------------------')

    # flight
    try:
        (conn, cur) = connect_db('fly')

        xid = conn.xid(123456, get_uid(), 'bbb63')

        conn.tpc_begin(xid)
        cur.execute(new_flight, (xid[1], 'Ihor', 'mh10', 'Lviv',
                                 'Obroshyno', datetime.date(2020, 3, 1)))

        conn.tpc_prepare()
        print('PREPARE flight transatcion')

        prepared.append((conn, cur))

    except:
        rollback_prepared(prepared)
        return

    # hotel
    try:
        (conn, cur) = connect_db('hotel')

        xid = conn.xid(1234567, get_uid(), 'bbb634')

        conn.tpc_begin(xid)
        cur.execute(new_hotel,
                    (xid[1], 'Ihor', 'Hilton', datetime.date(2020, 3, 1), datetime.date(2020, 3, 1)))

        conn.tpc_prepare()
        print('PREPARE hotel transatcion')

        if not fail:
            prepared.append((conn, cur))

    except:
        rollback_prepared(prepared)
        return

    # account
    try:
        (conn, cur) = connect_db('account')

        xid = conn.xid(12345678, get_uid(), 'bbb6345')

        conn.tpc_begin(xid)
        cur.execute(create_script.get('upsert_amount'), (amount-withdraw,))

        conn.tpc_prepare()
        print('PREPARE account transatcion')

        prepared.append((conn, cur))

    except:
        rollback_prepared(prepared)
        return

    commit_prepared(prepared)


def commit_prepared(prepared):
    print("COMMIT transaction(s)")
    for (conn, cur) in prepared:
        conn.tpc_commit()
        close_connection(conn, cur)


def rollback_prepared(prepared):

    print("ROLLBACK transaction(s)")
    for (conn, cur) in prepared:
        conn.tpc_rollback()
        close_connection(conn, cur)


def main():
    arg_count = len(sys.argv)
    if arg_count > 1:

        command = sys.argv[1]

        if command == '--help':
            help()
        elif command == '--clean':
            delete_tables()
        elif command == '--migrate':
            create_tables()
        elif command == '--set-amount':
            if arg_count > 2:
                set_amount(int(sys.argv[2]))
            else:
                set_amount(500)
        elif command == '--get-amount':
            get_amount()
        elif command == '--book':
            if arg_count > 2:
                book(int(sys.argv[2]))
            else:
                book(200)
        elif command == '--fail':
            if arg_count > 2:
                book(int(sys.argv[2]), True)
            else:
                book(200, True)

        elif command == '--repair':
            repair()
        else:
            help()
    else:
        help()


if __name__ == "__main__":
    main()
