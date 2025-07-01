from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import DB_PATH, BOT_TOKEN
from core.ai_recommendation import get_movie_recommendations
import sqlite3
from datetime import datetime

reminder_router = Router()
scheduler = AsyncIOScheduler()

async def send_daily_reminder():
    bot = Bot(token=BOT_TOKEN)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_blocked = 0")
    users = c.fetchall()
    conn.close()
    
    for user in users:
        user_id = user[0]
        recommendations = get_movie_recommendations(user_id)
        if recommendations:
            movie = recommendations[0]
            movie_id, title, genre, year, description = movie
            try:
                await bot.send_message(
                    user_id,
                    f"📽 Bugungi kino tavsiyasi: {title} ({year})\n🎭 Janr: {genre}\n📜 Tavsif: {description}"
                )
            except:
                continue
    
    await bot.close()

def setup_scheduler():
    scheduler.add_job(
        send_daily_reminder,
        trigger="cron",
        hour=9,
        minute=0,
        second=0
    )
    scheduler.start()

@reminder_router.message(Command("enable_reminder"))
async def enable_reminder_command(message: Message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET last_activity = ? WHERE user_id = ?",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.from_user.id))
    conn.commit()
    conn.close()
    
    await message.reply("🔔 Kunlik kino eslatmalari yoqildi!")