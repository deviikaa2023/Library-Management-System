import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="company",
    user="postgres",
    password="devika",
    port="5432"
)

cur = conn.cursor()