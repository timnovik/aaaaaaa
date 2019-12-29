import sqlite3


def create_base():
    conn = sqlite3.connect("main.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS country_infc
    (NAME TEXT,
    RULER INTEGER,
    BALANCE_MANY INTEGER,
    RES_FOREST INTEGER,
    RES_FOOD INTEGER,
    RES_METAL INTEGER,
    RES_ENERGY INTEGER,
    RES_OIL INTEGER,
    RES_MANPOWER INTEGER,
    NUM_OF_RECRUITS INTEGER,
    RES_CIVIL INTEGER,
    RES_FUEL INTEGER,
    RES_SUPPLY INTEGER,
    RES_UNREST REAL
    )
    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS prov_infc
    (NAME TEXT,
    COUNTRY TEXT,
    RANG TEXT,
    TYPE_LAND TEXT,
    STATUS TEXT,
    INFLUENCE TEXT,
    BUILD TEXT
    )
    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS corp_infc
    (NAME TEXT,
    BALANCE_MANY INTEGER,
    RES_FOREST INTEGER,
    RES_FOOD INTEGER,
    RES_METAL INTEGER,
    RES_ENERGY INTEGER,
    RES_OIL INTEGER,
    RES_FUEL INTEGER
    )
    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_infc
        (ID INTEGER,
        RANG INTEGER
        )
        ''')
    conn.commit()
