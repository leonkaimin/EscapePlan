CREATE_STOCK_TABLE = "CREATE TABLE IF NOT EXISTS STOCK(" \
    "DATE           TEXT     NOT NULL," \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "SHARES         INT," \
    "ENTRIES        INT," \
    "AMOUNT         INT," \
    "OPRICE           FLOAT," \
    "TOP        FLOAT," \
    "BOTTOM         FLOAT," \
    "CPRICE          FLOAT," \
    "FLUCATION      FLOAT," \
    "UNIQUE ( DATE, CODE) ON CONFLICT REPLACE"    \
    ");"

CREATE_BASIC_TABLE = "CREATE TABLE IF NOT EXISTS BASIC(" \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "DENO         FLOAT," \
    "CAP        FLOAT," \
    "CLASS      TEXT        NOT NULL" \
    ");"

INSERT_BASIC = "INSERT OR IGNORE INTO BASIC VALUES" \
    " (\"{}\", \"{}\", " \
    " {}, {}, \"{}\");"

CREATE_AMOUNT_TABLE = "CREATE TABLE IF NOT EXISTS AMOUNT(" \
    "DATE           TEXT     NOT NULL," \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "FOREIN_IN  INT," \
    "FOREIN_OUT  INT," \
    "FOREIN_SUM  INT," \
    "LOCAL_IN  INT," \
    "LOCAL_OUT  INT," \
    "LOCAL_SUM  INT," \
    "SMALL_LOCAL_IN  INT," \
    "SMALL_LOCAL_OUT  INT," \
    "SMALL_LOCAL_SUM  INT," \
    "TOTAL  INT," \
    "UNIQUE ( DATE, CODE) ON CONFLICT REPLACE"    \
    ");"

CREATE_MARGIN_TABLE = "CREATE TABLE IF NOT EXISTS MARGIN(" \
    "DATE           TEXT     NOT NULL," \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "MARGIN         INT," \
    "SHORT          INT," \
    "UNIQUE ( DATE, CODE) ON CONFLICT REPLACE"    \
    ");"


CREATE_LEGAL_TABLE = "CREATE TABLE IF NOT EXISTS LEGAL(" \
    "DATE           TEXT     NOT NULL," \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "LEGAL         FLOAT," \
    "UNIQUE ( DATE, CODE) ON CONFLICT REPLACE"    \
    ");"

CREATE_FUNDAMENTAL_TABLE = "CREATE TABLE IF NOT EXISTS FUNDAMENTAL(" \
    "DATE           TEXT     NOT NULL," \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "PER FLOAT," \
    "PBR FLOAT," \
    "DYR FLOAT," \
    "UNIQUE ( DATE, CODE) ON CONFLICT REPLACE"    \
    ");"

CREATE_EPS_TABLE = "CREATE TABLE IF NOT EXISTS EPS(" \
    "QUATER           TEXT     NOT NULL," \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "VAL           FLOAT," \
    "UNIQUE ( QUATER, CODE) ON CONFLICT REPLACE"    \
    ");"

CREATE_ETFDIV_TABLE = "CREATE TABLE IF NOT EXISTS ETFDIV(" \
    "DATE           TEXT     NOT NULL," \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "VAL           FLOAT," \
    "UNIQUE ( DATE, CODE) ON CONFLICT REPLACE"    \
    ");"

CREATE_BOOK_TABLE = "CREATE TABLE IF NOT EXISTS BOOK(" \
    "QUATER           TEXT     NOT NULL," \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "VAL           FLOAT," \
    "UNIQUE ( QUATER, CODE) ON CONFLICT REPLACE"    \
    ");"

CREATE_REVENUE_TABLE = "CREATE TABLE IF NOT EXISTS REVENUE(" \
    "MONTH           TEXT     NOT NULL," \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "VAL           FLOAT," \
    "UNIQUE ( MONTH, CODE) ON CONFLICT REPLACE"    \
    ");"

CREATE_NPM_TABLE = "CREATE TABLE IF NOT EXISTS NPM(" \
    "QUATER           TEXT     NOT NULL," \
    "CODE           TEXT     NOT NULL," \
    "NAME           TEXT     NOT NULL," \
    "VAL           FLOAT," \
    "UNIQUE ( QUATER, CODE) ON CONFLICT REPLACE"    \
    ");"

INSERT_EPS = "INSERT OR IGNORE INTO EPS VALUES" \
    " (\"{}\", \"{}\", \"{}\", {});"


INSERT_LEGAL = "INSERT OR IGNORE INTO LEGAL VALUES" \
    " (\"{}\", \"{}\", \"{}\", {});"

INSERT_MARGIN = "INSERT OR IGNORE INTO MARGIN VALUES" \
    " (\"{}\", \"{}\", \"{}\", {}, {});"

INSERT_ETFDIV = "INSERT OR IGNORE INTO ETFDIV VALUES" \
    " (\"{}\", \"{}\", \"{}\", {});"

INSERT_NPM = "INSERT OR IGNORE INTO NPM VALUES" \
    " (\"{}\", \"{}\", \"{}\", {});"

INSERT_REVENUE = "INSERT OR IGNORE INTO REVENUE VALUES" \
    " (\"{}\", \"{}\", \"{}\", {});"

INSERT_BOOK = "INSERT OR IGNORE INTO BOOK VALUES" \
    " (\"{}\", \"{}\", \"{}\", {});"

INSERT_FUNDAMENTAL = "INSERT OR IGNORE INTO FUNDAMENTAL VALUES" \
    " (\"{}\", \"{}\", \"{}\", {}," \
    " {}, {});"

INSERT_STOCK = "INSERT OR IGNORE INTO STOCK VALUES" \
    " (\"{}\", \"{}\", \"{}\", {}," \
    " {}, {}, {}, {}, {}, {}, {});"

SELECT_STOCK = "SELECT {} FROM STOCK {} ORDER BY DATE {}"

SELECT_EPS = "SELECT * FROM EPS {} ORDER BY QUATER"

SELECT_ETFDIV = "SELECT * FROM ETFDIV {} ORDER BY DATE"

SELECT_REVENUE = "SELECT * FROM REVENUE {} ORDER BY MONTH"

SELECT_BOOK = "SELECT * FROM BOOK {} ORDER BY QUATER"

SELECT_NPM = "SELECT * FROM NPM {} ORDER BY QUATER"

SELECT_BASIC = "SELECT {} FROM BASIC {}"

SELECT_MARGIN = "SELECT * FROM MARGIN {} ORDER BY DATE"

SELECT_DISTINCT_CODE = "SELECT DISTINCT CODE, NAME FROM BASIC WHERE LENGTH(CODE) <= 6 {} " \
    "{} ORDER BY CODE;"

SELECT_DISTINCT_CODE_STOCK = "SELECT DISTINCT CODE, NAME FROM STOCK WHERE LENGTH(CODE) <= 6 " \
    "AND DATE = '{}' ORDER BY CODE;"

SELECT_DISTINCT_CODE_BOND = "SELECT DISTINCT CODE, NAME FROM BASIC WHERE LENGTH(CODE) == 6 " \
    "AND CODE LIKE '%B' " \
    "ORDER BY CODE;"
