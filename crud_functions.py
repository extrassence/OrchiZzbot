import sqlite3


def get_all_products():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()
    connection.close()
    return products


def initiate_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        image TEXT NOT NULL
        )''')
    connection.commit()
    connection.close()


def fill_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    desc = ['Белки, жиры, углеводы и клетчатка для тех, кому лень готовить',
            'Ешьте сколько хотите и не поправляйтесь, на вкус не жалуйтесь',
            'Исцеление от всех болезней, от старости, от рака и от тупости',
            'Приправьте любую еду этим БАДом и она потеряет калории и вкус']
    titl = ['Хубур-чубур', 'Хрючево без калорий', 'Эликсир Николаса Фламеля', 'Обнулитель Калорий (БАД)']
    for i in range(4):
        cursor.execute('INSERT INTO Products (title, description, price, image) VALUES (?, ?, ?, ?)',
                       (titl[i], desc[i], (i+1) * 100, f'{i+1}.JPG'))

    connection.commit()
    connection.close()


def print_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()
    col_names = [_[0] for _ in cursor.description]
    print(col_names)
    for p in products:
        print(p)
    connection.close()


if __name__ == '__main__':
    initiate_db()
    fill_db()
    print_db()
