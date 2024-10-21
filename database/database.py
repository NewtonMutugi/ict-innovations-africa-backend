from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from settings import settings

DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{
    settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def connect_with_retry():
    retry_options = {
        'retries': 5,
        'factor': 2,
        'min_timeout': 1,  # in seconds
        'max_timeout': 5  # in seconds
    }

    for i in range(retry_options['retries']):
        try:
            # Try to connect to the database
            connection = engine.connect()
            print('Database connection established successfully.')
            return connection
        except Exception as err:  # noqa: F841
            print(f"Database connection failed. Retrying in {
                  retry_options['min_timeout']} seconds...")
            time.sleep(retry_options['min_timeout'])
            retry_options['min_timeout'] = min(
                retry_options['min_timeout'] * retry_options['factor'], retry_options['max_timeout'])

    raise Exception(
        'Unable to connect to the database after multiple attempts.')


connection = connect_with_retry()


def initialize_connection():
    global connection
    connection = connect_with_retry()


initialize_connection()
