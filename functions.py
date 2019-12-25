import vk_api
import sqlite3
from vk_api.longpoll import VkLongPoll
from base import create_base
from constants import *

vk_session = vk_api.VkApi(token=TOKEN)

longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
create_base()
conn = sqlite3.connect("main.db")
cursor = conn.cursor()


def give_vars():
    return vk, longpoll, conn, cursor


def delete_commas(l):
    return [l[i][:-1] if l[i][-1] == ',' else '' for i in range(len(l) - 1)] + [l[-1]]


def name(id):
    return vk.users.get(user_id=id, fields='screen_name')[0]['screen_name']


def id(s):
    try:
        return vk.users.get(user_ids=s)[0]['id']
    except:
        return 0


def update_roles():
    cursor.execute('SELECT * FROM users_infc')
    l = {}
    for user, rang in cursor.fetchall():
        l[user] = int(rang)
    return l


def add_prov(args, user_id):
    if update_roles()[user_id] >= 2:
        list1 = []
        for i in range(len(args)):
            if CHECK['prov'][i](args[i]):
                list1.append(args[i])
            else:
                return f'Ошибка во время чтения параметра №{i + 1}: {PARAMETERS["prov"][i]}. Проверьте формат ввода сообщением "параметры страны" и попробуйте снова.'
        cursor.execute("SELECT * FROM prov_infc WHERE NAME=?", [list1[0]])
        if len(cursor.fetchall()) > 0:
            return 'Такая провинция уже есть.'
        cursor.execute(f"INSERT INTO prov_infc VALUES({','.join(['?' for _ in range(len(PARAMETERS['prov']))])})",
                       list1)
        conn.commit()
        return 'Провинция успешно добавлена в список.'
    return NO_PERMISSION


def show_prov(user_id, prov=0):
    if prov:
        cursor.execute('SELECT * FROM prov_infc WHERE NAME = ?', [prov])
        l = []
        try:
            d = list(cursor.fetchall()[0])
        except:
            vk.messages.send(random_id=0, user_id=user_id, message='Страна не найдена.')
            return 0
        if user_id == int(d[2]) or update_roles()[user_id] >= 2:
            d[2] = '@' + name(int(d[2]))
            for i in range(len(d)):
                l.append(f'{PARAMETERS["prov"][i]}: {d[i]}')
            vk.messages.send(random_id=0, user_id=user_id, message='\n'.join(l))
        else:
            vk.messages.send(random_id=0, user_id=user_id, message=NO_PERMISSION)
    elif update_roles()[user_id] >= 2:
        cursor.execute('SELECT NAME FROM prov_infc')
        d = list(map(lambda x: x[0], cursor.fetchall()))
        for prov_name in d:
            show_prov(user_id, prov_name)
    else:
        vk.messages.send(random_id=0, user_id=user_id, message=NO_PERMISSION)


def edit_prov(user_id, prov, **kwargs):
    cursor.execute('SELECT * FROM prov_infc WHERE NAME = ?', [prov])
    l = list(cursor.fetchall()[0])
    if user_id == int(l[2]) and update_roles()[user_id] >= 2:
        for parameter, value in kwargs.items():
            if parameter in PARAMETERS['prov']:
                ind = PARAMETERS['prov'].index(parameter)
                if CHECK['prov'][ind](value):
                    l[PARAMETERS['prov'].index(parameter)] = int(value) if type(l[ind]) == int else value
                    cursor.execute('DELETE FROM prov_infc WHERE NAME = ?', [prov])
                    cursor.execute(
                        f"INSERT INTO prov_infc VALUES({','.join(['?' for _ in range(len(PARAMETERS['prov']))])})",
                        l)
                    conn.commit()
                elif value[1:].isdigit() and value[0] in ['+', '-'] and CHECK['prov'][ind](str(int(value) + l[ind])):
                    l[ind] += int(value)
                    cursor.execute('DELETE FROM prov_infc WHERE NAME = ?', [prov])
                    cursor.execute(
                        f"INSERT INTO prov_infc VALUES({','.join(['?' for _ in range(len(PARAMETERS['prov']))])})",
                        l)
                    conn.commit()
                else:
                    vk.messages.send(
                        random_id=0,
                        user_id=user_id,
                        message=f'Ошибка: некорректное значение "{value}" для параметра "{parameter}".'
                    )
                    return
            else:
                vk.messages.send(
                    random_id=0,
                    user_id=user_id,
                    message=f'Ошибка: некорректный параметр "{parameter}".'
                )
                return
        vk.messages.send(
            random_id=0,
            user_id=user_id,
            message="Провинция изменена успешно."
        )
        show_prov(user_id, prov)

    else:
        vk.messages.send(
            random_id=0,
            user_id=user_id,
            message=NO_PERMISSION
        )


