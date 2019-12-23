import vk_api
import sqlite3
from base import create_base
from vk_api.longpoll import VkLongPoll, VkEventType
from collections import deque

token = 'd82dafe5d1e11f83b5fd893fac3c799632e3aa6f60eee4a86799c43138f00afc712a13adfb5022ca2e05c'
vk_session = vk_api.VkApi(token='55d012dfde7be9b48ac454b87c4e9b456bbbe91e5aeace2a7938ffba5b58c354f31a607a8261c81e7bd98')

longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
create_base()
conn = sqlite3.connect("main.db")
cursor = conn.cursor()

NO_PERMISSION = 'У вас недостаточно полномочий для использования этой команды.'
ADMIN_KEY = 'ww7ir32smf40djbq'
MAIN_ADMIN_KEY = 'djf7y4n9ia22ut85'
DEV_KEY = 'stronghold_top_wpg'
LOG = deque()
PARAMETERS = {'country': ['название', 'правитель', 'деньги', 'лес', 'еда', 'металлы', 'электроэнергия', 'нефть',
                          'моб.ресурс', 'количество призывников', 'гражданские ресурсы', 'горючее',
                          'военное снабжение', 'беспорядки'],

              'land': ['название', 'страна-владелец', 'игрок-владелец',
                       'ранг (провинция -> мегаполис, или открытое море/ИЭЗ)',
                       'тип провинции (сухопутная/морская)', 'статус - национальная, оккупированная и т.д',
                       'страна, оказывающая влияние на провинцию', 'постройка']}
CHECK = {'country': [lambda x: x.isalpha()] + [lambda x: x != 0] + [lambda x: x.isdigit()] * 11 +
                    [lambda x: x in [str(i) for i in range(11)]],
         'land': [lambda x: x.isalpha()] * 3 + [lambda x: x.isdigit()] + [lambda x: x in ['сухопутная', 'морская']] +
                 [lambda x: x in ['национальная', 'оккупированная', 'удерживаемая', 'под контролем']] +
         [lambda x: x.isalpha()] + [lambda x: x in ['лесопилка', 'фермы', 'шахта', 'ТЭЦ', 'АЭС', 'ВИЭ', 'скважина',
                                                    'завод', 'военная база', 'нпз', 'морской порт', 'авиабаза',
                                                    'система ПРО', 'бараки']]}


def name(id):
    return vk.users.get(user_id=id, fields='screen_name')[0]['screen_name']


def id(s):
    try:
        return vk.users.get(user_ids=s)[0]['id']
    except:
        return 0


def update_roles():
    global users
    cursor.execute('SELECT * FROM users_infc')
    users = {}
    for user, rang in cursor.fetchall():
        users[user] = int(rang)


def add_province(args, user_id):
    if users[user_id] >= 2:
        list1 = []
        for i in range(len(args)):
            if CHECK['land'][i](args[i]):
                list1.append(args[i])
            else:
                return f'Ошибка во время чтения параметра №{i + 1}: {PARAMETERS["land"][i]}. Проверьте формат ввода сообщением "параметры провинции" и попробуйте снова.'
        cursor.execute(f"INSERT INTO prov_infc VALUES({','.join(['?' for _ in range(len(PARAMETERS['land']))])})",
                       list1)
        sql = "SELECT * FROM prov_infc WHERE NAME=?"
        cursor.execute(sql, [(list1[1])])
        conn.commit()
        return 'Провинция успешно добавлена в список.'
    return vk.messages.send(random_id=0, user_id=user_id, message=NO_PERMISSION)


def add_user():
    print("Тут должно быть добавление нового пользователя")


