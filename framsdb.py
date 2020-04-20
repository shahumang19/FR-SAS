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

    def rowcount(self):
        return self.cursor.rowcount

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
            "CREATE TABLE class(CID INT NOT NULL AUTO_INCREMENT,CNAME VARCHAR(255) NOT NULL,PRIMARY KEY(CID), UNIQUE INDEX CNAME_UNIQUE (CNAME ASC) VISIBLE)",
            "CREATE TABLE student(SID INT NOT NULL AUTO_INCREMENT,SREGNO VARCHAR(255) NOT NULL,SNAME VARCHAR(255) NULL,SCLASS INT NULL,ACTIVE TINYINT NOT NULL DEFAULT 1,PRIMARY KEY (SID), UNIQUE INDEX SREGNO_UNIQUE (SREGNO ASC) VISIBLE,INDEX fkclass_idx (SCLASS ASC) VISIBLE,CONSTRAINT fkclass FOREIGN KEY (SCLASS) REFERENCES frtemp.class (CID) ON DELETE NO ACTION ON UPDATE NO ACTION);",
            "CREATE TABLE attendance(SID INT NOT NULL,ADATE DATE NOT NULL,ATIME TIME NOT NULL,DISTANCE FLOAT NULL,INDEX fkattstu_idx (SID ASC) VISIBLE,CONSTRAINT fkattstu FOREIGN KEY (SID) REFERENCES student (SID) ON DELETE NO ACTION ON UPDATE NO ACTION);",
            "CREATE TABLE class_attendance(CID INT NOT NULL,ADATE DATE NULL,ATIME TIME NULL,SACTIVE INT NULL,SPRESENT INT NULL,SRECOG INT NULL,SABSCENT INT NULL,INDEX frcacl_idx (CID ASC) VISIBLE,CONSTRAINT frcacl FOREIGN KEY (CID) REFERENCES class (CID) ON DELETE NO ACTION ON UPDATE NO ACTION);"
        ]
        for table in tables:
            self.db.execute(table)
            self.db.commit()

    def addClass(self, cname):
        try:
            query = 'INSERT INTO class(CNAME) VALUES(%s)'
            self.db.execute(query, (cname,))
            self.db.commit()
            rc = 1 if self.db.rowcount() > 0 else 0
            return rc
        except mysql.connector.errors.IntegrityError:
            return -1
        except Exception as e:
            print(e)
    
    def updateClass(self, cid, cname):
        try:
            query = 'UPDATE class SET CNAME=%s WHERE CID=%s'
            self.db.execute(query, (cname, cid))
            self.db.commit()
            rc = 1 if self.db.rowcount() > 0 else 0
            return rc
        except mysql.connector.errors.IntegrityError:
            return -1
        except Exception as e:
            print(e)

    def deleteClass(self, cid):
        try:
            query = 'DELETE FROM class WHERE CID=%s'
            self.db.execute(query, (cid,))
            self.db.commit()
            rc = 1 if self.db.rowcount() > 0 else 0
            return rc
        except Exception as e:
            print(e)

    def viewClass(self, cid=None):
        try:
            if cid:
                query = 'SELECT * FROM class WHERE CID=%s'
                rows = self.db.query(query, (cid,))
            else:
                query = 'SELECT * FROM class'
                rows = self.db.query(query)
            return rows
        except Exception as e:
            print("Exception ocurred : ", e)
            return []

    def addStudent(self, sregno, sname, sclass, active):
        try:
            query = 'INSERT INTO student(SREGNO,SNAME, SCLASS, ACTIVE) VALUES(%s, %s, %s, %s)'
            self.db.execute(query, (sregno, sname, sclass, active))
            self.db.commit()
            rc = 1 if self.db.rowcount() > 0 else 0
            return rc
        except mysql.connector.errors.IntegrityError:
            return -1
        except Exception as e:
            print(e)

    def updateStudent(self, sregno, sname, sclass, active):
        try:
            query = 'UPDATE student SET SNAME=%s, SCLASS=%s, ACTIVE=%s WHERE SREGNO=%s'
            self.db.execute(query, (sname, sclass, active, sregno))
            self.db.commit()
            rc = 1 if self.db.rowcount() > 0 else 0
            return rc
        except mysql.connector.errors.IntegrityError:
            return -1
        except Exception as e:
            print(e)

    def deleteStudent(self, sregno):
        try:
            query = 'DELETE FROM student WHERE SREGNO=%s'
            self.db.execute(query, (sregno, ))
            self.db.commit()
            rc = 1 if self.db.rowcount() > 0 else 0
            return rc
        except Exception as e:
            print(e)

    def viewStudent(self, sregno=None):
        try:
            if sregno:
                query = 'SELECT * FROM student WHERE SREGNO=%s'
                rows = self.db.query(query, (sregno,))
            else:
                query = 'SELECT * FROM student'
                rows = self.db.query(query)
            return rows
        except Exception as e:
            print("Exception ocurred : ", e)
            return []

    def addAttendance(self, sid, adate, atime, dist):
        try:
            query = 'INSERT INTO attendance(SID, ADATE, ATIME, DISTANCE) VALUES(%s, %s, %s, %s)'
            self.db.execute(query, (sid, adate, atime, dist))
            self.db.commit()
            rc = 1 if self.db.rowcount() > 0 else 0
            return rc
        except mysql.connector.errors.IntegrityError as e:
            return -1
        except Exception as e:
            print(e)

    def viewAttendance(self, sregno=None, adate=None, active=None):
        try:
            if sregno:
                query = 'SELECT S.SREGNO,A.ADATE,A.ATIME  FROM attendance as A INNER JOIN student as S ON S.SID = A.SID WHERE A.SID IN (SELECT SID FROM STUDENT WHERE  SREGNO=%s)'
                rows = self.db.query(query, (sregno))
            elif adate and active:
                query = 'SELECT S.SREGNO,A.ADATE,A.ATIME  FROM attendance as A INNER JOIN student as S ON S.SID = A.SID WHERE A.SID IN (SELECT SID FROM STUDENT WHERE  ACTIVE=%s) AND ADATE = %s'
                rows = self.db.query(query, (active, adate))
            elif adate:
                query = 'SELECT S.SREGNO,A.ADATE,A.ATIME  FROM attendance as A INNER JOIN student as S ON S.SID = A.SID WHERE ADATE = %s'
                rows = self.db.query(query, (sregno,active))
            elif active:
                query = 'SELECT S.SREGNO,A.ADATE,A.ATIME  FROM attendance as A INNER JOIN student as S ON S.SID = A.SID WHERE A.SID IN (SELECT SID FROM STUDENT WHERE  ACTIVE=%s)'
                rows = self.db.query(query, (sregno,active))
            else:
                query = 'SELECT S.SREGNO,A.ADATE,A.ATIME  FROM attendance as A INNER JOIN student as S ON S.SID = A.SID'
                rows = self.db.query(query)
            return rows
        except Exception as e:
            print("Exception ocurred : ", e)
            return []

    def addClassAttendance(self, cid, adate, atime, spresent, srecog):
        try:
            query = 'INSERT INTO class_attendance(CID, ADATE, ATIME, SACTIVE, SPRESENT, SRECOG, SABSCENT) VALUES(%s,%s, %s, (SELECT COUNT(SID) FROM student WHERE ACTIVE=1), %s, %s, %s - (SELECT COUNT(SID) FROM student WHERE ACTIVE=1));'
            # query = 'INSERT INTO class_attendance(CID, ADATE, ATIME, SACTIVE, SPRESENT, SRECOG, SABSCENT) VALUES(%s, %s, %s, %s, %s, %s, %s)'
            self.db.execute(query, (cid, adate, atime, spresent, srecog, spresent))
            self.db.commit()
            rc = 1 if self.db.rowcount() > 0 else 0
            return rc
        except mysql.connector.errors.IntegrityError:
            return -1
        except Exception as e:
            print(e)

    def viewClassAttendance(self, cid= None):
        try:
            if cid:
                query = 'SELECT * FROM class_attendance WHERE CID=%s'
                rows = self.db.query(query, (cid,))
            else:
                query = 'SELECT * FROM class_attendance'
                rows = self.db.query(query)
            return rows
        except Exception as e:
            print("Exception ocurred : ", e)
            return []

    def close(self):
        self.db.close()






