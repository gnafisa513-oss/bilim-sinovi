import logging
import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import API_TOKEN, ADMIN_ID
from database import DB_NAME

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# FSM holatlari (Qidiruv, sana kiritish va yangi ishchi qo'shish uchun)
class ExamState(StatesGroup):
    waiting_for_search = State()
    waiting_for_date = State()
    
    # Ishchi qo'shish bosqichlari
    add_name = State()
    add_position = State()
    add_date = State()

def get_db_connection():
    return sqlite3.connect(DB_NAME)

@dp.message(Command("start"), F.from_user.id == ADMIN_ID)
async def start_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yangi ishchi qo'shish", callback_data="add_worker")],
        [InlineKeyboardButton(text="🔍 Ishchini qidirish / Muddat qo'shish", callback_data="search_worker")],
        [InlineKeyboardButton(text="📋 Barcha ishchilar", callback_data="list_workers")]
    ])
    await message.answer("Oltiariq TBTK Bilim sinovi nazorati botiga xush kelibsiz, Admin!", reply_markup=kb)

# ==================== YANGI ISHCHI QO'SHISH (FSM) ====================

@dp.callback_query(F.data == "add_worker", F.from_user.id == ADMIN_ID)
async def add_worker_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Yangi ishchining **Ismi va Familiyasi**ni kiriting:", parse_mode="Markdown")
    await state.set_state(ExamState.add_name)
    await call.answer()

@dp.message(ExamState.add_name, F.from_user.id == ADMIN_ID)
async def add_worker_name(message: types.Message, state: FSMContext):
    await state.update_data(new_name=message.text.strip())
    await message.answer("Ishchining **Lavozimi**ni kiriting (Masalan: *Elektromonter*):", parse_mode="Markdown")
    await state.set_state(ExamState.add_position)

@dp.message(ExamState.add_position, F.from_user.id == ADMIN_ID)
async def add_worker_position(message: types.Message, state: FSMContext):
    await state.update_data(new_position=message.text.strip())
    await message.answer(
        "Bilim sinovi muddatini kiriting.\nFormat: **YYYY-MM-DD** (Masalan: `2026-08-25`).\n"
        "Agar muddati hali aniq bo'lmasa, shunchaki `belgilanmagan` deb yozib yuboring:", 
        parse_mode="Markdown"
    )
    await state.set_state(ExamState.add_date)

@dp.message(ExamState.add_date, F.from_user.id == ADMIN_ID)
async def add_worker_date(message: types.Message, state: FSMContext):
    date_input = message.text.strip()
    
    # Sanani tekshirish
    if date_input.lower() != 'belgilanmagan':
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            exam_date = date_input
        except ValueError:
            await message.answer("Xato format! Sanani xuddi mana shunday kiriting: `2026-08-25` yoki `belgilanmagan` deb yozing:")
            return
    else:
        exam_date = "Muddati belgilanmagan"
        
    data = await state.get_data()
    
    # Bazaga qo'shish
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO workers (name, position, exam_date) VALUES (?, ?, ?)",
        (data['new_name'], data['new_position'], exam_date)
    )
    conn.commit()
    conn.close()
    
    await message.answer(
        f"✅ **Yangi xodim muvaffaqiyatli qo'shildi!**\n\n"
        f"👤 Xodim: {data['new_name']}\n"
        f"💼 Lavozimi: {data['new_position']}\n"
        f"📅 Imtihon sanasi: {exam_date}",
        parse_mode="Markdown"
    )
    await state.clear()

# ==================== QIDIRUV VA TAHRIRLASH ====================

@dp.callback_query(F.data == "search_worker", F.from_user.id == ADMIN_ID)
async def search_worker_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Qidirmoqchi bo'lgan xodimingizning ismini kiriting (yoki qisman yozing):")
    await state.set_state(ExamState.waiting_for_search)
    await call.answer()

@dp.message(ExamState.waiting_for_search, F.from_user.id == ADMIN_ID)
async def search_worker_results(message: types.Message, state: FSMContext):
    search_query = f"%{message.text}%"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, position, exam_date FROM workers WHERE name LIKE ?", (search_query,))
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        await message.answer("Bunday xodim topilmadi. Qaytadan ism kiriting:")
        return

    kb_builder = []
    for w_id, name, pos, date in results:
        kb_builder.append([InlineKeyboardButton(text=f"{name} ({pos})", callback_data=f"select_{w_id}")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=kb_builder)
    await message.answer("Kerakli xodimni tanlang:", reply_markup=kb)
    await state.clear()

@dp.callback_query(F.data.startswith("select_"), F.from_user.id == ADMIN_ID)
async def process_worker_selection(call: types.CallbackQuery, state: FSMContext):
    worker_id = call.data.split("_")[1]
    await state.update_data(selected_worker_id=worker_id)
    
    await call.message.answer("Ushbu xodim uchun bilim sinovi muddatini kiriting\nFormat: **YYYY-MM-DD** (Masalan: `2026-08-25`):", parse_mode="Markdown")
    await state.set_state(ExamState.waiting_for_date)
    await call.answer()

@dp.message(ExamState.waiting_for_date, F.from_user.id == ADMIN_ID)
async def process_date_entry(message: types.Message, state: FSMContext):
    date_text = message.text.strip()
    
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        await message.answer("Xato format! Sanani xuddi mana shunday kiriting: `2026-08-25`", parse_mode="Markdown")
        return
        
    user_data = await state.get_data()
    worker_id = user_data['selected_worker_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE workers SET exam_date = ? WHERE id = ?", (date_text, worker_id))
    cursor.execute("SELECT name FROM workers WHERE id = ?", (worker_id,))
    worker_name = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    
    await message.answer(f"✅ **{worker_name}** uchun bilim sinovi muddati belgilandi: `{date_text}`", parse_mode="Markdown")
    await state.clear()

@dp.callback_query(F.data == "list_workers", F.from_user.id == ADMIN_ID)
async def list_workers(call: types.CallbackQuery):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, position, exam_date FROM workers LIMIT 30")
    rows = cursor.fetchall()
    conn.close()
    
    text = "📋 **Xodimlar ro'yxati (Top 30):**\n\n"
    for name, pos, date in rows:
        text += f"👤 {name} - {pos}\n📅 Imtihon: {date}\n\n"
    
    await call.message.answer(text, parse_mode="Markdown")
    await call.answer()

# ==================== AVTOMATIK OGOHLANTIRISH ====================

async def check_daily_exams():
    today = datetime.now().date()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, position, exam_date FROM workers WHERE exam_date != 'Muddati belgilanmagan'")
    workers = cursor.fetchall()
    conn.close()
    
    for name, pos, exam_date_str in workers:
        try:
            exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
            days_left = (exam_date - today).days
            
            if days_left == 3:
                await bot.send_message(ADMIN_ID, f"⚠️ **Bilim sinoviga 3 kun qoldi!**\n👤 Xodim: {name}\n💼 Lavozimi: {pos}\n📅 Sana: {exam_date_str}")
            elif days_left == 1:
                await bot.send_message(ADMIN_ID, f"🚨 **DIQQAT! Ertaga bilim sinovi (1 kun qoldi):**\n👤 Xodim: {name}\n💼 Lavozimi: {pos}\n📅 Sana: {exam_date_str}")
            elif days_left == 0:
                await bot.send_message(ADMIN_ID, f"🔥 **BUGUN BILIM SINOVI KUNI!**\n👤 Xodim: {name}\n💼 Lavozimi: {pos}")
        except Exception:
            continue

async def main():
    scheduler.add_job(check_daily_exams, 'cron', hour=9, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())