def add_country(args, user_id):
    if users[user_id] >= 2:
        list1 = []
        for i in range(len(args)):
            if CHECK['country'][i](args[i]):
                list1.append(args[i])
            else:
                return f'Ошибка во время чтения параметра №{i + 1}: {PARAMETERS["country"][i]}. Проверьте формат ввода сообщением "параметры страны" и попробуйте снова.'
        cursor.execute(f"INSERT INTO country_infc VALUES({','.join(['?' for _ in range(len(PARAMETERS['country']))])})", list1)
        sql = "SELECT * FROM country_infc WHERE NAME=?"
        cursor.execute(sql, [(list1[1])])
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
        if user_id == int(d[1]) or users[user_id] >= 2:
            d[1] = '@' + name(int(d[1]))
            for i in range(len(d)):
                l.append(f'{PARAMETERS["country"][i]}: {d[i]}')
            vk.messages.send(random_id=0, user_id=user_id, message='\n'.join(l))
        else:
            vk.messages.send(random_id=0, user_id=user_id, message=NO_PERMISSION)
    elif users[user_id] >= 2:
        cursor.execute('SELECT NAME FROM country_infc')
        d = list(map(lambda x: x[0], cursor.fetchall()))
        for country_name in d:
            show_country(user_id, country_name)
    else:
        vk.messages.send(random_id=0, user_id=user_id, message=NO_PERMISSION)


