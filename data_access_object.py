import datetime
import os
import sqlite3


DB_NAME = 'students.db'


class HoroscopeDAO(object):
    def __init__(self, connection):
        self.connection = connection

    def grades_tendency(self):
        """
        Predicts whether a grade will get higher or lower in the future
        """

        raise NotImplementedError()

    def grade_8_lower_tendency(self):
        """
        Predicts how many >8 grades will get lower in the future
        """

        raise NotImplementedError()

    def good_day(self):
        """
        Predicts whether a given student will have a good day
        """

        raise NotImplementedError()


class SQLiteHoroscopeDAO(HoroscopeDAO):
    def grades_tendency(self, nr):
        cursor = self.connection.cursor()
        cursor.execute("""SELECT name,
                                 (CASE WHEN (LENGTH(name)+LENGTH(nr)) % 2 = 1
                                    then 'higher' else 'lower' end) AS tendency
                          FROM students WHERE nr=?""", (nr,))
        result = cursor.fetchone()
        return result

    def grade_8_lower_tendency(self):
        cursor = self.connection.cursor()
        cursor.execute("""SELECT COUNT(*) AS tendency
                          FROM students
                          WHERE (CASE WHEN (LENGTH(name)+LENGTH(nr)) % 2 = 1
                                    then 'higher' else 'lower' end)='lower'
                                AND grade>8""")
        result = cursor.fetchone()
        return result

    def good_day(self, nr):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM students WHERE nr=?", (nr,))
        result = cursor.fetchone()

        day = datetime.datetime.now().day
        if ((day+ord(result[0][0])) % 2 == 1):
            return (result[0], 'good')
        return (result[0], 'bad')


def init_db(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE students (nr TEXT, name TEXT, grade REAL)")

    students = [('124356', 'John', 8.6),
                ('124806', 'Jenny', 4.5),
                ('123386', 'Mark', 5.6),
                ('124376', 'Greg', 7),
                ('124266', 'Yves', 10),
                ('129956', 'Clark', 9.0),
                ('122476', 'Paul', 7.6),
                ('178356', 'Lemar', 5.6),
                ('124896', 'Brent', 9)]
    cursor.executemany("INSERT INTO students VALUES (?, ?, ?)", students)
    connection.commit()


if __name__ == '__main__':
    connection = sqlite3.connect(DB_NAME)
    init_db(connection)
    dao = SQLiteHoroscopeDAO(connection)

    print "%s's grade will get %s in the future" % dao.grades_tendency('124356')
    print "%s's grade will get %s in the future" % dao.grades_tendency('124806')

    print "%s students' grades currently over 8 will " \
          "lower in the future" % dao.grade_8_lower_tendency()

    print "%s will have a %s day" % dao.good_day('124356')
    print "%s will have a %s day" % dao.good_day('129956')

    # Close and also drop database file
    connection.close()
    os.remove(DB_NAME)
