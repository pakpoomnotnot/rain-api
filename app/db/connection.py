import psycopg2
from config.settings import DB_CONFIG

def get_connection():
    # ใช้ DB_CONFIG ที่เราเซ็ตไว้
    conn = psycopg2.connect(**DB_CONFIG)
    return conn