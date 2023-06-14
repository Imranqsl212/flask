from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from keyboard import keyboards as kb
import os
import logging
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import sqlite3 as sq
import tracemalloc
from catalogs import *

tracemalloc.start()  # используется для запуска сбора информации о распределении памяти (трассировки памяти) во время выполнения программы.

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


async def db_start():
    global db, cur
    db = sq.connect('new.db')
    cur = db.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS items(name1 TEXT, desc TEXT, price INTEGER, photo1 TEXT, brand TEXT,art PRIMARY KEY)")
    db.commit()


async def add_item(state):
    async with state.proxy() as data:
        cur.execute("INSERT INTO items (name1, desc, price, photo1, brand, art) VALUES (?, ?, ?, ?, ?,?)",
                    (data['name1'], data['desc'], data['price'], data['photo1'], data['type'], data['art']))
        db.commit()


async def on_startup(_):
    await db_start()
    print('ready')


class NewOrder(StatesGroup):
    type = State()
    name1 = State()
    desc = State()
    price = State()
    art = State()
    photo1 = State()


@dp.message_handler(text='back')
async def get_back(message: types.Message):
    await message.answer('вы вышли из каталога', reply_markup=kb.main)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Welcome to our shop')
    if int(os.getenv('ADMIN_ID')) == message.from_user.id:
        await message.answer('admin hi', reply_markup=kb.main_admin)
    else:
        await message.answer(f'hello, {message.from_user.first_name}', reply_markup=kb.main)


@dp.message_handler(commands=['buy'])
async def buy(message: types.Message):
    await message.reply('Here is site to buy our products', reply_markup=kb.buy)


@dp.message_handler(commands=['help'])
async def helper(message: types.Message):
    await message.answer('/start-запустить бота\n/buy-купить\n/help-список команд',
                         reply_markup=kb.main)


@dp.message_handler(text='контакты')
async def con(message: types.Message):
    await message.answer(f'https://t.me/imran_definitely')


@dp.message_handler(text='каталог')
async def con(message: types.Message):
    await message.answer(f'{message.from_user.first_name} hi', reply_markup=kb.asort)


@dp.message_handler(text='admin')
async def con(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'вы вошли в админку', reply_markup=kb.panel)
    else:
        print('я тебя не понимаю')


@dp.message_handler(text='отзывы')
async def con1(message: types.Message):
    cur.execute("SELECT * FROM reviews")
    items = cur.fetchall()
    if not items:
        await message.answer('нету ничего')
    else:
        for item in items:
            result1 = f'<b>Комментарий номер: </b> {item[0]}\n<b>Имя: </b> {item[1]}\n<b>Почта: </b> {item[2]}\n<b>Оценка: </b> {item[3]} из 5\n<b>Отзыв: </b>{item[4]}'
            await bot.send_photo(message.chat.id, item[5], caption=result1, parse_mode='html')


@dp.message_handler(text='назад')
async def con(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f'вы вышли из админки', reply_markup=kb.main_admin)
    else:
        await message.answer(f'{message.from_user.first_name},я вас не понимаю')


@dp.message_handler(text='add')
async def add_item1(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await NewOrder.type.set()  # Устанавливаем состояние FSM на 'type'
        await message.answer('Выберите тип товара', reply_markup=kb.list)
    else:
        await message.reply('Я тебя не понимаю.')


@dp.callback_query_handler(state=NewOrder.type)
async def add_item_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
    await call.message.answer('Напишите название товара')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.name1)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name1'] = message.text
    await message.answer('Напишите описание товара')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.desc)
async def add_item_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await message.answer('Напишите цену товара в рублях')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.price)
async def add_item_desc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.isdigit():
            data['price'] = int(message.text)
            await message.answer('Отправьте артикул товара')
            await NewOrder.next()
        else:
            await message.answer('Цена должна быть числом. Пожалуйста, введите цену снова.')


