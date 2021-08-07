from kinopoisk_api.filmapis.filmapis import API_Cinema
from random import randint

object_api = API_Cinema('key')
out_dic_const = {"name": "", "countries": [], "genres": [], "year": ""}
out_dic_film = {"name": "", "year": "", "countries": [], "genres": [], "rating": "", "posterUrl": "", "id": 0}


def find_film(film):
    movie_dic = object_api.get_by_keyword(film)['films'][0]
    out_dic = out_dic_const.copy()
    out_dic["name"] = movie_dic['nameRu']
    out_dic["countries"] = movie_dic['countries']
    out_dic["genres"] = movie_dic['genres']
    out_dic["year"] = movie_dic['year']
    return out_dic


def find_filters(attributes, one_name, many_name):
    filters = object_api.get_filters()
    out_ids = []
    for item1 in filters[many_name]:
        for item2 in attributes:
            if item1[one_name] == item2:
                out_ids.append(int(item1["id"]))
    return out_ids


def find_years(years):
    min = 2021
    max = 1888
    for item in years:
        if int(item) > max:
            max = int(item)
        if int(item) < min:
            min = int(item)
    return [min, max]


def find_favourite(fav_genres, fav_countries, fav_years):
    ids_genres = find_filters(fav_genres, "genre", "genres")
    ids_countries = find_filters(fav_countries, "country", "countries")
    years = find_years(fav_years)
    # print(type(ids_genres[0]))
    # print(type(ids_countries[0]))
    # print(type(years[0]))
    page_count = object_api.get_film_in_filters(counry=ids_countries, genre=ids_genres, ratingFrom=4, yearFrom=years[0],
                                                yearTo=years[1], page=1)['pagesCount']
    all_films = []
    for i in range(1, page_count + 1):
        all_films.extend(object_api.get_film_in_filters(counry=ids_countries, genre=ids_genres, ratingFrom=4,
                                                        yearFrom=years[0], yearTo=years[1], page=i)['films'])
    print(len(all_films))
    film = all_films[randint(0, len(all_films))]
    out_dic = out_dic_film.copy()
    out_dic["countries"] = []
    out_dic["genres"] = []
    out_dic["name"] = film['nameRu']
    out_dic["year"] = film['year']
    for item in film['countries']:
        out_dic["countries"].append(item['country'])
    for item in film['genres']:
        out_dic["genres"].append(item['genre'])
    out_dic["rating"] = film['rating']
    out_dic["posterUrl"] = film['posterUrl']
    out_dic["id"] = film['filmId']
    return out_dic
