import telebot
import mongo
import re
import requests
import os

bot = telebot.TeleBot('key')
head = "https://www.kinopoisk.ru/film/"


def check_have_user(user):
    if not mongo.check_user(user.id):
        mongo.create_user(user)


@bot.message_handler(commands=["help"])
def help_com(message):
    check_have_user(message.from_user)
    help_text = "Вот действия которые я могу выполнить:\n1⃣ Советую фильм специально для вас " \
                "(/film или напиши:{Посоветуй фильм})\n2⃣ Слушаю, что вы посмотрели, чтобы рекомендации" \
                " были точнее (/listen или напиши:{Я посмотрел [Полное навание фильма]})\n" \
                "3⃣ Рассказываю что вы посмотрели последнее (/history или напиши:{Что я смотрел?})\n" \
                "4⃣ Составляю список желаемого (/wish или напиши:{Хочу посмотреть [Полное навание фильма]})\n" \
                "5⃣ Удаляю фильм из списка желаемого (/del_wish или напиши:{Хочу удалить [Полное навание фильма]})\n" \
                "6⃣ Показываю список желаемого (/wishlist или напиши:{Покажи список желаемого})\n"
    bot.send_photo(message.from_user.id, open("help.jpg", 'rb'), help_text)


@bot.message_handler(commands=["film"])
def film_com(message):
    check_have_user(message.from_user)
    if len(mongo.check_history(message.from_user.id)) > 0:
        bot.send_message(message.from_user.id, "Исходя из того, что ты посмотрел, думаю тебе понравится этот фильм🎯:")
        dic_film = mongo.advise_film(message.from_user.id)
        countries = ""
        for country in dic_film["countries"]:
            countries += f" {country}"
        genres = ""
        for genre in dic_film["genres"]:
            genres += f" {genre}"
        report = "Название: " + dic_film["name"] + "\nГод: " + dic_film["year"] + "\nСтраны:" + countries + "\nЖанры:" \
                 + genres + "\nРейтинг: " + dic_film["rating"] + "\nСсылка: " + head + str(dic_film["id"]) + "\\"
        picture = requests.get(dic_film["posterUrl"])
        out = open("temp.jpg", "wb")
        out.write(picture.content)
        out.close()
        bot.send_photo(message.from_user.id, open("temp.jpg", 'rb'), report)
        os.remove("/home/aleksandr/практика/5/temp.jpg")
    else:
        bot.send_message(message.from_user.id, "У меня нет никаких данных о тебе, расскажи какие фильмы ты посмотрел"
                                               " одним из двух способов (/listen или напиши:{Я посмотрел"
                                               " [Полное навание фильма]})\n"
                                               "Так же могу посоветовать топ-500 кинопоиска: "
                                               "https://www.kinopoisk.ru/lists/top500/")


@bot.message_handler(commands=["listen"])
def listen_com(message):
    check_have_user(message.from_user)
    msg = bot.send_message(message.from_user.id, "Напиши название фильма, который посмотрел")
    bot.register_next_step_handler(msg, listen_add)


def listen_add(message):
    film = ""
    if len(re.findall("Я посмотрел", message.text)) > 0:
        for i in range(12, len(message.text)):
            film += message.text[i]
    else:
        film = message.text
    mongo.add_history(message.from_user.id, film)
    bot.send_message(message.from_user.id, f"Фильм {film} успешно добавлен в историю просмотра."
                                           f" Посмотреть историю: /history")


@bot.message_handler(commands=["history"])
def history_com(message):
    check_have_user(message.from_user)
    list = mongo.show_history(message.from_user.id)
    if len(list) == 0:
        bot.send_message(message.from_user.id, "Ваша истоия пуста!📃\n"
                                               "Не беда, можно её пополнить через команду: /listen")
    else:
        history = ""
        for item in list:
            history += f"🎦 {item}\n"
        history += "Добавить просмотренный фильм можно через команду: /listen"
        bot.send_message(message.from_user.id, f"Вот что ты посмотрел:\n{history}")


@bot.message_handler(commands=["wish"])
def wish_com(message):
    check_have_user(message.from_user)
    msg = bot.send_message(message.from_user.id, "Напиши название фильма, который хочешь посмотреть")
    bot.register_next_step_handler(msg, wish_add)


def wish_add(message):
    film = ""
    if len(re.findall("Хочу посмотреть", message.text)) > 0:
        for i in range(16, len(message.text)):
            film += message.text[i]
    else:
        film = message.text
    mongo.add_wishlist(message.from_user.id, film)
    bot.send_message(message.from_user.id, f"Фильм {film} успешно добавлен в список желаемого."
                                           f" Посмотреть список: /wishlist")


@bot.message_handler(commands=["del_wish"])
def del_wish_com(message):
    check_have_user(message.from_user)
    msg = bot.send_message(message.from_user.id, "Напиши название фильма, который хотите удалить из списка желаемого")
    bot.register_next_step_handler(msg, wish_del)


def wish_del(message):
    film = ""
    if len(re.findall("Хочу удалить", message.text)) > 0:
        for i in range(13, len(message.text)):
            film += message.text[i]
    else:
        film = message.text
    if mongo.del_wishlist(message.from_user.id, film):
        bot.send_message(message.from_user.id, f"Фильм {film} успешно удален из списока желаемого."
                                               f" Посмотреть список: /wishlist")
    else:
        bot.send_message(message.from_user.id, f"Фильм {film} не найден в списке желаемого,"
                                               f" попробуйте /del_wish заново")


@bot.message_handler(commands=["wishlist"])
def wishlist_com(message):
    check_have_user(message.from_user)
    list = mongo.show_wishlist(message.from_user.id)
    if len(list) == 0:
        bot.send_message(message.from_user.id, "Ваш список пуст!📃\nНе беда, можно его пополнить через команду: /wish")
    else:
        wishlist = ""
        for item in list:
            wishlist += f"🎦 {item}\n"
        wishlist += "Удалить из него просмотренный фильм можно через команду: /del_wish"
        bot.send_message(message.from_user.id, f"Вот что ты отложил на потом:\n{wishlist}")


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    check_have_user(message.from_user)
    if len(re.findall("Хочу посмотреть", message.text)) > 0:
        wish_add(message)
    elif len(re.findall("Хочу удалить", message.text)) > 0:
        wish_del(message)
    elif len(re.findall("Покажи список желаемого", message.text)) > 0:
        wishlist_com(message)
    elif len(re.findall("Что я смотрел?", message.text)) > 0:
        history_com(message)
    elif len(re.findall("Я посмотрел", message.text)) > 0:
        listen_add(message)
    elif len(re.findall("Посоветуй фильм", message.text)) > 0:
        film_com(message)
    else:
        bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}👋🏻, я бот-советчик фильмов! "
                                               f"Я помогаю людям искать фильмы на их вкус.\n"
                                               f"Я тебя не очень понял напиши /help и узнаешь, что я способен понять.🙂")


bot.polling(none_stop=True, interval=0)
