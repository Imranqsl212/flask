import os
import sqlite3
from flask import Flask, render_template, redirect, request, \
    flash  # request используется для работы с запросами от клиента.
from catalogs import *
from send_msg import send_message
import base64
app = Flask(__name__)  # Создается экземпляр класса Flask с именем keyboard
DB_NAME = 'new.db'  # база данных



def create_table():  # создаем таблицу бд
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT,
                           address TEXT,
                           item_code TEXT,
                           item TEXT,
                           must_pay TEXT,
                           phone TEXT,
                           maili TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS reviews
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT,
                        rate INTEGER,
                        comment TEXT,
                        img TEXT)''')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        image TEXT,
                        price TEXT
                    )
                ''')
        conn.commit()


def check_name_exists(name):
    with sqlite3.connect('new.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM users WHERE name = ?', (name,))
        result = cursor.fetchall()
        if len(result) == 0:
            return False
        else:
            return True


def check_code_exists(
        item_code):  # проверяем существование кода товара в базе данных или в каталогах товаров.
    with sqlite3.connect('new.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT art FROM items WHERE art = ?', (item_code,))
        result = cursor.fetchone()
        if result is not None:
            return True  # Если результат не равен None, то код товара существует в базе данных, и возвращается значение True.
        if any(item['art'] == int(item_code) for item in
               catalog_phone + catalog_tablet + catalog_car + catalog_clock + catalog_pc + catalog_notebook):
            return True  # Здесь проверяется наличие кода товара в каталогах catalog_phone, catalog_tablet,
            # catalog_car, catalog_clock, catalog_pc и catalog_notebook. Если код товара найден в любом из каталогов,
            # возвращается значение True.
        else:
            return False  # если никакое условие не сработало , вернется False


def is_valid_phone(phone):
    if len(phone) != 13:
        return False  # Если длина номера телефона не равна 13, то возвращается значение False
    if phone[0] != '+':
        return False  # Если первый символ номера телефона не является знаком плюса +, то возвращается значение False
    if not phone[1:].isdigit():
        return False  # Если все символы после первого символа номера телефона не являются цифрами, то возвращается значение False.
    return True  # Если все проверки пройдены успешно, возвращается значение True, указывающее на правилность номера телефона.


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if request.method == 'POST':  # Проверяется метод запроса. Если он равен 'POST', то выполняется код внутри этого условия.
        name = request.form['name']
        address = request.form['address']
        item_code = request.form['item_code']
        phone = request.form['phone']
        maili = request.form['maili']
        # Получаем значения полей формы из POST-запроса, используя объект request.
        if name.isdigit():  # Если значение имени состоит только из цифр, устанавливается сообщение об ошибке.
            valid_message = 'Некорректное имя'
            return render_template('buy.html', message=valid_message)
        if not is_valid_phone(
                phone):  # Если номер телефона не является корректным, устанавливается сообщение об ошыбке.
            message1 = "Пожалуйста, введите номер телефона со знаком «+», за которым следуют 12 цифр."
            return render_template('buy.html', message=message1)
        if check_name_exists(name):
            message1 = 'такое имя существует, введите другое'
            return render_template('buy.html', message=message1)
        if address.isdigit():  # Если значение адреса состоит только из цифр, устанавливается сообщение об ошибке.
            valid1_message = 'Некорректный адрес'
            return render_template('buy.html', message=valid1_message)

        code_exists = check_code_exists(item_code)  # Проверяется существование кода товара с помощью функции
        if code_exists:  # Если код товара существует, устанавливаем сообщение об успешной покупке.
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (name, address, item_code, phone, maili) VALUES (?, ?, ?, ?, ?)',
                               (name, address, item_code, phone, maili))

                cursor.execute('SELECT * FROM items WHERE art = ?', (item_code,))
                items = cursor.fetchall()

                for item in items:
                    message = f'Успешно!!!, вы заказали {item[0]}, Описание: {item[1]}, цена: {item[2]} рублей. Наши менеджера скоро свяжутся с вами'
                    cursor.execute('UPDATE users SET item = ?, must_pay = ?  WHERE name=?',
                                   (item[0], item[2], name))
                    send = f'Здравстуйте {name}, вы заказали у нас {item[0]}, ваша итоговая плата равняется {item[2]} рублей ,отправьте деньги на мбанк .Оплатите на сайте в разделе "PAYMENTS"'
                    send_message(phone, send)

                for item in catalog_phone + catalog_tablet + catalog_car + catalog_clock + catalog_pc + catalog_notebook:
                    if int(item_code) == item['art']:
                        message = f"Успешно!!!, вы заказали {item['name1']}, Описание: {item['desc']}, цена: {item['price']}RUB. Наши менеджера скоро свяжутся с вами"
                        cursor.execute('UPDATE users SET item = ?, must_pay = ? WHERE name=?',
                                       (item['name1'], item['price'], name))
                        send = f'Здравстуйте {name}, вы заказали у нас {item["name1"]}, ваша итоговая плата равняется {item["price"]} RUB,отправьте деньги на мбанк . Оплатите на сайте в разделе "PAYMENTS"'
                        send_message(phone, send)






        else:
            message = "Вы ввели неправильный код товара"  # Если код товара не существует, устанавливаем сообщение об ошибке.

        return render_template('buy.html',
                               message=message)  # Отображается HTML-шаблон buy.html с передачей сообщения в
        # качестве параметра.

    return render_template(
        'buy.html')  # Если метод запроса не является 'POST', возвращается просто HTML-шаблон buy.html.


