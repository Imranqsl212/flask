from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

list = InlineKeyboardMarkup(row_width=3)
list.add(InlineKeyboardButton(text='Phone', callback_data='Phone'),
         InlineKeyboardButton(text='Cars', callback_data='Cars'),
         InlineKeyboardButton(text='Tablet', callback_data='Tablet'),
         InlineKeyboardButton(text='Clock', callback_data='Clock'),
         InlineKeyboardButton(text='PC', callback_data='PC'),
         InlineKeyboardButton(text='Notebook', callback_data='Notebook'))

asort=InlineKeyboardMarkup(row_width=3)
asort.add(InlineKeyboardButton(text='Phone', callback_data='Phone_sh'),
         InlineKeyboardButton(text='Cars', callback_data='Cars_sh'),
         InlineKeyboardButton(text='Tablet', callback_data='Tablet_sh'),
         InlineKeyboardButton(text='Clock', callback_data='Clock_sh'),
         InlineKeyboardButton(text='PC', callback_data='PC_sh'),
         InlineKeyboardButton(text='Notebook', callback_data='Notebook_sh'))


main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('каталог').add('контакты').add('отзывы')

buy = InlineKeyboardMarkup(row_width=1)
buy.add(InlineKeyboardButton(text='SITE TO BUY ITEM ====>>>>', callback_data='site', url='http://192.168.0.111:8080'))






main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.add('каталог').add('контакты').add('отзывы').add('admin')
panel = ReplyKeyboardMarkup(resize_keyboard=True)
panel.add('add').add('create button').add('назад')


