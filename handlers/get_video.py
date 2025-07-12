from aiogram import Router, F
from aiogram.types import Message,CallbackQuery
from config import DB_PATH,BOT_TOKEN,CHANNEL_IDS
from database.models import get_movie_by_code
from utils.subscription_check import check_subscription_status
from aiogram import Bot
import sqlite3
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
class MovieStates(StatesGroup):
    waiting_for_movie_code = State()
video_router = Router()


@video_router.callback_query(F.data == "get_video")
async def process_get_video_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🎬 Iltimos, kino kodini yuboring. Masalan: `123`", parse_mode="Markdown")
    await state.set_state(MovieStates.waiting_for_movie_code)
    await callback.answer()

@video_router.message(Command("start"))
async def start_command(message: Message,state: FSMContext):
    bot = Bot(token=BOT_TOKEN)
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, registration_date, last_activity) VALUES (?, ?, ?, ?)",
              (user_id, username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    
    is_subscribed = await check_subscription_status(bot, user_id)
    if not is_subscribed:
        channel_links = "\n".join([f"📢 <a href='https://t.me/{channel}'>Kanal</a>" for channel in CHANNEL_IDS])
        await message.reply(
            f"👋 Xush kelibsiz, {username}!\n"
            f"KinoBot Pro++ ga xush kelibsiz! Kino olish uchun quyidagi kanallarga obuna bo‘ling:\n{channel_links}",
            parse_mode="HTML"
        )
        return
    await message.answer(f"🎬 <b>KinoBot</b> ga xush kelibsiz, <b>{username}</b>!\n\n iltimos kod yuboring",parse_mode="HTML")
    await state.set_state(MovieStates.waiting_for_movie_code)

@video_router.message(MovieStates.waiting_for_movie_code)
async def handle_movie_code(message: Message, state: FSMContext):
    movie_code = message.text.strip().upper()
    movie = get_movie_by_code(movie_code)
    
    if not movie:
        await message.reply("⚠️ Kino topilmadi!")
        return

    movie_id, file_id, title, genre, year, description, is_premium = movie
    
    bot = Bot(token=BOT_TOKEN)
    is_subscribed = await check_subscription_status(bot, message.from_user.id)
    if is_premium and not is_subscribed:
        await message.reply("💎 Bu premium kino! Iltimos, obuna bo‘ling: /buy_subscription")
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE movies SET view_count = view_count + 1 WHERE id = ?", (movie_id,))
    c.execute("UPDATE users SET last_activity = ? WHERE user_id = ?",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.from_user.id))
    conn.commit()
    conn.close()
    caption = (
        f"🎬 <b>{title}</b> ({year})\n"
        f"🎭 <b>Janr:</b> {genre}\n"
        f"📝 <b>Tavsif:</b>\n{description}\n\n"
    )
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📢 Barcha kodlar", url="https://t.me/MegaKinoUz")
            ]
        ]
    )
    await bot.send_video(
        chat_id=message.chat.id,
        video=file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )

    await state.clear()



