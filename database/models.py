import sqlite3
from config import DB_PATH

def get_all_channels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM channels")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


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


def get_top_movies(limit: int = 5):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # natijani dict sifatida olish uchun
    c = conn.cursor()
    c.execute("SELECT * FROM movies ORDER BY view_count DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# --- Series ---
def add_series(title, genre, year, description, is_premium):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO series (title, genre, year, description, is_premium) VALUES (?, ?, ?, ?, ?)",
              (title, genre, year, description, is_premium))
    conn.commit()
    conn.close()


def add_season(series_id, season_number, episode_count):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO seasons (series_id, season_number, episode_count) VALUES (?, ?, ?)",
              (series_id, season_number, episode_count))
    conn.commit()
    conn.close()


def add_episode(season_id, episode_number, file_id, title, description):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO episodes (season_id, episode_number, file_id, title, description) VALUES (?, ?, ?, ?, ?)",
              (season_id, episode_number, file_id, title, description))
    conn.commit()
    conn.close()


def get_all_series():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM series")
    series = [{'id': row[0], 'title': row[1], 'year': row[3]} for row in c.fetchall()]
    conn.close()
    return series


def get_series_by_id(series_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM series WHERE id = ?", (series_id,))
    series = c.fetchone()
    conn.close()
    return {'id': series[0], 'title': series[1], 'year': series[3]} if series else None


def get_all_seasons(series_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM seasons WHERE series_id = ?", (series_id,))
    seasons = [{'id': row[0], 'season_number': row[2]} for row in c.fetchall()]
    conn.close()
    return seasons


def get_season_by_id(season_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM seasons WHERE id = ?", (season_id,))
    season = c.fetchone()
    conn.close()
    return {'id': season[0], 'season_number': season[2]} if season else None


def update_series(series_id, title, genre, year, description, is_premium):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE series SET title = ?, genre = ?, year = ?, description = ?, is_premium = ? WHERE id = ?",
              (title, genre, year, description, is_premium, series_id))
    conn.commit()
    conn.close()


def delete_series(series_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM series WHERE id = ?", (series_id,))
    conn.commit()
    conn.close()


def get_all_episodes(season_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM episodes WHERE season_id = ?", (season_id,))
    episodes = [{'id': row[0], 'title': row[4], 'episode_number': row[2]} for row in c.fetchall()]
    conn.close()
    return episodes


def get_episode_by_id(episode_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
    episode = c.fetchone()
    conn.close()
    return {'id': episode[0], 'title': episode[4], 'episode_number': episode[2]} if episode else None


def delete_episode(episode_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM episodes WHERE id = ?", (episode_id,))
    conn.commit()
    conn.close()
