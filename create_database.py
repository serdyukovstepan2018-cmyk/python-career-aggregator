# create_database.py
import pymysql
from mysql_database import Base, engine

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='564106',
        database='mysql'
    )
    
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS vacancies_db")
        print("База данных 'vacancies_db' создана!")
    
    connection.close()
    
    Base.metadata.create_all(bind=engine)
    print("✅ Таблица 'vacancies' создана")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")