if __name__ == "__main__":
    import os
    from utils import read_txtfile
    from datetime import datetime

    configs = eval(read_txtfile(os.path.join("data", "config.txt"))[0])
    dbc = configs["db"]
    host, user, passwd, dbname = dbc["host"], dbc["user"], dbc["passwd"], dbc["db"]

    tnow = datetime.now()
    dt = tnow.date().strftime("%Y/%m/%d")
    tm = tnow.time().strftime("%H:%M:%S")
    
    db = FRAMSDatabase(host, user, passwd, dbname)
    # inserted = db.addClass("11-B")
    # inserted = db.addStudent("2", "Disha", 1, 1)
    # inserted = db.addAttendance(8, dt, tm,0.1)
    # inserted = db.addClassAttendance(1, "2020-04-20", "15:30:34", 2, 2)
    # print(f"Inserted : {inserted}")

    # updated = db.updateClass(3,"11-A")
    # updated = db.updateStudent("2", "Disha Shah", 1, 1)
    # print(f"Updated : {updated}")

    # deleted = db.deleteClass(3)
    # deleted = db.deleteStudent("2")
    # print(f"Deleted : {deleted}")

    # rows = db.viewClass()
    # rows = db.viewStudent()
    # rows = db.viewAttendance()
    # rows = db.viewClassAttendance(cid=14)
    # print(rows)

    db.close()

