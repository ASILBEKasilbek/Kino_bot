from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database import models

serial_router = Router()


# States for adding a series
class AddSeriesStates(StatesGroup):
    title = State()
    genre = State()
    year = State()
    description = State()
    is_premium = State()


# States for adding a season
class AddSeasonStates(StatesGroup):
    series_id = State()
    season_number = State()
    episode_count = State()


# States for adding an episode
class AddEpisodeStates(StatesGroup):
    series_id = State()
    season_id = State()
    episode_number = State()
    file_id = State()
    title = State()
    description = State()


# States for editing a series
class EditSeriesStates(StatesGroup):
    series_id = State()
    title = State()
    genre = State()
    year = State()
    description = State()
    is_premium = State()


# States for deleting a series
class DeleteSeriesStates(StatesGroup):
    series_id = State()


# States for deleting an episode
class DeleteEpisodeStates(StatesGroup):
    series_id = State()
    season_id = State()
    episode_id = State()



# =======================
# 📌 ADD SERIES
# =======================
@serial_router.callback_query(F.data == "add_series")
async def add_series_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📺 Serial nomini kiriting:")
    await state.set_state(AddSeriesStates.title)
    await callback.answer()


@serial_router.message(AddSeriesStates.title)
async def add_series_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("🎭 Janrini kiriting:")
    await state.set_state(AddSeriesStates.genre)


@serial_router.message(AddSeriesStates.genre)
async def add_series_genre(message: Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await message.answer("📅 Yilini kiriting:")
    await state.set_state(AddSeriesStates.year)


@serial_router.message(AddSeriesStates.year)
async def add_series_year(message: Message, state: FSMContext):
    try:
        year = int(message.text)
        await state.update_data(year=year)
        await message.answer("📜 Tavsif kiriting:")
        await state.set_state(AddSeriesStates.description)
    except ValueError:
        await message.answer("❌ Yil raqam bo‘lishi kerak. Qaytadan kiriting:")


@serial_router.message(AddSeriesStates.description)
async def add_series_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha (Premium)", callback_data="premium_yes"),
            InlineKeyboardButton(text="❌ Yo‘q (Oddiy)", callback_data="premium_no"),
        ]
    ])

    await message.answer("💰 Serial premium bo‘lsinmi?", reply_markup=keyboard)
    print(90)
    await state.set_state(AddSeriesStates.is_premium)

    print("Current state:", await state.get_state())

@serial_router.callback_query()
async def test_any_callback(call: CallbackQuery, state: FSMContext):
    print("Keldi callback:", call.data)
    await call.answer("Callback keldi")

@serial_router.callback_query(F.data.in_(["premium_yes", "premium_no"]), AddSeriesStates.is_premium)
async def add_series_premium(call: CallbackQuery, state: FSMContext):
    print("CALLBACK ISHLEDI:", call.data)
    print(12)
    data = await state.get_data()
    title = data["title"]
    genre = data["genre"]
    year = data["year"]
    description = data["description"]

    is_premium = 1 if call.data == "premium_yes" else 0
    print(90)

    models.add_series(title, genre, year, description, is_premium)
    print(91)

    await call.message.edit_text(f"✅ Serial qo‘shildi: <b>{title}</b>")
    await state.clear()
    await call.answer()



# =======================
# 📌 LIST SERIES
# =======================
@serial_router.callback_query(F.data == "list_series")
async def list_series(callback: CallbackQuery):
    series = models.get_all_series()
    if not series:
        await callback.message.answer("❌ Hali seriallar qo‘shilmagan.")
        return

    text = "📺 <b>Barcha seriallar:</b>\n\n"
    for s in series:
        text += f"ID: <code>{s['id']}</code> | {s['title']} ({s['year']})\n"

    await callback.message.answer(text)
    await callback.answer()


# =======================
# 📌 DELETE SERIES
# =======================

@serial_router.callback_query(F.data == "delete_series")
async def delete_series_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🗑 O‘chirmoqchi bo‘lgan serial ID sini kiriting:")
    await state.set_state(DeleteSeriesStates.series_id)
    await callback.answer()


