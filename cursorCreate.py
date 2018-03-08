def cursorCreate():
    import pymysql

    database = pymysql.connect(host="localhost", user="root", passwd="..n1tT.fa.gm", db="Brackets", autocommit=True)
    cursor = database.cursor(pymysql.cursors.DictCursor)

    return database, cursor
