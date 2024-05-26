import psycopg2


def drop_db(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
        DROP TABLE phone_data;
        DROP TABLE client_data;
        """
        )
        conn.commit()


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS client_data(
            id SERIAL PRIMARY KEY,
            name VARCHAR(40),
            surname VARCHAR(40),
            email VARCHAR(40)
        );
        CREATE TABLE IF NOT EXISTS phone_data(
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES client_data(id),
            phone VARCHAR(40) NOT NULL
        );
        """
        )
        conn.commit()


def add_client(conn, name, surname, email, phones=None):
    with conn.cursor() as cur:
        cur.execute(
            """
        INSERT INTO client_data(name, surname, email)"""
            """ VALUES(%s, %s, %s) RETURNING id
        """,
            (name, surname, email),
        )
        user_id = cur.fetchone()
        if phones:
            for phone in phones:
                cur.execute(
                    """INSERT INTO phone_data(client_id, phone)"""
                    """ VALUES(%s, %s)""",
                    (user_id, phone),
                )
        conn.commit()
    return user_id


def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO phone_data(client_id, phone) VALUES(%s, %s)""",
            (client_id, phone),
        )
        conn.commit()


def change_client(
    conn, client_id, name=None, surname=None, email=None, phones=None
):
    with conn.cursor() as cur:
        if name is not None:
            cur.execute(
                """UPDATE client_data SET name = %s WHERE id = %s""",
                (name, client_id),
            )
        if surname is not None:
            cur.execute(
                """UPDATE client_data SET surname = %s WHERE id = %s""",
                (surname, client_id),
            )
        if email is not None:
            cur.execute(
                """UPDATE client_data SET email = %s WHERE id = %s""",
                (email, client_id),
            )
        if phones is not None:
            cur.execute(
                """DELETE FROM phone_data WHERE client_id = %s""", (client_id,)
            )
            for phone in phones:
                cur.execute(
                    """INSERT INTO phone_data(client_id, phone)"""
                    """ VALUES(%s, %s)""",
                    (client_id, phone),
                )


def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute(
            """DELETE FROM phone_data WHERE client_id = %s AND phone = %s""",
            (client_id, phone),
        )
        conn.commit()


def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute(
            """DELETE FROM phone_data WHERE client_id = %s""", (client_id,)
        )
        cur.execute("""DELETE FROM client_data WHERE id = %s""", (client_id,))
        conn.commit()


def find_client(conn, name=None, surname=None, email=None, phone=None):
    with conn.cursor() as cur:
        if name is None:
            name = "%"
        if surname is None:
            surname = "%"
        if email is None:
            email = "%"
        if phone is None:
            phone = "%"
        cur.execute(
            """SELECT * FROM client_data"""
            """ JOIN phone_data ON client_data.id = phone_data.client_id"""
            """ WHERE name LIKE %s """
            """AND surname LIKE %s AND email LIKE %s AND phone LIKE %s """,
            (name, surname, email, phone),
        )
        return cur.fetchall()


def find_client_by_name(conn, name):
    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM client_data WHERE name = %s""", (name,))
        return cur.fetchall()


def find_client_by_surname(conn, surname):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT * FROM client_data WHERE surname = %s""", (surname,)
        )
        return cur.fetchall()


def find_client_by_email(conn, email):
    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM client_data WHERE email = %s""", (email,))
        return cur.fetchall()


def find_client_by_phone(conn, phone):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT * FROM client_data"""
            """ JOIN phone_data ON client_data.id = phone_data.client_id"""
            """ WHERE phone = %s""",
            (phone,),
        )
        return cur.fetchall()


with psycopg2.connect(
    database="clients_db", user="postgres", password="tester"
) as conn:
    drop_db(conn)
    create_db(conn)

    user_id_Ivan_Ivanov = add_client(
        conn,
        name="Ivan",
        surname="Ivanov",
        email="Ivanov@ya.ru",
        phones=["+7(999)-999-99-99", "+7(987)-987-98-98"],
    )
    user_id_Petr_Petrov = add_client(
        conn,
        "Petr",
        "Petrov",
        "Petrov@ya.ru",
        ["555-555-55-55", "666-666-66-66"],
    )

    print(find_client_by_name(conn, "Ivan"))
    print(find_client_by_surname(conn, "Ivanov"))
    print(find_client_by_email(conn, "Ivanov@ya.ru"))
    print(find_client_by_phone(conn, "+7(999)-999-99-99"))
    print(find_client_by_phone(conn, "+7(987)-987-98-98"))
    print(find_client(conn, email="Ivanov@ya.ru"))

    add_phone(conn, user_id_Ivan_Ivanov, "+7(999)-999-99-90")
    print(find_client_by_phone(conn, "+7(999)-999-99-90"))
    delete_phone(conn, user_id_Ivan_Ivanov, "+7(999)-999-99-90")

    delete_client(conn, user_id_Ivan_Ivanov)
    print(find_client(conn, surname="Ivanov"))

    print(find_client(conn, name="Petr"))
    change_client(
        conn,
        user_id_Petr_Petrov,
        name="Ivan",
        surname="Ivanov",
        email="Ivanov@ya.ru",
        phones=["777-777-77-77", "888-888-88-88"],
    )
    print(find_client(conn, surname="Petrov"))
    print(find_client(conn, phone="777-777-77-77"))