@serial_router.message(DeleteSeriesStates.series_id)
async def delete_series_confirm(message: Message, state: FSMContext):
    try:
        series_id = int(message.text)
        series = models.get_series_by_id(series_id)

        if not series:
            await message.answer("❌ Bunday ID li serial topilmadi.")
            await state.clear()
            return

        models.delete_series(series_id)
        await message.answer(f"❌ Serial o‘chirildi: <b>{series['title']}</b>")
        await state.clear()
    except ValueError:
        await message.answer("❌ ID raqam bo‘lishi kerak. Qaytadan kiriting:")


# =======================
# 📌 ADD SEASON
# =======================
@serial_router.callback_query(F.data == "add_season")
async def add_season_start(callback: CallbackQuery, state: FSMContext):
    series = models.get_all_series()
    if not series:
        await callback.message.answer("❌ Hali seriallar qo‘shilmagan. Avval serial qo‘shing.")
        await callback.answer()
        return

    text = "📺 Mavsum qo‘shish uchun serial ID sini kiriting:\n\n"
    for s in series:
        text += f"ID: <code>{s['id']}</code> | {s['title']} ({s['year']})\n"

    await callback.message.answer(text)
    await state.set_state(AddSeasonStates.series_id)
    await callback.answer()


@serial_router.message(AddSeasonStates.series_id)
async def add_season_series_id(message: Message, state: FSMContext):
    try:
        series_id = int(message.text)
        series = models.get_series_by_id(series_id)

        if not series:
            await message.answer("❌ Bunday ID li serial topilmadi.")
            return

        await state.update_data(series_id=series_id)
        await message.answer("📂 Mavsum raqamini kiriting (masalan, 1, 2, 3):")
        await state.set_state(AddSeasonStates.season_number)
    except ValueError:
        await message.answer("❌ ID raqam bo‘lishi kerak. Qaytadan kiriting:")


@serial_router.message(AddSeasonStates.season_number)
async def add_season_number(message: Message, state: FSMContext):
    try:
        season_number = int(message.text)
        await state.update_data(season_number=season_number)
        await message.answer("🎞 Ushbu mavsumdagi qismlar sonini kiriting:")
        await state.set_state(AddSeasonStates.episode_count)
    except ValueError:
        await message.answer("❌ Mavsum raqami raqam bo‘lishi kerak. Qaytadan kiriting:")


@serial_router.message(AddSeasonStates.episode_count)
async def add_season_episode_count(message: Message, state: FSMContext):
    try:
        episode_count = int(message.text)
        data = await state.get_data()
        series_id = data["series_id"]
        season_number = data["season_number"]

        models.add_season(series_id, season_number, episode_count)
        await message.answer(f"✅ Mavsum qo‘shildi: Serial ID {series_id}, Mavsum {season_number}")
        await state.clear()
    except ValueError:
        await message.answer("❌ Qismlar soni raqam bo‘lishi kerak. Qaytadan kiriting:")


# =======================
# 📌 ADD EPISODE
# =======================
@serial_router.callback_query(F.data == "add_episode")
async def add_episode_start(callback: CallbackQuery, state: FSMContext):
    series = models.get_all_series()
    if not series:
        await callback.message.answer("❌ Hali seriallar qo‘shilmagan. Avval serial qo‘shing.")
        await callback.answer()
        return

    text = "📺 Qism qo‘shish uchun serial ID sini kiriting:\n\n"
    for s in series:
        text += f"ID: <code>{s['id']}</code> | {s['title']} ({s['year']})\n"

    await callback.message.answer(text)
    await state.set_state(AddEpisodeStates.series_id)
    await callback.answer()


@serial_router.message(AddEpisodeStates.series_id)
async def add_episode_series_id(message: Message, state: FSMContext):
    try:
        series_id = int(message.text)
        series = models.get_series_by_id(series_id)

        if not series:
            await message.answer("❌ Bunday ID li serial topilmadi.")
            return

        seasons = models.get_all_seasons(series_id)
        if not seasons:
            await message.answer("❌ Ushbu serialda hali mavsumlar yo‘q. Avval mavsum qo‘shing.")
            return

        text = f"📂 {series['title']} uchun mavsum tanlang:\n\n"
        for s in seasons:
            text += f"ID: <code>{s['id']}</code> | Mavsum {s['season_number']}\n"

        await state.update_data(series_id=series_id)
        await message.answer(text)
        await state.set_state(AddEpisodeStates.season_id)
    except ValueError:
        await message.answer("❌ ID raqam bo‘lishi kerak. Qaytadan kiriting:")