@dp.message_handler(state=NewOrder.art)
async def add_art(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        art = message.text.strip()
        if len(art) == 6 and art.isdigit():
            with db:
                cur.execute("SELECT * FROM items WHERE art = ?", (art,))
                existing_art = cur.fetchone()
            if existing_art is None and not any(item['art'] == int(art) for item in
                                                catalog_phone + catalog_tablet + catalog_car + catalog_clock + catalog_pc + catalog_notebook):
                data['art'] = art
                await message.answer('Отправьте фотографию товара')
                await NewOrder.next()
            else:
                await message.answer('Товар с указанным кодом уже существует')
        else:
            await message.answer('Введите код товара заново (6 цифр)')


@dp.message_handler(lambda message: not message.photo, state=NewOrder.photo1)
async def add_item_photo_check(message: types.Message):
    await message.answer('Это не фотография!')


@dp.message_handler(content_types=['photo'], state=NewOrder.photo1)
async def add_item_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo1'] = message.photo[0].file_id
    await add_item(state)
    await message.answer('Товар успешно создан!', reply_markup=kb.panel)
    await state.finish()


@dp.callback_query_handler()
async def show_catal(callback_query: types.CallbackQuery):
    if callback_query.data == 'Phone_sh':
        for phone in catalog_phone:
            result1 = f'<b>Name</b>: {phone["name1"]}\n<b>Description</b>: {phone["desc"]}\n<b>Price</b>: {phone["price"]}\n<b>ART</b>:{phone["art"]}'
            await bot.send_photo(callback_query.message.chat.id, phone["photo1"], caption=result1, parse_mode="html")
        cur.execute("SELECT * FROM items WHERE brand=?", ('Phone',))
        items = cur.fetchall()
        for item in items:
            result1 = f'<b>Name</b>: {item[0]}\n<b>Description</b>: {item[1]}\n<b>Price</b>: {item[2]}\n<b>ART</b>:{item[5]}'
            await bot.send_photo(callback_query.message.chat.id, item[3], caption=result1, parse_mode="html")

    elif callback_query.data == 'Notebook_sh':
        for notebook in catalog_notebook:
            result1 = f'<b>Name</b>: {notebook["name1"]}\n<b>Description</b>: {notebook["desc"]}\n<b>Price</b>: {notebook["price"]}\n<b>ART</b>:{notebook["art"]}'
            await bot.send_photo(callback_query.message.chat.id, notebook["photo1"], caption=result1, parse_mode="html")
        cur.execute("SELECT * FROM items WHERE brand=?", ('Notebook',))
        items = cur.fetchall()
        for item in items:
            result1 = f'<b>Name</b>: {item[0]}\n<b>Description</b>: {item[1]}\n<b>Price</b>: {item[2]}\n<b>ART</b>:{item[5]}'
            await bot.send_photo(callback_query.message.chat.id, item[3], caption=result1, parse_mode="html")

    elif callback_query.data == 'PC_sh':
        for pc in catalog_pc:
            result1 = f'<b>Name</b>: {pc["name1"]}\n<b>Description</b>: {pc["desc"]}\n<b>Price</b>: {pc["price"]}\n<b>ART</b>:{pc["art"]}'
            await bot.send_photo(callback_query.message.chat.id, pc["photo1"], caption=result1, parse_mode="html")
        cur.execute("SELECT * FROM items WHERE brand=?", ('PC',))
        items = cur.fetchall()
        for item in items:
            result1 = f'<b>Name</b>: {item[0]}\n<b>Description</b>: {item[1]}\n<b>Price</b>: {item[2]}\n<b>ART</b>:{item[5]}'
            await bot.send_photo(callback_query.message.chat.id, item[3], caption=result1, parse_mode="html")

    elif callback_query.data == 'Clock_sh':
        for phone in catalog_clock:
            result1 = f'<b>Name</b>: {phone["name1"]}\n<b>Description</b>: {phone["desc"]}\n<b>Price</b>: {phone["price"]}\n<b>ART</b>:{phone["art"]}'
            await bot.send_photo(callback_query.message.chat.id, phone["photo1"], caption=result1, parse_mode="html")
        cur.execute("SELECT * FROM items WHERE brand=?", ('Clock',))
        items = cur.fetchall()
        for item in items:
            result1 = f'<b>Name</b>: {item[0]}\n<b>Description</b>: {item[1]}\n<b>Price</b>: {item[2]}\n<b>ART</b>:{item[5]}'
            await bot.send_photo(callback_query.message.chat.id, item[3], caption=result1, parse_mode="html")
    elif callback_query.data == 'Tablet_sh':
        for phone in catalog_tablet:
            result1 = f'<b>Name</b>: {phone["name1"]}\n<b>Description</b>: {phone["desc"]}\n<b>Price</b>: {phone["price"]}\n<b>ART</b>:{phone["art"]}'
            await bot.send_photo(callback_query.message.chat.id, phone["photo1"], caption=result1, parse_mode="html")
        cur.execute("SELECT * FROM items WHERE brand=?", ('Tablet',))
        items = cur.fetchall()
        for item in items:
            result1 = f'<b>Name</b>: {item[0]}\n<b>Description</b>: {item[1]}\n<b>Price</b>: {item[2]}\n<b>ART</b>:{item[5]}'
            await bot.send_photo(callback_query.message.chat.id, item[3], caption=result1, parse_mode="html")
    elif callback_query.data == 'Cars_sh':
        for phone in catalog_car:
            result1 = f'<b>Name</b>: {phone["name1"]}\n<b>Description</b>: {phone["desc"]}\n<b>Price</b>: {phone["price"]}\n<b>ART</b>:{phone["art"]}'
            await bot.send_photo(callback_query.message.chat.id, phone["photo1"], caption=result1, parse_mode="html")
        cur.execute("SELECT * FROM items WHERE brand=?", ('Cars',))
        items = cur.fetchall()
        for item in items:
            result1 = f'<b>Name</b>: {item[0]}\n<b>Description</b>: {item[1]}\n<b>Price</b>: {item[2]}\n<b>ART</b>:{item[5]}'
            await bot.send_photo(callback_query.message.chat.id, item[3], caption=result1, parse_mode="html")
    else:
        await callback_query.answer('i dont understand you')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
