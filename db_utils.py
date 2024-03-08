import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv


def create_connection():
    load_dotenv()
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
    return conn


def create_table_if_not_exists():
    conn = create_connection()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute(sql.SQL('''
        CREATE TABLE IF NOT EXISTS ticket_info (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            message TEXT NOT NULL,
            author BIGINT NOT NULL,
            line VARCHAR(3),
            station_name VARCHAR(255),
            station_id VARCHAR(10),
            direction_name VARCHAR(255),
            direction_id VARCHAR(10)
        );
    '''))
    print('created table')
    cursor.close()
    conn.close()


def insert_ticket_info(
    timestamp,
    message,
    author,
    line,
    station_name,
    station_id,
    direction_name,
    direction_id
):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(sql.SQL('''
        INSERT INTO ticket_info (
            timestamp, message, author, line, station_name, station_id, direction_name, direction_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    '''), (
        timestamp,
        message,
        author,
        line,
        station_name,
        station_id,
        direction_name,
        direction_id
    ))
    conn.commit()
    cursor.close()
    conn.close()


def update_info(
    last_known_message,
    timestamp,
    message,
    author,
    line,
    station_name,
    station_id,
    direction_name,
    direction_id
):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute(sql.SQL('''
        UPDATE ticket_info
        SET timestamp = %s, message = %s, author = %s, line = %s,
            station_name = %s, station_id = %s, direction_name = %s,
            direction_id = %s
        WHERE message = %s AND author = %s;
    '''), (
        timestamp,
        message,
        author,
        line,
        station_name,
        station_id,
        direction_name,
        direction_id,
        last_known_message,
        author
    ))

    conn.commit()
    cursor.close()
    conn.close()