@serial_router.message(AddEpisodeStates.season_id)
async def add_episode_season_id(message: Message, state: FSMContext):
    try:
        season_id = int(message.text)
        season = models.get_season_by_id(season_id)

        if not season:
            await message.answer("❌ Bunday ID li mavsum topilmadi.")
            return

        await state.update_data(season_id=season_id)
        await message.answer("🎞 Qism raqamini kiriting (masalan, 1, 2, 3):")
        await state.set_state(AddEpisodeStates.episode_number)
    except ValueError:
        await message.answer("❌ ID raqam bo‘lishi kerak. Qaytadan kiriting:")


@serial_router.message(AddEpisodeStates.episode_number)
async def add_episode_number(message: Message, state: FSMContext):
    try:
        episode_number = int(message.text)
        await state.update_data(episode_number=episode_number)
        await message.answer("📎 Telegram fayl ID sini kiriting (video uchun):")
        await state.set_state(AddEpisodeStates.file_id)
    except ValueError:
        await message.answer("❌ Qism raqami raqam bo‘lishi kerak. Qaytadan kiriting:")


@serial_router.message(AddEpisodeStates.file_id)
async def add_episode_file_id(message: Message, state: FSMContext):
    await state.update_data(file_id=message.text)
    await message.answer("🎬 Qism nomini kiriting (masalan, '1-qism' yoki 'Boshlanish'):")
    await state.set_state(AddEpisodeStates.title)


@serial_router.message(AddEpisodeStates.title)
async def add_episode_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📜 Qism haqida izoh kiriting:")
    await state.set_state(AddEpisodeStates.description)


@serial_router.message(AddEpisodeStates.description)
async def add_episode_description(message: Message, state: FSMContext):
    data = await state.get_data()
    season_id = data["season_id"]
    episode_number = data["episode_number"]
    file_id = data["file_id"]
    title = data["title"]
    description = message.text

    models.add_episode(season_id, episode_number, file_id, title, description)
    await message.answer(f"✅ Qism qo‘shildi: <b>{title}</b>")
    await state.clear()


# =======================
# 📌 EDIT SERIES
# =======================
@serial_router.callback_query(F.data == "edit_series")
async def edit_series_start(callback: CallbackQuery, state: FSMContext):
    series = models.get_all_series()
    if not series:
        await callback.message.answer("❌ Hali seriallar qo‘shilmagan.")
        await callback.answer()
        return

    text = "✏️ Tahrirlamoqchi bo‘lgan serial ID sini kiriting:\n\n"
    for s in series:
        text += f"ID: <code>{s['id']}</code> | {s['title']} ({s['year']})\n"

    await callback.message.answer(text)
    await state.set_state(EditSeriesStates.series_id)
    await callback.answer()


@serial_router.message(EditSeriesStates.series_id)
async def edit_series_id(message: Message, state: FSMContext):
    try:
        series_id = int(message.text)
        series = models.get_series_by_id(series_id)

        if not series:
            await message.answer("❌ Bunday ID li serial topilmadi.")
            return

        await state.update_data(series_id=series_id)
        await message.answer(f"📺 Yangi nomini kiriting (hozirgi: {series['title']}):")
        await state.set_state(EditSeriesStates.title)
    except ValueError:
        await message.answer("❌ ID raqam bo‘lishi kerak. Qaytadan kiriting:")


@serial_router.message(EditSeriesStates.title)
async def edit_series_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("🎭 Yangi janrini kiriting:")
    await state.set_state(EditSeriesStates.genre)


