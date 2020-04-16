import mysql.connector

class MySQLDatabase:
    def __init__(self, host, user, passwd, dbname=""):
        self._conn = mysql.connector.connect(host=host,user=user,passwd=passwd, database=dbname)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def exists(self, dbname):
        check = True
        dbs = self.query("SHOW DATABASES")
        dbs = list(map(lambda x: x[0], dbs))
        check = True if dbname in dbs else False
        return check

    def commit(self):
        self.connection.commit()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()

    def close(self):
        self.connection.close()


class FRAMSDatabase:
    def __init__(self, host, user, passwd, dbname):
        self.db = MySQLDatabase(host, user, passwd)
        if self.db.exists(dbname):
            print(f"[INFO] [framsdb.py] Database exists....")
            self.db.close()
            self.db = MySQLDatabase(host, user, passwd, dbname)
        else:
            print(f"[WARNING] [framsdb.py] Database does not exists....")
            print(f"[WARNING] [framsdb.py] Generating DB and Tables....")
            self.db = MySQLDatabase(host, user, passwd)
            self.makeDB(dbname)
            self.db = MySQLDatabase(host, user, passwd, dbname)
            self.makeTables()

    def makeDB(self, dbname):
        self.db.execute(f"CREATE DATABASE {dbname}")
        self.db.commit()
        self.db.close()

    def makeTables(self):
        tables = [
            "CREATE TABLE class(CID INT NOT NULL AUTO_INCREMENT,CNAME VARCHAR(255) NOT NULL,PRIMARY KEY(CID))",
            "CREATE TABLE student(SID INT NOT NULL AUTO_INCREMENT,SREGNO VARCHAR(255) NOT NULL,SNAME VARCHAR(255) NULL,SCLASS INT NULL,ACTIVE TINYINT NOT NULL DEFAULT 1,PRIMARY KEY (SID),INDEX fkclass_idx (SCLASS ASC) VISIBLE,CONSTRAINT fkclass FOREIGN KEY (SCLASS) REFERENCES frtemp.class (CID) ON DELETE NO ACTION ON UPDATE NO ACTION);",
            "CREATE TABLE attendance(SID INT NOT NULL,ADATE DATE NOT NULL,ATIME TIME NOT NULL,DISTANCE FLOAT NULL,INDEX fkattstu_idx (SID ASC) VISIBLE,CONSTRAINT fkattstu FOREIGN KEY (SID) REFERENCES frtemp.student (SID) ON DELETE NO ACTION ON UPDATE NO ACTION);",
            "CREATE TABLE class_attendance(CID INT NOT NULL,ADATE DATE NULL,ATIME TIME NULL,SACTIVE INT NULL,SPRESENT INT NULL,SRECOG INT NULL,SABSCENT INT NULL,INDEX frcacl_idx (CID ASC) VISIBLE,CONSTRAINT frcacl FOREIGN KEY (CID) REFERENCES frtemp.class (CID) ON DELETE NO ACTION ON UPDATE NO ACTION);"
        ]
        for table in tables:
            self.db.execute(table)
            self.db.commit()

    def close(self):
        self.db.close()






if __name__ == "__main__":
    import os
    from utils import read_txtfile
    configs = eval(read_txtfile(os.path.join("data", "config.txt"))[0])
    dbc = configs["db"]
    host, user, passwd, dbname = dbc["host"], dbc["user"], dbc["passwd"], dbc["db"]
    
    db = FRAMSDatabase(host, user, passwd, dbname)
    db.close()
        