@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        rate = request.form['rate']
        comment = request.form['comment']
        img = request.files['file']
        if name.isdigit():  # Если значение имени состоит только из цифр, устанавливается сообщение об ошибке.
            valid_message = 'Некорректное имя'
            return render_template('review.html', message=valid_message)
        elif comment.isdigit():
            valid_message1 = 'Некорректный отзыв'
            return render_template('review.html', message=valid_message1)
        else:
            img1 = img.read()
            with sqlite3.connect(DB_NAME) as conn:  # Устанавливаемся  соединение с базой данных SQLite.
                cursor = conn.cursor()
                cursor.execute('INSERT INTO reviews (name, email, rate, comment, img) VALUES (?, ?, ?, ?, ?)',
                               (name, email, rate, comment, img1))  # заносим данные кторой ввел юзер в бд
                conn.commit()
                return redirect('/')
    return render_template('review.html')


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')





@app.route('/change', methods=['GET', 'POST'])
def change():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
    return render_template('change.html', products=products)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
    return render_template('delete.html', products=products)


@app.route('/delete/<int:delete1>', methods=['POST', 'GET'])
def delete_details(delete1):
    if request.method == 'POST':
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM products WHERE id=?', (delete1,))
            name1 = cursor.fetchone()  # Use fetchone() to get a single value instead of fetchall()
            if name1:
                name1 = name1[0]  # Extract the value from the tuple
                cursor.execute('DELETE FROM products WHERE id=?', (delete1,))
                cursor.execute('DELETE FROM users WHERE item = ?', (name1,))
                conn.commit()

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (delete1,))
        products = cursor.fetchall()
    return render_template('delete_details.html', products=products)


@app.route('/change/<int:change1>', methods=['POST', 'GET'])
def change_details(change1):
    if request.method == 'POST':
        item = request.form['item']
        must_pay = request.form['must_pay']
        image = request.files['file']
        desc = request.form['desc']
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            image = base64.b64encode(image.read()).decode('utf-8')
            cursor.execute('UPDATE products SET name=?, price=?, image=?, description=? WHERE id=?',
                           (item, must_pay, image, desc, change1))
            conn.commit()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (change1,))
        products = cursor.fetchall()
    return render_template('change_details.html', products=products)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['pass']
        if name == 'ADMIN' and password == 'TEST123':
            return redirect('/admin/panel')
    return render_template('admin.html')


@app.route('/admin/panel', methods=['GET', 'POST'])
def panel():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = request.files['image']
        price = request.form['price']
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            image = base64.b64encode(image.read()).decode('utf-8')
            cursor.execute('''
                    INSERT INTO products (name, description, image, price)
                    VALUES (?, ?, ?, ?)
                ''', (name, description, image, price))
            error = 'Товар успешно создан'
            return render_template('panel.html', error=error)

    return render_template('panel.html')


@app.route('/more')
def more():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
    return render_template('more.html', products=products)


@app.route('/product/<int:product_id>', methods=['POST', 'GET'])
def product_details(product_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        products = cursor.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        must_pay = request.form['must_pay']
        item = request.form['item']
        address = request.form['address']
        if name.isdigit():  # Если значение имени состоит только из цифр, устанавливается сообщение об ошибке.
            valid_message = 'Некорректное имя'
            flash(valid_message)
        if check_name_exists(name):
            return 'такое имя существует, выберите другое'
        if not is_valid_phone(
                phone):  # Если номер телефона не является корректным, устанавливается сообщение об ошыбке.
            message1 = "Пожалуйста, введите номер телефона со знаком «+», за которым следуют 12 цифр."
            return message1
        if address.isdigit():  # Если значение адреса состоит только из цифр, устанавливается сообщение об ошибке.
            valid1_message = 'Некорректный адрес'
            flash(valid1_message)
        else:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO users (name, address, item, item_code, must_pay, phone, maili) VALUES (?,?,?,?,?,?,?)
                ''', (name, address, item, 0, must_pay, phone, email))
                send = f'Здравстуйте {name}, вы заказали у нас {item}, ваша итоговая плата равняется {must_pay} рублей ,отправьте деньги на мбанк . Оплатите на сайте в разделе "PAYMENTS"'
                send_message(phone, send)

    return render_template('product_details.html', products=products)


@app.route('/payment', methods=['POST', 'GET'])
def payment():
    if request.method == 'POST':
        username = request.form.get('username')
        pay = request.form.get('pay')

        if not username or not pay:
            error_message = 'Please provide a valid username and payment amount.'
            return render_template('payment.html', error=error_message)

        try:
            pay = float(pay)
        except ValueError:
            error_message = 'Please enter a valid payment amount.'
            return render_template('payment.html', error=error_message)

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET must_pay = NULL WHERE name = ?", (username,))
            conn.commit()

        success_message = f'Payment of {pay} RUB successfully processed.'
        return render_template('payment.html', success=success_message)

    return render_template('payment.html')


@app.route('/get_must_pay')
def get_must_pay():
    username = request.args.get('username')

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT must_pay FROM users WHERE name = ?", (username,))
        result = cursor.fetchone()
        if result:
            must_pay = result[0]
        else:
            must_pay = ""

    return must_pay


if __name__ == '__main__':
    create_table()  # Вызывается функция create_table() для создания таблицы в базе данных.
    app.run(debug=True, port=500, host='0.0.0.0')  # Запускается веб-приложение Flask
