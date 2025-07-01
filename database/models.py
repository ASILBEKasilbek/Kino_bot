
import sqlite3
from config import DB_PATH

# database/models.py faylida
from config import DB_PATH
import sqlite3

def get_movie_by_code(code: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, file_id, title, genre, year, description, is_premium
        FROM movies WHERE movie_code = ?
    """, (code,))
    result = c.fetchone()
    conn.close()
    return result



def update_view_count(movie_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE movies SET view_count = view_count + 1 WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()

def search_movies(query: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM movies WHERE title LIKE ? OR genre LIKE ? OR year LIKE ?",
              ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
    movies = c.fetchall()
    conn.close()
    return movies
