import psycopg2


class WeatherRepository:
    def fetch_weather(self):
        conn = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="admin",
            host="postgres",
            port="5232",
        )

        cursor = conn.cursor()

        cursor.execute("select * from metdata")

        data = cursor.fetchall()
        return data

    def save_weather(self, data_csv):
        pass