def add_country(args, user_id):
    if update_roles()[user_id] >= 2:
        list1 = []
        for i in range(len(args)):
            if CHECK['country'][i](args[i]):
                list1.append(args[i])
            else:
                return f'Ошибка во время чтения параметра №{i + 1}: {PARAMETERS["country"][i]}. Проверьте формат ввода сообщением "параметры страны" и попробуйте снова.'
        cursor.execute("SELECT * FROM country_infc WHERE NAME=?", [list1[0]])
        if len(cursor.fetchall()) > 0:
            return 'Такая страна уже есть.'
        cursor.execute(f"INSERT INTO country_infc VALUES({','.join(['?' for _ in range(len(PARAMETERS['country']))])})",
                       list1)
        conn.commit()
        return 'Страна успешно добавлена в список.'
    return NO_PERMISSION


def show_country(user_id, country=0):
    if country:
        cursor.execute('SELECT * FROM country_infc WHERE NAME = ?', [country])
        l = []
        try:
            d = list(cursor.fetchall()[0])
        except:
            vk.messages.send(random_id=0, user_id=user_id, message='Страна не найдена.')
            return 0
        if user_id == int(d[1]) or update_roles()[user_id] >= 2:
            d[1] = '@' + name(int(d[1]))
            for i in range(len(d)):
                l.append(f'{PARAMETERS["country"][i]}: {d[i]}')
            vk.messages.send(random_id=0, user_id=user_id, message='\n'.join(l))
        else:
            vk.messages.send(random_id=0, user_id=user_id, message=NO_PERMISSION)
    elif update_roles()[user_id] >= 2:
        cursor.execute('SELECT NAME FROM country_infc')
        d = list(map(lambda x: x[0], cursor.fetchall()))
        for country_name in d:
            show_country(user_id, country_name)
    else:
        vk.messages.send(random_id=0, user_id=user_id, message=NO_PERMISSION)


def edit_country(user_id, country, **kwargs):
    cursor.execute('SELECT * FROM country_infc WHERE NAME = ?', [country])
    l = list(cursor.fetchall()[0])
    if user_id == int(l[1]) and update_roles()[user_id] >= 2:
        for parameter, value in kwargs.items():
            if parameter in PARAMETERS['country']:
                ind = PARAMETERS['country'].index(parameter)
                if CHECK['country'][ind](value):
                    l[PARAMETERS['country'].index(parameter)] = int(value) if type(l[ind]) == int else value
                    cursor.execute('DELETE FROM country_infc WHERE NAME = ?', [country])
                    cursor.execute(
                        f"INSERT INTO country_infc VALUES({','.join(['?' for _ in range(len(PARAMETERS['country']))])})",
                        l)
                    conn.commit()
                elif value[1:].isdigit() and value[0] in ['+', '-'] and CHECK['country'][ind](str(int(value) + l[ind])):
                    l[ind] += int(value)
                    cursor.execute('DELETE FROM country_infc WHERE NAME = ?', [country])
                    cursor.execute(
                        f"INSERT INTO country_infc VALUES({','.join(['?' for _ in range(len(PARAMETERS['country']))])})",
                        l)
                    conn.commit()
                else:
                    vk.messages.send(
                        random_id=0,
                        user_id=user_id,
                        message=f'Ошибка: некорректное значение "{value}" для параметра "{parameter}".'
                    )
                    return
            else:
                vk.messages.send(
                    random_id=0,
                    user_id=user_id,
                    message=f'Ошибка: некорректный параметр "{parameter}".'
                )
                return
        vk.messages.send(
            random_id=0,
            user_id=user_id,
            message="Cтрана изменена успешно."
        )
        show_country(user_id, country)
    else:
        vk.messages.send(
            random_id=0,
            user_id=user_id,
            message=NO_PERMISSION
        )