@serial_router.message(EditSeriesStates.genre)
async def edit_series_genre(message: Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await message.answer("📅 Yangi yilini kiriting:")
    await state.set_state(EditSeriesStates.year)


@serial_router.message(EditSeriesStates.year)
async def edit_series_year(message: Message, state: FSMContext):
    try:
        year = int(message.text)
        await state.update_data(year=year)
        await message.answer("📜 Yangi tavsif kiriting:")
        await state.set_state(EditSeriesStates.description)
    except ValueError:
        await message.answer("❌ Yil raqam bo‘lishi kerak. Qaytadan kiriting:")


@serial_router.message(EditSeriesStates.description)
async def edit_series_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💰 Premiummi? (ha/yo‘q):")
    await state.set_state(EditSeriesStates.is_premium)


@serial_router.message(EditSeriesStates.is_premium)
async def edit_series_premium(message: Message, state: FSMContext):
    data = await state.get_data()
    series_id = data["series_id"]
    title = data["title"]
    genre = data["genre"]
    year = data["year"]
    description = data["description"]
    is_premium = 1 if message.text.lower() in ["ha", "✅", "yes"] else 0

    models.update_series(series_id, title, genre, year, description, is_premium)
    await message.answer(f"✅ Serial tahrirlandi: <b>{title}</b>")
    await state.clear()


# =======================
# 📌 DELETE EPISODE
# =======================
@serial_router.callback_query(F.data == "delete_episode")
async def delete_episode_start(callback: CallbackQuery, state: FSMContext):
    series = models.get_all_series()
    if not series:
        await callback.message.answer("❌ Hali seriallar qo‘shilmagan. Avval serial qo‘shing.")
        await callback.answer()
        return

    text = "📺 Qism o‘chirmoqchi bo‘lgan serial ID sini kiriting:\n\n"
    for s in series:
        text += f"ID: <code>{s['id']}</code> | {s['title']} ({s['year']})\n"

    await callback.message.answer(text)
    await state.set_state(DeleteEpisodeStates.series_id)
    await callback.answer()


@serial_router.message(DeleteEpisodeStates.series_id)
async def delete_episode_series_id(message: Message, state: FSMContext):
    try:
        series_id = int(message.text)
        series = models.get_series_by_id(series_id)

        if not series:
            await message.answer("❌ Bunday ID li serial topilmadi.")
            return

        seasons = models.get_all_seasons(series_id)
        if not seasons:
            await message.answer("❌ Ushbu serialda hali mavsumlar yo‘q.")
            return

        text = f"📂 {series['title']} uchun mavsum tanlang:\n\n"
        for s in seasons:
            text += f"ID: <code>{s['id']}</code> | Mavsum {s['season_number']}\n"

        await state.update_data(series_id=series_id)
        await message.answer(text)
        await state.set_state(DeleteEpisodeStates.season_id)
    except ValueError:
        await message.answer("❌ ID raqam bo‘lishi kerak. Qaytadan kiriting:")


@serial_router.message(DeleteEpisodeStates.season_id)
async def delete_episode_season_id(message: Message, state: FSMContext):
    try:
        season_id = int(message.text)
        season = models.get_season_by_id(season_id)

        if not season:
            await message.answer("❌ Bunday ID li mavsum topilmadi.")
            return

        episodes = models.get_all_episodes(season_id)
        if not episodes:
            await message.answer("❌ Ushbu mavsumda hali qismlar yo‘q.")
            return

        text = f"🎞 Mavsum {season['season_number']} uchun qism tanlang:\n\n"
        for e in episodes:
            text += f"ID: <code>{e['id']}</code> | {e['title']} (Qism {e['episode_number']})\n"

        await state.update_data(season_id=season_id)
        await message.answer(text)
        await state.set_state(DeleteEpisodeStates.episode_id)
    except ValueError:
        await message.answer("❌ ID raqam bo‘lishi kerak. Qaytadan kiriting:")


@serial_router.message(DeleteEpisodeStates.episode_id)
async def delete_episode_confirm(message: Message, state: FSMContext):
    try:
        episode_id = int(message.text)
        episode = models.get_episode_by_id(episode_id)

        if not episode:
            await message.answer("❌ Bunday ID li qism topilmadi.")
            await state.clear()
            return

        models.delete_episode(episode_id)
        await message.answer(f"❌ Qism o‘chirildi: <b>{episode['title']}</b>")
        await state.clear()
    except ValueError:
        await message.answer("❌ ID raqam bo‘lishi kerak. Qaytadan kiriting:")