update_roles()
for event in longpoll.listen():
    try:
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.user_id not in users:
                cursor.execute('INSERT INTO users_infc VALUES(?,?)', [event.user_id, 1])
                users[event.user_id] = 1
            # Слушаем longpoll, если пришло сообщение, то:
            cmd = list(map(lambda x: x.lower(), event.text.split()))
            if cmd[0] == 'log':
                if event.from_user and users[event.user_id] == 4:
                    for _ in range(len(LOG)):
                        vk.messages.send(
                            random_id=0,
                            user_id=event.user_id,
                            message=LOG[_][1] + ':\n' + LOG[_][0]
                        )
            elif cmd[0] == 'log_last':
                if event.from_user and users[event.user_id] == 4:
                    try:
                        log_last = LOG.pop()
                    except:
                        log_last = ['empty deque', 'Error']
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message=log_last[1] + ':\n' + log_last[0]
                    )
            elif cmd[0:2] == ['ввести', 'ключ']:
                if event.from_user:
                    try:
                        if cmd[2] == 'админ' and cmd[3] == ADMIN_KEY:
                            users[event.user_id] = 2
                            cursor.execute('UPDATE users_infc SET RANG = ? WHERE ID = ?', [2, event.user_id])
                            vk.messages.send(random_id=0, user_id=event.user_id, message='Роль успешно изменена.')
                        elif cmd[2] == 'главадмин' and cmd[3] == MAIN_ADMIN_KEY:
                            users[event.user_id] = 3
                            cursor.execute('UPDATE users_infc SET RANG = ? WHERE ID = ?', [3, event.user_id])
                            vk.messages.send(random_id=0, user_id=event.user_id, message='Роль успешно изменена.')
                        elif cmd[2] == 'разработчик' and cmd[3] == DEV_KEY:
                            users[event.user_id] = 4
                            cursor.execute('UPDATE users_infc SET RANG = ? WHERE ID = ?', [4, event.user_id])
                            vk.messages.send(random_id=0, user_id=event.user_id, message='Роль успешно изменена.')
                        else:
                            print(1 / 0)
                    except:
                        vk.messages.send(
                            random_id=0,
                            user_id=event.user_id,
                            message='Ошибка: некорректный запрос, роль или ключ. Используйте команду "роли"'
                        )
            elif cmd[0] == 'роль':
                if event.from_user:
                    vk.messages.send(random_id=0, user_id=event.user_id,
                                     message=
                                     f'Ты {[0, "игрок", "админ", "главадмин", "разраб"][users[event.user_id]]}.')
            elif cmd[0] == 'роли':
                if event.from_user:
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message='''Роли:
игрок -> админ -> главный админ.
Для получения роли выше игрока попросите, чтобы кто-то вас повысил(команда "повысить имя_человека(то, что с собачкой 
обычно, но писать без неё) на сколько уровней повысить"). Точно так же можно понижать людей, если вы выше них. Кроме 
того, вы можете использовать специальные ключи командой "ввести ключ [ключ]."
Узнать свою роль можно командой "роль".'''
                    )
            elif cmd[0] == 'понизить' and len(cmd) >= 2:
                if event.from_user:
                    if len(cmd) == 2:
                        cmd.append(1)
                    if not cmd[1].isdigit():
                        cmd[1] = id(cmd[1])
                    if cmd[1] in users and (users[event.user_id] > users[cmd[1]] or users[event.user_id] == 4):
                        users[cmd[1]] -= int(cmd[2])
                        users[cmd[1]] = max(1, users[cmd[1]])
                        cursor.execute('UPDATE users_infc SET RANG = ? WHERE ID = ?', [users[cmd[1]], event.user_id])
                        vk.messages.send(random_id=0, user_id=event.user_id, message='Роль успешно изменена.')
                    else:
                        vk.messages.send(random_id=0, user_id=event.user_id, message=NO_PERMISSION)
            elif cmd[0] == 'бот' or cmd[0] == 'начать':
                if event.from_user:
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message='''Привет! Я - бот.
    Пока что я нахожусь в разработке, так что функционала у меня не особо много.
    Но есть очень полезная команда "Помощь", набрав которую ты сможешь получить список действующих команд.'''
                    )
            elif cmd[0:3] == ['привет', 'от', 'цитадели']:
                if event.from_user:
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message='Люблю вас, кушайте хорошо и растите большими, мур'
                    )
            elif cmd[0] == 'помощь':
                if event.from_user:
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message='''Вот список моих команд:
Начать, Бот - вызовет приветствие.
Помощь - вызовет список команд.
Добавить страну - добавит страну в базу данных. Узнайте формат параметров командой "параметры страны".
Посмотреть страну x - выведет всю информацию о стране x.
Посмотреть страны - выведет всю информацию о всех странах.
Роли - выводит информацию о получении ролей и их полномочиях.
Добавить провинцию - добавит провинцию в базу данных. Формат - Используйте "параметры провинции".'''
                )
            elif cmd[0:2] == ['добавить', 'страну']:
                if event.from_user:
                    args = cmd[2:]
                    if len(args) != len(PARAMETERS['country']):
                        vk.messages.send(
                            random_id=0,
                            user_id=event.user_id,
                            message='Ошибка: некорректное число параметров. Проверьте формат ввода сообщением "параметры страны" и попробуйте снова.')
                        pass
                    else:
                        args[1] = id(args[1])
                        answer = add_country(args, event.user_id)
                        vk.messages.send(
                            random_id=0,
                            user_id=event.user_id,
                            message=answer)
            elif cmd[0:2] == ['параметры', 'страны']:
                if event.from_user:
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message=f'Параметры: {", ".join(PARAMETERS["country"])}. Название - строка без цифр. Правитель - тег(@t13novik), но без @. Беспорядки - число от 0 до 10. Остальное - целые числа, не меньшие 0.')
            elif cmd[0:2] == ['показать', 'страну']:
                show_country(event.user_id, cmd[2])
            elif cmd[0:2] == ['показать', 'страны']:
                show_country(event.user_id)
            elif cmd[0:2] == ['параметры', 'провинции']:
                if event.from_user:
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message=f'Параметры: {", ".join(PARAMETERS["land"])}. Названия и имена - строки без цифр.')
            elif cmd[0:2] == ['добавить', 'провинцию']:
                if event.from_user:
                    args = cmd[2:]
                    answer = add_province(args, event.user_id)
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message=answer)
            else:
                if event.from_user:
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message='А вот это вот я не понимаю. Прости :('
                    )
            if 'log_last' != cmd[0] != 'log':
                LOG.append([event.text, '@' + name(event.user_id)])
                if len(LOG) >= 500:
                    LOG.popleft()
    except EOFError:  # Тупа костыль, который пока деактивирован(вообще костыль нужен, чтобы бот никогда не падал)
        vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message='Я сломался, напишите об этом кейсе @t13novik'
                    )
        print(event.text)
