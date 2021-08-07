import pymongo
import use_kinopoisk


def mongodb_connect():
    client = pymongo.MongoClient("localhost", 27017)
    return client.movie_adviser


db = mongodb_connect()
dic_user = {"user": {"nickname": "", "id": "", "name": "", "language_code": ""},
            "countries": [], "genres": [], "years": [], "history": [], "wish": []}


def check_user(user_id):
    a = db.users.find({"user.id": user_id})
    out = False
    for i in a:
        out = True
    return out


def create_user(user):
    dic_temp = dic_user.copy()
    dic_temp["user"]["nickname"] = user.username
    dic_temp["user"]["id"] = user.id
    if user.last_name:
        dic_temp["user"]["name"] = f"{user.first_name} {user.last_name}"
    else:
        dic_temp["user"]["name"] = user.first_name
    dic_temp["user"]["language_code"] = user.language_code
    db.users.insert_one(dic_temp)
    print(f"Добавлен пользователь {user.id}")


def add_wishlist(id, film):
    my_query = {"user.id": id}
    array = db.users.find_one(my_query)["wish"]
    array.append(film)
    new_values = {"$set": {"wish": array}}
    db.users.update_one(my_query, new_values)


def del_wishlist(id, film):
    my_query = {"user.id": id}
    array = db.users.find_one(my_query)["wish"]
    try:
        array.remove(film)
    except:
        return False
    new_values = {"$set": {"wish": array}}
    db.users.update_one(my_query, new_values)
    return True


def show_wishlist(id):
    my_query = {"user.id": id}
    array = db.users.find_one(my_query)["wish"]
    return array


def show_history(id):
    my_query = {"user.id": id}
    array = db.users.find_one(my_query)["history"]
    return array


def add_attribute(query, one_name, many_name, film_dic):
    attribute = db.users.find_one(query)[many_name]
    dic_attribute = {one_name: "", "count": 0}
    if len(attribute) > 0:
        for item1 in film_dic[many_name]:
            similar = False
            for item2 in attribute:
                if item2[one_name] == item1[one_name]:
                    item2["count"] += 1
                    similar = True
                    break
            if not similar:
                dic_temp = dic_attribute.copy()
                dic_temp[one_name] = item1[one_name]
                dic_temp["count"] = 1
                attribute.append(dic_temp)
    else:
        for item1 in film_dic[many_name]:
            dic_temp = dic_attribute.copy()
            dic_temp[one_name] = item1[one_name]
            dic_temp["count"] = 1
            attribute.append(dic_temp)
    new_values = {"$set": {many_name: attribute}}
    db.users.update_one(query, new_values)


def add_year(query, film_dic):
    years = db.users.find_one(query)["years"]
    dic_year = {"year": "", "count": 0}
    new_year = film_dic["year"]
    if len(years) > 0:
        for item in years:
            similar = False
            if item["year"] == new_year:
                item["count"] += 1
                similar = True
                break
        if not similar:
            dic_temp = dic_year.copy()
            dic_temp["year"] = new_year
            dic_temp["count"] = 1
            years.append(dic_temp)
    else:
        dic_temp = dic_year.copy()
        dic_temp["year"] = new_year
        dic_temp["count"] = 1
        years.append(dic_temp)
    new_values = {"$set": {"years": years}}
    db.users.update_one(query, new_values)


def add_history(id, film):
    my_query = {"user.id": id}
    film_dic = use_kinopoisk.find_film(film)
    history = db.users.find_one(my_query)["history"]
    history.append(film_dic["name"])
    new_values = {"$set": {"history": history}}
    db.users.update_one(my_query, new_values)
    add_attribute(my_query, "country", "countries", film_dic)
    add_attribute(my_query, "genre", "genres", film_dic)
    add_year(my_query, film_dic)


def find_favourite(name, attributes):
    max = 0
    out = []
    for item in attributes:
        if item["count"] > max:
            max = item["count"]
    for item in attributes:
        if item["count"] == max:
            out.append(item[name])
    return out


def advise_film(id):
    my_query = {"user.id": id}
    fav_countries = find_favourite("country", db.users.find_one(my_query)["countries"])
    fav_genres = find_favourite("genre", db.users.find_one(my_query)["genres"])
    fav_years = find_favourite("year", db.users.find_one(my_query)["years"])
    return use_kinopoisk.find_favourite(fav_genres, fav_countries, fav_years)


def check_history(id):
    my_query = {"user.id": id}
    return db.users.find_one(my_query)["history"]
