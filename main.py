from collections import deque
from functions import *
from vk_api.longpoll import VkEventType

vk, longpoll, conn, cursor = give_vars()

log = deque()

cursor.execute('pragma table_info(prov_infc)')
COLUMNS_PROV = list(map(lambda x: x[1], cursor.fetchall()))
cursor.execute('pragma table_info(country_infc)')
COLUMNS_COUNTRY = list(map(lambda x: x[1], cursor.fetchall()))
last_turn = 0

for event in longpoll.listen():
    try:
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if not role(event.user_id):
                cursor.execute('INSERT INTO users_infc VALUES(?,?)', [event.user_id, 1])
            # Слушаем longpoll, если пришло сообщение, то:
            cmd = list(map(lambda x: x.lower(), event.text.split()))
            if cmd[0] == 'log':
                if event.from_user and role(event.user_id) == 4:
                    for _ in range(len(log)):
                        vk.messages.send(
                            random_id=0,
                            user_id=event.user_id,
                            message=log[_][1] + ':\n' + log[_][0]
                        )
            elif cmd[0] == 'log_last':
                if event.from_user and role(event.user_id) == 4:
                    try:
                        log_last = log.pop()
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
                        if cmd[2] == ADMIN_KEY:
                            cursor.execute('UPDATE users_infc SET RANG = ? WHERE ID = ?', [2, event.user_id])
                            vk.messages.send(random_id=0, user_id=event.user_id, message='Роль успешно изменена.')
                        elif cmd[2] == MAIN_ADMIN_KEY:
                            cursor.execute('UPDATE users_infc SET RANG = ? WHERE ID = ?', [3, event.user_id])
                            vk.messages.send(random_id=0, user_id=event.user_id, message='Роль успешно изменена.')
                        elif cmd[2] == DEV_KEY:
                            cursor.execute('UPDATE users_infc SET RANG = ? WHERE ID = ?', [4, event.user_id])
                            vk.messages.send(random_id=0, user_id=event.user_id, message='Роль успешно изменена.')
                        else:
                            print(1 / 0)
                    except:
                        vk.messages.send(
                            random_id=0,
                            user_id=event.user_id,
                            message='Ошибка: некорректный ключ.'
                        )
            elif cmd[0] == 'роль':
                if event.from_user:
                    vk.messages.send(random_id=0, user_id=event.user_id,
                                     message=
                                     f'Ты {[0, "игрок", "админ", "главадмин", "разраб"][role(event.user_id)]}.')
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
                    if role(event.user_id) > role(cmd[1]) or role(event.user_id) == 4:
                        cursor.execute('UPDATE users_infc SET RANG = ? WHERE ID = ?', [max(1, role(cmd[1]) - int(cmd[2])), event.user_id])
                        vk.messages.send(random_id=0, user_id=event.user_id, message='Роль успешно изменена.')
                    else:
                        vk.messages.send(random_id=0, user_id=event.user_id, message=NO_PERMISSION)
            elif cmd[0] == 'повысить' and len(cmd) >= 2:
                if event.from_user:
                    if len(cmd) == 2:
                        cmd.append(1)
                    if not cmd[1].isdigit():
                        cmd[1] = id(cmd[1])
                    if role(event.user_id) > role(cmd[1]) + int(cmd[2]) or role(event.user_id) == 4:
                        cursor.execute('UPDATE users_infc SET RANG = ? WHERE ID = ?', [min(4, role(cmd[1]) + int(cmd[2])), event.user_id])
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
Роли - выводит информацию о получении ролей и их полномочиях.
Роль - выводит вашу роль.
Добавить страну - добавит страну в базу данных. Узнайте формат параметров командой "параметры страны".
Изменить страну х - изменяет параметры страны х. Формат: изменить страну {название}: {параметр_1}: {значение_1}, {параметр_2}: {значение_2}, ...
Показать страну x - выведет всю информацию о стране x.
Показать страны / страны - выведет всю информацию о всех странах.
Добавить провинцию - добавит провинцию в базу данных. Узнайте формат параметров командой "параметры провинции".
Изменить провинцию - аналогично такой же функции у стран. 
Показать провинцию x - выведет всю информацию о провинции x.
Показать провинции / провинции - выведет всю информацию о всех провинциях.'''
                )
            elif cmd[0:2] == ['добавить', 'страну']:
                if event.from_user:
                    args = delete_commas(cmd[2:])
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
                        message=f'Параметры: {", ".join(PARAMETERS["country"])}. Название - строка без цифр. '
                                f'Правитель - тег(@t13novik), но без @. Беспорядки - число от 0 до 10. Остальное - '
                                f'целые числа, не меньшие 0. Все аргументы писать через запятую+пробел(0, 0, 0)')
            elif cmd[0:2] == ['показать', 'страну']:
                show_country(event.user_id, cmd[2])
            elif cmd[0:2] == ['показать', 'страны'] or cmd[0] == 'страны':
                show_country(event.user_id)
            elif cmd[0:2] == ['изменить', 'страну']:
                params = ' '.join(cmd[2:]).replace(',', ':').replace('\n', ':').split(': ')
                cmd = cmd[0:2] + params
                if len(cmd) >= 5 and len(cmd) % 2:
                    d = {cmd[i]: cmd[i + 1][:-1] if cmd[i + 1][-1] == ',' else cmd[i + 1] for i in range(3, len(cmd), 2)}
                    edit_country(event.user_id, cmd[2], **d)
            elif cmd[0:2] == ['параметры', 'провинции']:
                if event.from_user:
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message=f'Параметры: {", ".join(PARAMETERS["prov"])}. Названия и имена - строки без цифр. '
                                f'Все аргументы писать через запятую+пробел(0, 0, 0)')
            elif cmd[:2] == ['добавить', 'провинцию']:
                if event.from_user:
                    args = ' '.join(cmd[2:]).split(', ')
                    print(args)
                    if len(args) != len(PARAMETERS['prov']):
                        vk.messages.send(
                            random_id=0,
                            user_id=event.user_id,
                            message='Ошибка: некорректное число параметров. Проверьте формат ввода сообщением "параметры провинции" и попробуйте снова.')
                        pass
                    else:
                        answer = add_prov(args, event.user_id)
                        vk.messages.send(
                            random_id=0,
                            user_id=event.user_id,
                            message=answer)
            elif cmd[0:2] == ['показать', 'провинцию']:
                show_prov(event.user_id, cmd[2])
            elif cmd[0:2] == ['показать', 'провинции'] or cmd[0] == 'провинции':
                show_prov(event.user_id)
            elif cmd[0:2] == ['изменить', 'провинцию']:
                params = ' '.join(cmd[2:]).replace(',', ':').replace('\n', ':').split(': ')
                cmd = cmd[0:2] + params
                if len(cmd) >= 5 and len(cmd) % 2:
                    d = {cmd[i]: cmd[i + 1][:-1] if cmd[i + 1][-1] == ',' else cmd[i + 1] for i in range(3, len(cmd), 2)}
                    edit_prov(event.user_id, cmd[2], **d)
            elif cmd[0] == 'test':
                print(event.text.split('\n'))
            elif cmd[0] == 'ход':
                msg, last_turn = turn(event.user_id, last_turn)
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=0,
                    message=msg)
            else:
                if event.from_user:
                    vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message='А вот это вот я не понимаю. Прости :('
                    )
            if 'log_last' != cmd[0] != 'log':
                log.append([event.text, '@' + name(event.user_id)])
                if len(log) >= 1000:
                    log.popleft()
    except EOFError:  # Тупа костыль, который пока деактивирован(вообще костыль нужен, чтобы бот никогда не падал)
        vk.messages.send(
                        random_id=0,
                        user_id=event.user_id,
                        message='Я сломался, напишите об этом кейсе @t13novik'
                    )
        print(event.text)
    conn.commit()
