import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from neo4j import GraphDatabase
from io import StringIO

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

URI = os.environ.get("URI")
USERNAME = os.environ.get("UNAME")
PASSWORD = os.environ.get("PASSWORD")

driver = GraphDatabase.driver(uri=URI, auth=(USERNAME, PASSWORD))
api = Flask(__name__)
driver.verify_connectivity()


# /genres---------------------------------------------------------------------------------------------------------------


def get_genres(tx):
    locate_genre = """
        MATCH (genre:Genre)
        WITH genre.name AS genre, ID(genre) AS id
        RETURN genre, id
    """
    locate_genre_result = tx.run(locate_genre).data()
    return locate_genre_result


@api.route('/genres', methods=['GET'])
def get_genres_route():
    """
    http GET http://127.0.0.1:5000/genres
    :return: {}
    """
    with driver.session() as session:
        genres = session.read_transaction(get_genres)

    response = {'genres': genres}
    return jsonify(response)


def sort_genres_by_name(tx):
    locate_genre = """
        MATCH (genre:Genre)
        WITH genre.name AS genre, ID(genre) AS id
        RETURN genre, id
        ORDER BY genre
    """
    locate_genre_result = tx.run(locate_genre).data()
    return locate_genre_result


@api.route('/genres/sort/by_name', methods=['GET'])
def sort_genres_by_name_route():
    """
    http GET http://127.0.0.1:5000/genres/sort/by_name
    :return: {}
    """
    with driver.session() as session:
        genres = session.read_transaction(sort_genres_by_name)

    response = {'genres': genres}
    return jsonify(response)


def reverse_sort_genres_by_name(tx):
    locate_genre = """
        MATCH (genre:Genre)
        WITH genre.name AS genre, ID(genre) AS id
        RETURN genre, id
        ORDER BY genre DESC
    """
    locate_genre_result = tx.run(locate_genre).data()
    return locate_genre_result


@api.route('/genres/sort/reverse/by_name', methods=['GET'])
def reverse_sort_genres_by_name_route():
    """
    http GET http://127.0.0.1:5000/genres/sort/reverse/by_name
    :return: {}
    """
    with driver.session() as session:
        genres = session.read_transaction(reverse_sort_genres_by_name)

    response = {'genres': genres}
    return jsonify(response)


# /admin/genres---------------------------------------------------------------------------------------------------------


def add_genre(tx, name):
    locate_genre = "MATCH (genre:Genre {name: $name}) RETURN genre"
    locate_genre_result = tx.run(locate_genre, name=name).data()

    if not locate_genre_result:
        create_genre = "CREATE (:Genre {name: $name})"
        tx.run(create_genre, name=name)
        return {'name': name}


@api.route('/admin/genres', methods=['POST'])
def add_genre_route():
    """
    http POST http://127.0.0.1:5000/admin/genres genre="name"
    :return: {}
    """
    name = request.json['genre']

    with driver.session() as session:
        genre = session.write_transaction(add_genre, name)

    if not genre:
        response = {'message': 'Genre already exists!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_genre(tx, the_id):
    locate_genre = "MATCH (genre:Genre) WHERE ID(genre) = $the_id RETURN genre"
    locate_genre_result = tx.run(locate_genre, the_id=the_id).data()

    if locate_genre_result:
        remove_genre = "MATCH (genre:Genre) WHERE ID(genre) = $the_id DETACH DELETE genre"
        tx.run(remove_genre, the_id=the_id)
        return {'id': the_id}


@api.route('/admin/genres/<int:the_id>', methods=['DELETE'])
def delete_genre_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/admin/genres/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        genre = session.write_transaction(delete_genre, the_id)

    if not genre:
        response = {'message': 'Genre not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /persons--------------------------------------------------------------------------------------------------------------


def get_persons(tx):
    locate_person = """
        MATCH (person:Person)
        WITH person.name AS name, person.surname AS surname, person.photo AS photo, ID(person) AS id
        RETURN name, surname, photo, id
    """
    locate_person_result = tx.run(locate_person).data()
    return locate_person_result


@api.route('/persons', methods=['GET'])
def get_persons_route():
    """
    http GET http://127.0.0.1:5000/persons
    :return: {}
    """
    with driver.session() as session:
        persons = session.read_transaction(get_persons)

    response = {'persons': persons}
    return jsonify(response)


def find_person_by_name(tx, name, surname):
    locate_person = """
        MATCH (person:Person {name: $name, surname: $surname})
        WITH person.name AS name, person.surname AS surname, person.photo AS photo, ID(person) AS id
        RETURN name, surname, photo, id
    """
    locate_person_result = tx.run(locate_person, name=name, surname=surname).data()
    return locate_person_result


@api.route('/persons/find/by_name/<string:name>&<string:surname>', methods=['GET'])
def find_person_by_name_route(name, surname):
    """
    http GET http://127.0.0.1:5000/persons/find/by_name/<string:name>&<string:surname>
    :param name: string
    :param surname: string
    :return: {}
    """
    with driver.session() as session:
        person = session.read_transaction(find_person_by_name, name, surname)

    response = {'person': person}
    return jsonify(response)


def sort_persons_by_surname(tx):
    locate_person = """
        MATCH (person:Person)
        WITH person.name AS name, person.surname AS surname, person.photo AS photo, ID(person) AS id
        RETURN name, surname, photo, id
        ORDER BY surname
    """
    locate_person_result = tx.run(locate_person).data()
    return locate_person_result


@api.route('/persons/sort/by_name', methods=['GET'])
def sort_persons_by_surname_route():
    """
    http GET http://127.0.0.1:5000/persons/sort/by_name
    :return: {}
    """
    with driver.session() as session:
        persons = session.read_transaction(sort_persons_by_surname)

    response = {'persons': persons}
    return jsonify(response)


def reverse_sort_persons_by_surname(tx):
    locate_person = """
        MATCH (person:Person)
        WITH person.name AS name, person.surname AS surname, person.photo AS photo, ID(person) AS id
        RETURN name, surname, photo, id
        ORDER BY surname DESC
    """
    locate_person_result = tx.run(locate_person).data()
    return locate_person_result


@api.route('/persons/sort/reverse/by_name', methods=['GET'])
def reverse_sort_persons_by_surname_route():
    """
    http GET http://127.0.0.1:5000/persons/sort/reverse/by_name
    :return: {}
    """
    with driver.session() as session:
        persons = session.read_transaction(reverse_sort_persons_by_surname)

    response = {'persons': persons}
    return jsonify(response)


def sort_persons_by_roles(tx):
    locate_person = """
        MATCH (person:Person)
        OPTIONAL MATCH (person)-[conn:PLAYED]-(:Show)
        WITH person.name AS name,
            person.surname AS surname,
            person.photo AS photo,
            ID(person) AS id,
            count(conn) AS played
        RETURN name, surname, photo, id
        ORDER BY played DESC
    """
    locate_person_result = tx.run(locate_person).data()
    return locate_person_result


@api.route('/persons/sort/by_roles', methods=['GET'])
def sort_persons_by_roles_route():
    """
    http GET http://127.0.0.1:5000/persons/sort/by_roles
    :return: {}
    """
    with driver.session() as session:
        persons = session.read_transaction(sort_persons_by_roles)

    response = {'persons': persons}
    return jsonify(response)


def reverse_sort_persons_by_roles(tx):
    locate_person = """
        MATCH (person:Person)
        OPTIONAL MATCH (person)-[conn:PLAYED]-(:Show)
        WITH person.name AS name,
            person.surname AS surname,
            person.photo AS photo,
            ID(person) AS id,
            count(conn) AS played
        RETURN name, surname, photo, id
        ORDER BY played
    """
    locate_person_result = tx.run(locate_person).data()
    return locate_person_result


@api.route('/persons/sort/reverse/by_roles', methods=['GET'])
def reverse_sort_persons_by_roles_route():
    """
    http GET http://127.0.0.1:5000/persons/sort/reverse/by_roles
    :return: {}
    """
    with driver.session() as session:
        persons = session.read_transaction(reverse_sort_persons_by_roles)

    response = {'persons': persons}
    return jsonify(response)


def sort_persons_by_directed(tx):
    locate_person = """
        MATCH (person:Person)
        OPTIONAL MATCH (person)-[conn:DIRECTED]-(:Show)
        WITH person.name AS name,
            person.surname AS surname,
            person.photo AS photo,
            ID(person) AS id,
            count(conn) AS directed
        RETURN name, surname, photo, id
        ORDER BY directed DESC
    """
    locate_person_result = tx.run(locate_person).data()
    return locate_person_result


@api.route('/persons/sort/by_directed', methods=['GET'])
def sort_persons_by_directed_route():
    """
    http GET http://127.0.0.1:5000/persons/sort/by_directed
    :return: {}
    """
    with driver.session() as session:
        persons = session.read_transaction(sort_persons_by_directed)

    response = {'persons': persons}
    return jsonify(response)


def reverse_sort_persons_by_directed(tx):
    locate_person = """
        MATCH (person:Person)
        OPTIONAL MATCH (person)-[conn:DIRECTED]-(:Show)
        WITH person.name AS name,
            person.surname AS surname,
            person.photo AS photo,
            ID(person) AS id,
            count(conn) AS directed
        RETURN name, surname, photo, id
        ORDER BY directed
    """
    locate_person_result = tx.run(locate_person).data()
    return locate_person_result


@api.route('/persons/sort/reverse/by_directed', methods=['GET'])
def reverse_sort_persons_by_directed_route():
    """
    http GET http://127.0.0.1:5000/persons/sort/reverse/by_directed
    :return: {}
    """
    with driver.session() as session:
        persons = session.read_transaction(reverse_sort_persons_by_directed)

    response = {'persons': persons}
    return jsonify(response)


def get_person_info(tx, the_id):
    locate_person = """
        MATCH (person:Person)
        WHERE ID(person) = $the_id
        OPTIONAL MATCH (person)-[played:PLAYED]-(in:Show)
        OPTIONAL MATCH (person)-[:DIRECTED]-(what:Show)
        WITH person,
            ID(person) AS id,
            collect(distinct played.role) AS roles,
            collect(distinct in.title) AS filmography,
            collect(distinct what.title) AS directed
        RETURN person, id, roles, filmography, directed
    """
    locate_person_result = tx.run(locate_person, the_id=the_id).data()

    if locate_person_result:
        person = {
            'id': locate_person_result[0]['id'],
            'name': locate_person_result[0]['person']['name'],
            'surname': locate_person_result[0]['person']['surname'],
            'born': locate_person_result[0]['person']['born'],
            'photo': locate_person_result[0]['person']['photo'],
            'filmography': [{
                'role': locate_person_result[0]['roles'][i],
                'title': locate_person_result[0]['filmography'][i]
            } for i in range(0, len(locate_person_result[0]['roles']))],
            'directed': locate_person_result[0]['directed']
        }
        return person


@api.route('/persons/<int:the_id>', methods=['GET'])
def get_person_info_route(the_id):
    """
    http GET http://127.0.0.1:5000/persons/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        person = session.read_transaction(get_person_info, the_id)

    if not person:
        response = {'message': 'Person not found!'}
        return jsonify(response)
    else:
        response = {'person': person}
        return jsonify(response)


# /admin/persons--------------------------------------------------------------------------------------------------------


def add_person(tx, name, surname, born, photo):
    locate_person = "MATCH (person:Person {name: $name, surname: $surname, born: $born}) RETURN person"
    locate_person_result = tx.run(locate_person, name=name, surname=surname, born=born).data()

    if not locate_person_result:
        create_person = "CREATE (:Person {name: $name, surname: $surname, born: $born, photo: $photo})"
        tx.run(create_person, name=name, surname=surname, born=born, photo=photo)
        return {'name': name, 'surname': surname, 'born': born, 'photo': photo}


@api.route('/admin/persons', methods=['POST'])
def add_person_route():
    """
    http POST http://127.0.0.1:5000/admin/persons name="name" surname="surname" born=1999 photo="photoURL"
    :return: {}
    """
    name = request.json['name']
    surname = request.json['surname']
    born = request.json['born']
    photo = request.json['photo']

    with driver.session() as session:
        person = session.write_transaction(add_person, name, surname, born, photo)

    if not person:
        response = {'message': 'This person is already in database!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def put_person_info(tx, the_id, name, surname, born, photo):
    locate_person = "MATCH (person:Person) WHERE ID(person) = $the_id RETURN person"
    locate_person_result = tx.run(locate_person, the_id=the_id).data()

    if locate_person_result:
        update_person = """
            MATCH (person:Person)
            WHERE ID(person) = $the_id
            SET person.name = $name, person.surname = $surname, person.born = $born, person.photo = $photo
        """
        tx.run(update_person, the_id=the_id, name=name, surname=surname, born=born, photo=photo).data()
        return {'name': name, 'surname': surname, 'born': born, 'photo': photo}


@api.route('/admin/persons/<int:the_id>', methods=['PUT'])
def put_person_info_route(the_id):
    """
    http PUT http://127.0.0.1:5000/admin/persons/<int:the_id> name="name" surname="surname" born=1999 photo="photoURL"
    :param the_id: int
    :return: {}
    """
    name = request.json['name']
    surname = request.json['surname']
    born = request.json['born']
    photo = request.json['photo']

    with driver.session() as session:
        person = session.write_transaction(put_person_info, the_id, name, surname, born, photo)

    if not person:
        response = {'message': 'Person not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_person(tx, the_id):
    locate_person = "MATCH (person:Person) WHERE ID(person) = $the_id RETURN person"
    locate_person_result = tx.run(locate_person, the_id=the_id).data()

    if locate_person_result:
        detach_delete_person = """
            MATCH (person:Person)
            WHERE ID(person) = $the_id
            DETACH DELETE person
        """
        tx.run(detach_delete_person, the_id=the_id)
        return {'the_id': the_id}


@api.route('/admin/persons/<int:the_id>', methods=['DELETE'])
def delete_person_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/admin/persons/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        person = session.write_transaction(delete_person, the_id)

    if not person:
        response = {'message': 'Person not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /shows----------------------------------------------------------------------------------------------------------------


def get_shows(tx):
    locate_title = """
        MATCH (show:Show)-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[like:LIKES]-(:User)
        WITH show.title AS title, show.photo AS photo, genre.name AS genre, ID(show) AS id, count(like) AS score
        RETURN title, photo, genre, id, score
    """
    locate_title_result = tx.run(locate_title).data()
    return locate_title_result


@api.route('/shows', methods=['GET'])
def get_shows_route():
    """
    http GET http://127.0.0.1:5000/shows
    :return: {}
    """
    with driver.session() as session:
        shows = session.read_transaction(get_shows)

    response = {'shows': shows}
    return jsonify(response)


def get_top_shows(tx):
    locate_title = """
        MATCH (show:Show)-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[like:LIKES]-(:User)
        WITH show.title AS title, show.photo AS photo, ID(show) AS id, genre.name AS genre, count(like) AS score
        RETURN title, photo, genre, id, score
        ORDER BY score DESC
        LIMIT 5
    """
    locate_title_result = tx.run(locate_title).data()
    return locate_title_result


@api.route('/shows/top', methods=['GET'])
def get_top_shows_route():
    """
    http GET http://127.0.0.1:5000/shows/top
    :return: {}
    """
    with driver.session() as session:
        shows = session.read_transaction(get_top_shows)

    response = {'shows': shows}
    return jsonify(response)


def find_show_by_name(tx, title):
    locate_title = """
        MATCH (show:Show {title: $title})-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[like:LIKES]-(:User)
        WITH show.title AS title, show.photo AS photo, ID(show) AS id, genre.name AS genre, count(like) AS score
        RETURN title, photo, id, genre, score
    """
    locate_title_result = tx.run(locate_title, title=title).data()
    return locate_title_result


@api.route('/shows/find/by_name/<string:title>', methods=['GET'])
def find_show_by_name_route(title):
    """
    http GET http://127.0.0.1:5000/shows/find/by_name/<string:title>
    :param title: string
    :return: {}
    """
    with driver.session() as session:
        show = session.read_transaction(find_show_by_name, title)

    response = {'show': show}
    return jsonify(response)


def sort_shows_by_genre(tx):
    locate_title = """
        MATCH (show:Show)-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[like:LIKES]-(:User)
        WITH show.title AS title, show.photo AS photo, genre.name AS genre, ID(show) AS id, count(like) AS score
        RETURN title, photo, genre, id, score
        ORDER BY genre
    """
    locate_title_result = tx.run(locate_title).data()
    return locate_title_result


@api.route('/shows/sort/by_genre', methods=['GET'])
def sort_shows_by_genre_route():
    """
    http GET http://127.0.0.1:5000/shows/sort/by_genre
    :return: {}
    """
    with driver.session() as session:
        shows = session.read_transaction(sort_shows_by_genre)

    response = {'shows': shows}
    return jsonify(response)


def reverse_sort_shows_by_genre(tx):
    locate_title = """
        MATCH (show:Show)-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[like:LIKES]-(:User)
        WITH show.title AS title, show.photo AS photo, genre.name AS genre, ID(show) AS id, count(like) AS score
        RETURN title, photo, genre, id, score
        ORDER BY genre DESC
    """
    locate_title_result = tx.run(locate_title).data()
    return locate_title_result


@api.route('/shows/sort/reverse/by_genre', methods=['GET'])
def reverse_sort_shows_by_genre_route():
    """
    http GET http://127.0.0.1:5000/shows/sort/reverse/by_genre
    :return: {}
    """
    with driver.session() as session:
        shows = session.read_transaction(reverse_sort_shows_by_genre)

    response = {'shows': shows}
    return jsonify(response)


def sort_shows_by_title(tx):
    locate_title = """
        MATCH (show:Show)-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[like:LIKES]-(:User)
        WITH show.title AS title, show.photo AS photo, genre.name AS genre, ID(show) AS id, count(like) AS score
        RETURN title, photo, genre, id, score
        ORDER BY title
    """
    locate_title_result = tx.run(locate_title).data()
    return locate_title_result


@api.route('/shows/sort/by_name', methods=['GET'])
def sort_shows_by_title_route():
    """
    http GET http://127.0.0.1:5000/shows/sort/by_name
    :return: {}
    """
    with driver.session() as session:
        shows = session.read_transaction(sort_shows_by_title)

    response = {'shows': shows}
    return jsonify(response)


def reverse_sort_shows_by_title(tx):
    locate_title = """
        MATCH (show:Show)-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[like:LIKES]-(:User)
        WITH show.title AS title, show.photo AS photo, genre.name AS genre, ID(show) AS id, count(like) AS score
        RETURN title, photo, genre, id, score
        ORDER BY title DESC
    """
    locate_title_result = tx.run(locate_title).data()
    return locate_title_result


@api.route('/shows/sort/reverse/by_name', methods=['GET'])
def reverse_sort_shows_by_title_route():
    """
    http GET http://127.0.0.1:5000/shows/sort/reverse/by_name
    :return: {}
    """
    with driver.session() as session:
        shows = session.read_transaction(reverse_sort_shows_by_title)

    response = {'shows': shows}
    return jsonify(response)


def sort_shows_by_score(tx):
    locate_title = """
        MATCH (show:Show)-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[like:LIKES]-(:User)
        WITH show.title AS title, show.photo AS photo, genre.name AS genre, ID(show) AS id, count(like) AS score
        RETURN title, photo, genre, id, score
        ORDER BY score DESC
    """
    locate_title_result = tx.run(locate_title).data()
    return locate_title_result


@api.route('/shows/sort/by_score', methods=['GET'])
def sort_shows_by_score_route():
    """
    http GET http://127.0.0.1:5000/shows/sort/by_score
    :return: {}
    """
    with driver.session() as session:
        shows = session.read_transaction(sort_shows_by_score)

    response = {'shows': shows}
    return jsonify(response)


def reverse_sort_shows_by_score(tx):
    locate_title = """
        MATCH (show:Show)-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[like:LIKES]-(:User)
        WITH show.title AS title, show.photo AS photo, genre.name AS genre, ID(show) AS id, count(like) AS score
        RETURN title, photo, genre, id, score
        ORDER BY score
    """
    locate_title_result = tx.run(locate_title).data()
    return locate_title_result


@api.route('/shows/sort/reverse/by_score', methods=['GET'])
def reverse_sort_shows_by_score_route():
    """
    http GET http://127.0.0.1:5000/shows/sort/reverse/by_score
    :return: {}
    """
    with driver.session() as session:
        shows = session.read_transaction(reverse_sort_shows_by_score)

    response = {'shows': shows}
    return jsonify(response)


def get_show_info(tx, the_id):
    locate_title = """
        MATCH (show:Show)-[:BELONGS]-(genre:Genre)
        WHERE ID(show) = $the_id
        OPTIONAL MATCH (show)-[:DIRECTED]-(director:Person)
        OPTIONAL MATCH (show)-[played:PLAYED]-(actor:Person)
        OPTIONAL MATCH (show)-[:LIKES]-(user:User)
        OPTIONAL MATCH (show)-[:ABOUT]-(review:Review)
        OPTIONAL MATCH (review)-[:WROTE]-(author:User)
        WITH show,
            genre,
            ID(show) AS id,
            collect(distinct director) AS directors,
            collect(distinct played.role) AS roles,
            collect(distinct actor) AS cast,
            count(distinct user) AS score,
            collect(distinct review) AS reviews,
            collect(distinct ID(review)) AS review_ids,
            collect(distinct author) AS authors
        RETURN show, genre, id, directors, roles, cast, score, reviews, review_ids, authors
    """
    locate_title_result = tx.run(locate_title, the_id=the_id).data()

    if locate_title_result:
        show = {
            'id': locate_title_result[0]['id'],
            'title': locate_title_result[0]['show']['title'],
            'genre': locate_title_result[0]['genre']['name'],
            'photo': locate_title_result[0]['show']['photo'],
            'trailer': locate_title_result[0]['show']['trailer'],
            'episodes': locate_title_result[0]['show']['episodes'],
            'released': locate_title_result[0]['show']['released'],
            'ended': locate_title_result[0]['show']['ended'],
            'director': [{
                'name': locate_title_result[0]['directors'][i]['name'],
                'surname': locate_title_result[0]['directors'][i]['surname']
            } for i in range(0, len(locate_title_result[0]['directors']))],
            'cast': [{
                'name': locate_title_result[0]['cast'][i]['name'],
                'surname': locate_title_result[0]['cast'][i]['surname'],
                'as': locate_title_result[0]['roles'][i]
            } for i in range(0, len(locate_title_result[0]['cast']))],
            'score': locate_title_result[0]['score'],
            'reviews': [{
                'author': locate_title_result[0]['authors'][i]['nick'],
                'body': locate_title_result[0]['reviews'][i]['body'],
                'id': locate_title_result[0]['review_ids'][i]
            } for i in range(0, len(locate_title_result[0]['reviews']))]
        }
        return show


@api.route('/shows/<int:the_id>', methods=['GET'])
def get_show_info_route(the_id):
    """
    http GET http://127.0.0.1:5000/shows/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        show = session.read_transaction(get_show_info, the_id)

    if not show:
        response = {'message': 'Show not found!'}
        return jsonify(response)
    else:
        response = {'show': show}
        return jsonify(response)


# /admin/shows----------------------------------------------------------------------------------------------------------


def add_show(tx, title, genre, photo, trailer, episodes, released, ended):
    locate_title = "MATCH (show:Show {title: $title}) RETURN show"
    locate_title_result = tx.run(locate_title, title=title).data()

    locate_genre = "MATCH (genre:Genre {name: $genre}) RETURN genre"
    locate_genre_result = tx.run(locate_genre, genre=genre).data()

    if not locate_title_result and locate_genre_result:
        create_show = """
            MATCH (genre:Genre {name: $genre})
            CREATE (:Show {
                title: $title,
                photo: $photo,
                trailer: $trailer,
                episodes: $episodes,
                released: $released,
                ended:$ended
            })-[:BELONGS]->(genre)
        """
        tx.run(create_show,
               title=title,
               genre=genre,
               photo=photo,
               trailer=trailer,
               episodes=episodes,
               released=released,
               ended=ended)
        return {
            'title': title,
            'genre': genre,
            'photo': photo,
            'trailer': trailer,
            'episodes': episodes,
            'released': released,
            'ended': ended
        }


@api.route('/admin/shows', methods=['POST'])
def add_show_route():
    """
    http POST http://127.0.0.1:5000/admin/shows title="title" genre="genre" photo="photoURL" trailer="trailerURL"
    episodes=10 released="01/12/2000" ended="01/12/2001"
    :return: {}
    """
    title = request.json['title']
    genre = request.json['genre']
    photo = request.json['photo']
    trailer = request.json['trailer']
    episodes = request.json['episodes']
    released = request.json['released']
    ended = request.json['ended']

    with driver.session() as session:
        show = session.write_transaction(add_show, title, genre, photo, trailer, episodes, released, ended)

    if not show:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def put_show_info(tx, the_id, title, genre, photo, trailer, episodes, released, ended):
    locate_title = "MATCH (show:Show) WHERE ID(show) = $the_id RETURN show"
    locate_title_result = tx.run(locate_title, the_id=the_id).data()

    locate_genre = "MATCH (genre:Genre {name: $genre}) RETURN genre"
    locate_genre_result = tx.run(locate_genre, genre=genre).data()

    if locate_title_result and locate_genre_result:
        update_show = """
            MATCH (show:Show)-[old:BELONGS]-(:Genre) WHERE ID(show) = $the_id
            MATCH (genre:Genre {name: $genre})
            DELETE old
            CREATE (show)-[:BELONGS]->(genre)
            SET show.title = $title,
                show.photo = $photo,
                show.trailer = $trailer,
                show.episodes = $episodes,
                show.released = $released,
                show.ended = $ended
        """
        tx.run(
            update_show,
            the_id=the_id,
            title=title,
            genre=genre,
            photo=photo,
            trailer=trailer,
            episodes=episodes,
            released=released,
            ended=ended
        )
        return {'the_id': the_id}


@api.route('/admin/shows/<int:the_id>', methods=['PUT'])
def put_show_info_route(the_id):
    """
    http PUT http://127.0.0.1:5000/admin/shows/<int:the_id> title="title" genre="genre" photo="photoURL"
    trailer="trailerURL" episodes=00 released="01/12/2000" ended="01/12/2001"
    :param the_id: int
    :return: {}
    """
    title = request.json['title']
    genre = request.json['genre']
    photo = request.json['photo']
    trailer = request.json['trailer']
    episodes = request.json['episodes']
    released = request.json['released']
    ended = request.json['ended']

    with driver.session() as session:
        show = session.write_transaction(put_show_info, the_id, title, genre, photo, trailer, episodes, released, ended)

    if not show:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_show(tx, the_id):
    locate_title = "MATCH (show:Show) WHERE ID(show) = $the_id RETURN show"
    locate_title_result = tx.run(locate_title, the_id=the_id).data()

    if locate_title_result:
        remove_show = "MATCH (show:Show) WHERE ID(show) = $the_id DETACH DELETE show"
        tx.run(remove_show, the_id=the_id)
        return {'id': the_id}


@api.route('/admin/shows/<int:the_id>', methods=['DELETE'])
def delete_show_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/admin/shows/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        show = session.write_transaction(delete_show, the_id)
    if not show:
        response = {'message': 'Show not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /users----------------------------------------------------------------------------------------------------------------


def get_users(tx):
    locate_user = """
        MATCH (user:User)
        WITH ID(user) AS id, user.nick AS nick, user.e_mail AS e_mail, user.photo AS photo 
        RETURN id, nick, e_mail, photo
    """
    locate_user_result = tx.run(locate_user).data()
    return locate_user_result


@api.route('/users', methods=['GET'])
def get_users_route():
    """
    http GET http://127.0.0.1:5000/users
    :return: {}
    """
    with driver.session() as session:
        users = session.read_transaction(get_users)

    response = {'users': users}
    return jsonify(response)


def find_user_by_name(tx, nick):
    locate_user = """
        MATCH (user:User {nick: $nick})
        WITH ID(user) AS id, user.nick AS nick, user.e_mail AS e_mail, user.photo AS photo 
        RETURN id, nick, e_mail, photo
    """
    locate_user_result = tx.run(locate_user, nick=nick).data()
    return locate_user_result


@api.route('/users/find/by_name/<string:nick>', methods=['GET'])
def find_user_by_name_route(nick):
    """
    http GET http://127.0.0.1:5000/users/find/by_name/<string:nick>
    :param nick: string
    :return: {}
    """
    with driver.session() as session:
        user = session.read_transaction(find_user_by_name, nick)

    response = {'user': user}
    return jsonify(response)


def sort_users_by_name(tx):
    locate_user = """
        MATCH (user:User)
        WITH ID(user) AS id, user.nick AS nick, user.e_mail AS e_mail, user.photo AS photo 
        RETURN id, nick, e_mail, photo
        ORDER BY nick
    """
    locate_user_result = tx.run(locate_user).data()
    return locate_user_result


@api.route('/users/sort/by_name', methods=['GET'])
def sort_users_by_name_route():
    """
    http GET http://127.0.0.1:5000/users/sort/by_name
    :return: {}
    """
    with driver.session() as session:
        users = session.read_transaction(sort_users_by_name)

    response = {'users': users}
    return jsonify(response)


def reverse_sort_users_by_name(tx):
    locate_user = """
        MATCH (user:User)
        WITH ID(user) AS id, user.nick AS nick, user.e_mail AS e_mail, user.photo AS photo 
        RETURN id, nick, e_mail, photo
        ORDER BY nick DESC
    """
    locate_user_result = tx.run(locate_user).data()
    return locate_user_result


@api.route('/users/sort/reverse/by_name', methods=['GET'])
def reverse_sort_users_by_name_route():
    """
    http GET http://127.0.0.1:5000/users/sort/reverse/by_name
    :return: {}
    """
    with driver.session() as session:
        users = session.read_transaction(reverse_sort_users_by_name)

    response = {'users': users}
    return jsonify(response)


def sort_users_by_activity(tx):
    locate_user = """
        MATCH (user:User)
        OPTIONAL MATCH (user)-[conn:WROTE|COMMENTS]-(:Review)
        WITH ID(user) AS id, user.nick AS nick, user.e_mail AS e_mail, user.photo AS photo, count(conn) AS activity
        RETURN id, nick, e_mail, photo
        ORDER BY activity DESC
    """
    locate_user_result = tx.run(locate_user).data()
    return locate_user_result


@api.route('/users/sort/by_activity', methods=['GET'])
def sort_users_by_activity_route():
    """
    http GET http://127.0.0.1:5000/users/sort/by_activity
    :return: {}
    """
    with driver.session() as session:
        users = session.read_transaction(sort_users_by_activity)

    response = {'users': users}
    return jsonify(response)


def reverse_sort_users_by_activity(tx):
    locate_user = """
        MATCH (user:User)
        OPTIONAL MATCH (user)-[conn:WROTE|COMMENTS]-(:Review)
        WITH ID(user) AS id, user.nick AS nick, user.e_mail AS e_mail, user.photo AS photo, count(conn) AS activity
        RETURN id, nick, e_mail, photo
        ORDER BY activity
    """
    locate_user_result = tx.run(locate_user).data()
    return locate_user_result


@api.route('/users/sort/reverse/by_activity', methods=['GET'])
def reverse_sort_users_by_activity_route():
    """
    http GET http://127.0.0.1:5000/users/sort/reverse/by_activity
    :return: {}
    """
    with driver.session() as session:
        users = session.read_transaction(reverse_sort_users_by_activity)

    response = {'users': users}
    return jsonify(response)


def get_top_users(tx):
    locate_user = """
        MATCH (user:User)
        OPTIONAL MATCH (user)-[conn:WROTE|COMMENTS]-(:Review)
        WITH ID(user) AS id, user.nick AS nick, user.e_mail AS e_mail, user.photo AS photo, count(conn) AS activity
        RETURN id, nick, e_mail, photo
        ORDER BY activity DESC
        LIMIT 3
    """
    locate_user_result = tx.run(locate_user).data()
    return locate_user_result


@api.route('/users/top', methods=['GET'])
def get_top_users_route():
    """
    http GET http://127.0.0.1:5000/users/top
    :return: {}
    """
    with driver.session() as session:
        users = session.read_transaction(get_top_users)

    response = {'users': users}
    return jsonify(response)


def get_user_info(tx, the_id):
    locate_user = """
        MATCH (user:User)
        WHERE ID(user) = $the_id
        OPTIONAL MATCH (user)-[:SEEN]-(seen:Show)
        OPTIONAL MATCH (user)-[:LIKES]-(liked:Show)
        OPTIONAL MATCH (user)-[:WANTS_TO_WATCH]-(to_watch:Show)
        OPTIONAL MATCH (user)-[:WROTE]-(written:Review)-[:ABOUT]-(review_about:Show)
        OPTIONAL MATCH (user)-[comment:COMMENTS]-(commented:Review)-[:ABOUT]-(comment_about:Show)
        OPTIONAL MATCH (commented)-[:WROTE]-(author:User)
        WITH user,
            ID(user) AS id,
            collect(distinct seen.title) AS seen_shows,
            collect(distinct liked.title) AS favourite,
            collect(distinct to_watch.title) AS watchlist,
            collect(distinct written.body) AS written_reviews,
            collect(review_about.title) AS reviews_titles,
            collect(distinct comment.comment) AS comments,
            collect(comment_about.title) AS comments_titles,
            collect(distinct ID(comment)) AS comments_ids,
            collect(author.nick) AS authors
        RETURN user,
            id,
            seen_shows,
            favourite,
            watchlist,
            written_reviews,
            reviews_titles,
            comments,
            comments_titles,
            comments_ids,
            authors
    """
    locate_user_result = tx.run(locate_user, the_id=the_id).data()

    if locate_user_result:
        user = {
            'nick': locate_user_result[0]['user']['nick'],
            'e_mail': locate_user_result[0]['user']['e_mail'],
            'registered': locate_user_result[0]['user']['registered'],
            'photo': locate_user_result[0]['user']['photo'],
            'id': locate_user_result[0]['id'],
            'seen_shows': locate_user_result[0]['seen_shows'],
            'favourite': locate_user_result[0]['favourite'],
            'watchlist': locate_user_result[0]['watchlist'],
            'reviews': [{
                'review': locate_user_result[0]['written_reviews'][i],
                'title': locate_user_result[0]['reviews_titles'][i]
            } for i in range(0, len(locate_user_result[0]['written_reviews']))],
            'comments': [{
                'review': {
                    'author': locate_user_result[0]['authors'][i],
                    'title': locate_user_result[0]['comments_titles'][i]
                },
                'comment': locate_user_result[0]['comments'][i],
                'id': locate_user_result[0]['comments_ids'][i]
            } for i in range(0, len(locate_user_result[0]['comments']))]
        }
        return user


@api.route('/users/<int:the_id>', methods=['GET'])
def get_user_info_route(the_id):
    """
    http GET http://127.0.0.1:5000/users/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        user = session.read_transaction(get_user_info, the_id)

    if not user:
        response = {'message': 'User not found!'}
        return jsonify(response)
    else:
        response = {'user': user}
        return jsonify(response)


# /admin/users----------------------------------------------------------------------------------------------------------


def add_user(tx, nick, e_mail, password, registered, photo):
    locate_user = "MATCH (user:User {nick: $nick}) RETURN user"
    locate_user_result = tx.run(locate_user, nick=nick).data()

    if not locate_user_result:
        create_user = """
            CREATE (:User {nick: $nick, e_mail: $e_mail, password: $password, registered: $registered, photo: $photo})
        """
        tx.run(create_user, nick=nick, e_mail=e_mail, password=password, registered=registered, photo=photo)
        return {'user': nick}


@api.route('/admin/users', methods=['POST'])
def add_user_route():
    """
    http POST http://127.0.0.1:5000/admin/users nick="nick" e_mail="e_mail" password="password" registered="01/12/2000"
    photo="photoURL"
    :return: {}
    """
    nick = request.json['nick']
    e_mail = request.json['e_mail']
    password = request.json['password']
    registered = request.json['registered']
    photo = request.json['photo']

    with driver.session() as session:
        user = session.write_transaction(add_user, nick, e_mail, password, registered, photo)

    if not user:
        response = {'message': 'User already exists in database!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def put_user_info(tx, the_id, nick, e_mail, password, registered, photo):
    locate_user = "MATCH (user:User) WHERE ID(user) = $the_id RETURN user"
    locate_user_result = tx.run(locate_user, the_id=the_id).data()

    if locate_user_result:
        update_user = """
            MATCH (user:User) WHERE ID(user) = $the_id
            SET user.nick = $nick,
                user.e_mail = $e_mail,
                user.password = $password,
                user.registered = $registered,
                user.photo = $photo
        """
        tx.run(update_user,
               the_id=the_id,
               nick=nick,
               e_mail=e_mail,
               password=password,
               registered=registered,
               photo=photo
               )
        return {'user': nick, 'e_mail': e_mail, 'registered': registered, 'photo': photo}


@api.route('/admin/users/<int:the_id>', methods=['PUT'])
def put_user_info_route(the_id):
    """
    http PUT http://127.0.0.1:5000/admin/users/<int:the_id> nick="nick" e_mail="e_mail" password="password"
    registered="01/12/2000" photo="photoURL"
    :param the_id: int
    :return: {}
    """
    nick = request.json['nick']
    e_mail = request.json['e_mail']
    password = request.json['password']
    registered = request.json['registered']
    photo = request.json['photo']

    with driver.session() as session:
        user = session.write_transaction(put_user_info, the_id, nick, e_mail, password, registered, photo)

    if not user:
        response = {'message': 'User not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_user(tx, the_id):
    locate_user = "MATCH (user:User) WHERE ID(user) = $the_id RETURN user"
    locate_user_result = tx.run(locate_user, the_id=the_id).data()

    if locate_user_result:
        remove_user = "MATCH (user:User) WHERE ID(user) = $the_id DETACH DELETE user"
        tx.run(remove_user, the_id=the_id)
        return {'id': the_id}


@api.route('/admin/users/<int:the_id>', methods=['DELETE'])
def delete_user_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/admin/users/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        user = session.write_transaction(delete_user, the_id)

    if not user:
        response = {'message': 'User not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /reviews--------------------------------------------------------------------------------------------------------------


def get_reviews(tx):
    locate_review = """
        MATCH (show:Show)-[:ABOUT]-(review:Review)-[:WROTE]-(user:User)
        OPTIONAL MATCH (review)-[like:LIKES]-(:User)
        WITH show.title AS title, ID(review) AS id, user.nick AS author, count(like) AS score
        RETURN title, id, author, score
    """
    locate_review_result = tx.run(locate_review).data()
    return locate_review_result


@api.route('/reviews', methods=['GET'])
def get_reviews_route():
    """
    http GET http://127.0.0.1:5000/reviews
    :return: {}
    """
    with driver.session() as session:
        reviews = session.read_transaction(get_reviews)

    response = {'reviews': reviews}
    return jsonify(response)


def sort_reviews_by_score(tx):
    locate_review = """
        MATCH (show:Show)-[:ABOUT]-(review:Review)-[:WROTE]-(user:User)
        OPTIONAL MATCH (review)-[like:LIKES]-(:User)
        WITH show.title AS title, ID(review) AS id, user.nick AS author, count(like) AS score
        RETURN title, id, author, score
        ORDER BY score DESC
    """
    locate_review_result = tx.run(locate_review).data()
    return locate_review_result


@api.route('/reviews/sort/by_score', methods=['GET'])
def sort_reviews_by_score_route():
    """
    http GET http://127.0.0.1:5000/reviews/sort/by_score
    :return: {}
    """
    with driver.session() as session:
        reviews = session.read_transaction(sort_reviews_by_score)

    response = {'reviews': reviews}
    return jsonify(response)


def reverse_sort_reviews_by_score(tx):
    locate_review = """
        MATCH (show:Show)-[:ABOUT]-(review:Review)-[:WROTE]-(user:User)
        OPTIONAL MATCH (review)-[like:LIKES]-(:User)
        WITH show.title AS title, ID(review) AS id, user.nick AS author, count(like) AS score
        RETURN title, id, author, score
        ORDER BY score
    """
    locate_review_result = tx.run(locate_review).data()
    return locate_review_result


@api.route('/reviews/sort/reverse/by_score', methods=['GET'])
def reverse_sort_reviews_by_score_route():
    """
    http GET http://127.0.0.1:5000/reviews/sort/reverse/by_score
    :return: {}
    """
    with driver.session() as session:
        reviews = session.read_transaction(reverse_sort_reviews_by_score)

    response = {'reviews': reviews}
    return jsonify(response)


def sort_reviews_by_comments(tx):
    locate_review = """
        MATCH (show:Show)-[:ABOUT]-(review:Review)-[:WROTE]-(user:User)
        OPTIONAL MATCH (review)-[like:LIKES]-(:User)
        OPTIONAL MATCH (review)-[comment:COMMENTS]-(:User)
        WITH show.title AS title,
            ID(review) AS id,
            user.nick AS author,
            count(like) AS score,
            count(comment) AS comments
        RETURN title, id, author, score                
        ORDER BY comments DESC
    """
    locate_review_result = tx.run(locate_review).data()
    return locate_review_result


@api.route('/reviews/sort/by_comments', methods=['GET'])
def sort_reviews_by_comments_route():
    """
    http GET http://127.0.0.1:5000/reviews/sort/by_comments
    :return: {}
    """
    with driver.session() as session:
        reviews = session.read_transaction(sort_reviews_by_comments)

    response = {'reviews': reviews}
    return jsonify(response)


def reverse_sort_reviews_by_comments(tx):
    locate_review = """
        MATCH (show:Show)-[:ABOUT]-(review:Review)-[:WROTE]-(user:User)
        OPTIONAL MATCH (review)-[like:LIKES]-(:User)
        OPTIONAL MATCH (review)-[comment:COMMENTS]-(:User)
        WITH show.title AS title,
            ID(review) AS id,
            user.nick AS author,
            count(like) AS score,
            count(comment) AS comments
        RETURN title, id, author, score                
        ORDER BY comments
    """
    locate_review_result = tx.run(locate_review).data()
    return locate_review_result


@api.route('/reviews/sort/reverse/by_comments', methods=['GET'])
def reverse_sort_reviews_by_comments_route():
    """
    http GET http://127.0.0.1:5000/reviews/sort/reverse/by_comments
    :return: {}
    """
    with driver.session() as session:
        reviews = session.read_transaction(reverse_sort_reviews_by_comments)

    response = {'reviews': reviews}
    return jsonify(response)


def sort_reviews_by_title(tx):
    locate_review = """
        MATCH (show:Show)-[:ABOUT]-(review:Review)-[:WROTE]-(user:User)
        OPTIONAL MATCH (review)-[like:LIKES]-(:User)
        WITH show.title AS title, ID(review) AS id, user.nick AS author, count(like) AS score
        RETURN title, id, author, score
        ORDER BY title
    """
    locate_review_result = tx.run(locate_review).data()
    return locate_review_result


@api.route('/reviews/sort/by_title', methods=['GET'])
def sort_reviews_by_title_route():
    """
    http GET http://127.0.0.1:5000/reviews/sort/by_title
    :return: {}
    """
    with driver.session() as session:
        reviews = session.read_transaction(sort_reviews_by_title)

    response = {'reviews': reviews}
    return jsonify(response)


def reverse_sort_reviews_by_title(tx):
    locate_review = """
        MATCH (show:Show)-[:ABOUT]-(review:Review)-[:WROTE]-(user:User)
        OPTIONAL MATCH (review)-[like:LIKES]-(:User)
        WITH show.title AS title, ID(review) AS id, user.nick AS author, count(like) AS score
        RETURN title, id, author, score
        ORDER BY title DESC
    """
    locate_review_result = tx.run(locate_review).data()
    return locate_review_result


@api.route('/reviews/sort/reverse/by_title', methods=['GET'])
def reverse_sort_reviews_by_title_route():
    """
    http GET http://127.0.0.1:5000/reviews/sort/reverse/by_title
    :return: {}
    """
    with driver.session() as session:
        reviews = session.read_transaction(reverse_sort_reviews_by_title)

    response = {'reviews': reviews}
    return jsonify(response)


def sort_reviews_by_author(tx):
    locate_review = """
        MATCH (show:Show)-[:ABOUT]-(review:Review)-[:WROTE]-(user:User)
        OPTIONAL MATCH (review)-[like:LIKES]-(:User)
        WITH show.title AS title, ID(review) AS id, user.nick AS author, count(like) AS score
        RETURN title, id, author, score
        ORDER BY author
    """
    locate_review_result = tx.run(locate_review).data()
    return locate_review_result


@api.route('/reviews/sort/by_author', methods=['GET'])
def sort_reviews_by_author_route():
    """
    http GET http://127.0.0.1:5000/reviews/sort/by_author
    :return: {}
    """
    with driver.session() as session:
        reviews = session.read_transaction(sort_reviews_by_author)

    response = {'reviews': reviews}
    return jsonify(response)


def reverse_sort_reviews_by_author(tx):
    locate_review = """
        MATCH (show:Show)-[:ABOUT]-(review:Review)-[:WROTE]-(user:User)
        OPTIONAL MATCH (review)-[like:LIKES]-(:User)
        WITH show.title AS title, ID(review) AS id, user.nick AS author, count(like) AS score
        RETURN title, id, author, score
        ORDER BY author DESC
    """
    locate_review_result = tx.run(locate_review).data()
    return locate_review_result


@api.route('/reviews/sort/reverse/by_author', methods=['GET'])
def reverse_sort_reviews_by_author_route():
    """
    http GET http://127.0.0.1:5000/reviews/sort/reverse/by_author
    :return: {}
    """
    with driver.session() as session:
        reviews = session.read_transaction(reverse_sort_reviews_by_author)

    response = {'reviews': reviews}
    return jsonify(response)



def get_review_info(tx, the_id):
    locate_review = """
        MATCH (show:Show)-[:ABOUT]-(review:Review)-[:WROTE]-(user:User)
        WHERE ID(review) = $the_id
        OPTIONAL MATCH (review)-[like:LIKES]-(:User)
        WITH show.title AS title,
            ID(show) AS show_id,
            review.body AS body,
            ID(review) AS id,
            user.nick AS author,
            ID(user) AS user_id,
            count(like) AS score
        RETURN title, show_id, body, id, author, user_id, score
    """
    locate_review_result = tx.run(locate_review, the_id=the_id).data()
    return locate_review_result


@api.route('/reviews/<int:the_id>', methods=['GET'])
def get_review_info_route(the_id):
    """
    http GET http://127.0.0.1:5000/reviews/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        review = session.read_transaction(get_review_info, the_id)

    response = {'review': review}
    return jsonify(response)


def add_review(tx, nick, title, body):
    locate_user = "MATCH (user:User {nick: $nick}) RETURN user"
    locate_user_result = tx.run(locate_user, nick=nick).data()

    locate_title = "MATCH (show:Show {title: $title}) RETURN show"
    locate_title_result = tx.run(locate_title, title=title).data()

    if locate_user_result and locate_title_result:
        create_review = """
            MATCH (user:User {nick: $nick})
            MATCH (show:Show {title: $title})
            CREATE (show)<-[:ABOUT]-(:Review {body: $body})<-[:WROTE]-(user)
        """
        tx.run(create_review, nick=nick, title=title, body=body)
        return {'nick': nick, 'title': title}


@api.route('/reviews', methods=['POST'])
def add_review_route():
    """
    http POST http://127.0.0.1:5000/reviews user="user" title="title" body="body"
    :return: {}
    """
    nick = request.json['user']
    title = request.json['title']
    body = request.json['body']

    with driver.session() as session:
        review = session.write_transaction(add_review, nick, title, body)

    if not review:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def put_review_body(tx, the_id, body):
    locate_review = "MATCH (review:Review) WHERE ID(review) = $the_id RETURN review"
    locate_review_result = tx.run(locate_review, the_id=the_id).data()

    if locate_review_result:
        update_review = """
            MATCH (review:Review)
            WHERE ID(review) = $the_id
            SET review.body = $body
        """
        tx.run(update_review, the_id=the_id, body=body)
        return {'id': the_id, 'body': body}


@api.route('/reviews/<int:the_id>', methods=['PUT'])
def put_review_body_route(the_id):
    """
    http PUT http://127.0.0.1:5000/reviews/<int:the_id> body="body"
    :param the_id: int
    :return: {}
    """
    body = request.json['body']

    with driver.session() as session:
        review = session.write_transaction(put_review_body, the_id, body)

    if not review:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_review(tx, the_id):
    locate_review = "MATCH (review:Review) WHERE ID(review) = $the_id RETURN review"
    locate_review_result = tx.run(locate_review, the_id=the_id).data()

    if locate_review_result:
        remove_review = "MATCH (review:Review) WHERE ID(review) = $the_id DETACH DELETE review"
        tx.run(remove_review, the_id=the_id)
        return {'id': the_id}


@api.route('/reviews/<int:the_id>', methods=['DELETE'])
def delete_review_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/reviews/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        review = session.write_transaction(delete_review, the_id)

    if not review:
        response = {'message': 'Review not found in database!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /connection/show/seen-------------------------------------------------------------------------------------------------


def get_connections_seen(tx):
    locate_connection = """
        MATCH (user:User)-[conn:SEEN]-(show:Show)
        WITH user.nick AS user, ID(conn) AS id, show.title AS title
        RETURN user, id, title
    """
    locate_connection_result = tx.run(locate_connection).data()
    return locate_connection_result


@api.route('/connection/show/seen', methods=['GET'])
def get_connections_seen_route():
    """
    http GET http://127.0.0.1:5000/connection/show/seen
    :return: {}
    """
    with driver.session() as session:
        connections = session.read_transaction(get_connections_seen)

    response = {'connections': connections}
    return response


def add_connection_seen(tx, nick, title):
    locate_user = "MATCH (user:User {nick: $nick}) RETURN user"
    locate_user_result = tx.run(locate_user, nick=nick).data()

    locate_title = "MATCH (show:Show {title: $title}) RETURN show"
    locate_title_result = tx.run(locate_title, title=title).data()

    if locate_user_result and locate_title_result:
        create_connection = """
            MATCH (user:User {nick: $nick})
            MATCH (show:Show {title: $title})
            CREATE (user)-[:SEEN]->(show)
        """
        tx.run(create_connection, nick=nick, title=title)
        return {'user': nick, 'title': title}


@api.route('/connection/show/seen', methods=['POST'])
def add_connection_seen_route():
    """
    http POST http://127.0.0.1:5000/connection/show/seen user="user" title="title"
    :return: {}
    """
    nick = request.json['user']
    title = request.json['title']

    with driver.session() as session:
        connection = session.write_transaction(add_connection_seen, nick, title)

    if not connection:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_connection_seen(tx, the_id):
    locate_connection = "MATCH (:User)-[conn:SEEN]-(:Show) WHERE ID(conn) = $the_id RETURN conn"
    locate_connection_result = tx.run(locate_connection, the_id=the_id).data()

    if locate_connection_result:
        delete_connection = "MATCH (:User)-[conn:SEEN]-(:Show) WHERE ID(conn) = $the_id DELETE conn"
        tx.run(delete_connection, the_id=the_id)
        return {'id': the_id}


@api.route('/connection/show/seen/<int:the_id>', methods=['DELETE'])
def delete_connection_seen_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/connection/show/seen/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        connection = session.write_transaction(delete_connection_seen, the_id)

    if not connection:
        response = {'message': 'Connection not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /connections/show/likes-----------------------------------------------------------------------------------------------


def get_connections_likes(tx):
    locate_connection = """
        MATCH (user:User)-[conn:LIKES]-(show:Show)
        WITH user.nick AS user, ID(conn) AS id, show.title AS title
        RETURN user, id, title
    """
    locate_connection_result = tx.run(locate_connection).data()
    return locate_connection_result


@api.route('/connection/show/likes', methods=['GET'])
def get_connections_likes_route():
    """
    http GET http://127.0.0.1:5000/connection/show/likes
    :return: {}
    """
    with driver.session() as session:
        connections = session.read_transaction(get_connections_likes)

    response = {'connections': connections}
    return jsonify(response)


def add_connection_likes(tx, nick, title):
    locate_user = "MATCH (user:User {nick: $nick}) RETURN user"
    locate_user_result = tx.run(locate_user, nick=nick).data()

    locate_title = "MATCH (show:Show {title: $title}) RETURN show"
    locate_title_result = tx.run(locate_title, title=title).data()

    if locate_user_result and locate_title_result:
        create_connection = """
            MATCH (user:User {nick: $nick})
            MATCH (show:Show {title: $title})
            CREATE (user)-[:LIKES]->(show)
        """
        tx.run(create_connection, nick=nick, title=title)
        return {'user': nick, 'title': title}


@api.route('/connection/show/likes', methods=['POST'])
def add_connection_likes_route():
    """
    http POST http://127.0.0.1:5000/connection/show/likes user="user" title="title"
    :return: {}
    """
    nick = request.json['user']
    title = request.json['title']

    with driver.session() as session:
        connection = session.write_transaction(add_connection_likes, nick, title)

    if not connection:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_connection_likes(tx, the_id):
    locate_connection = "MATCH (:User)-[conn:LIKES]-(:Show) WHERE ID(conn) = $the_id RETURN conn"
    locate_connection_result = tx.run(locate_connection, the_id=the_id).data()

    if locate_connection_result:
        delete_connection = "MATCH (:User)-[conn:LIKES]-(:Show) WHERE ID(conn) = $the_id DELETE conn"
        tx.run(delete_connection, the_id=the_id)
        return {'id': the_id}


@api.route('/connection/show/likes/<int:the_id>', methods=['DELETE'])
def delete_connection_likes_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/connection/show/likes/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        connection = session.write_transaction(delete_connection_likes, the_id)

    if not connection:
        response = {'message': 'Connection not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /connection/show/wants_to_watch---------------------------------------------------------------------------------------


def get_connections_wants_to_watch(tx):
    locate_connection = """
        MATCH (user:User)-[conn:WANTS_TO_WATCH]-(show:Show)
        WITH user.nick AS user, ID(conn) AS id, show.title AS title
        RETURN user, id, title
    """
    locate_connection_result = tx.run(locate_connection).data()
    return locate_connection_result


@api.route('/connection/show/wants_to_watch', methods=['GET'])
def get_connections_wants_to_watch_route():
    """
    http GET http://127.0.0.1:5000/connection/show/wants_to_watch
    :return: {}
    """
    with driver.session() as session:
        connections = session.read_transaction(get_connections_wants_to_watch)

    response = {'connections': connections}
    return jsonify(response)


def add_connection_wants_to_watch(tx, nick, title):
    locate_user = "MATCH (user:User {nick: $nick}) RETURN user"
    locate_user_result = tx.run(locate_user, nick=nick).data()

    locate_title = "MATCH (show:Show {title: $title}) RETURN show"
    locate_title_result = tx.run(locate_title, title=title).data()

    if locate_user_result and locate_title_result:
        create_connection = """
            MATCH (user:User {nick: $nick})
            MATCH (show:Show {title: $title})
            CREATE (user)-[:WANTS_TO_WATCH]->(show)
        """
        tx.run(create_connection, nick=nick, title=title)
        return {'user': nick, 'title': title}


@api.route('/connection/show/wants_to_watch', methods=['POST'])
def add_connection_wants_to_watch_route():
    """
    http POST http://127.0.0.1:5000/connection/show/wants_to_watch user="user" title="title"
    :return: {}
    """
    nick = request.json['user']
    title = request.json['title']

    with driver.session() as session:
        connection = session.write_transaction(add_connection_wants_to_watch, nick, title)

    if not connection:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_connection_wants_to_watch(tx, the_id):
    locate_connection = "MATCH (:User)-[conn:WANTS_TO_WATCH]-(:Show) WHERE ID(conn) = $the_id RETURN conn"
    locate_connection_result = tx.run(locate_connection, the_id=the_id).data()

    if locate_connection_result:
        delete_connection = "MATCH (:User)-[conn:WANTS_TO_WATCH]-(:Show) WHERE ID(conn) = $the_id DELETE conn"
        tx.run(delete_connection, the_id=the_id)
        return {'id': the_id}


@api.route('/connection/show/wants_to_watch/<int:the_id>', methods=['DELETE'])
def delete_connection_wants_to_watch_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/connection/show/wants_to_watch/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        connection = session.write_transaction(delete_connection_wants_to_watch, the_id)

    if not connection:
        response = {'message': 'Connection not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /admin/connection/show/played-----------------------------------------------------------------------------------------


def get_connections_played(tx):
    locate_connection = """
        MATCH (person:Person)-[conn:PLAYED]-(show:Show)
        WITH person.name AS name, person.surname AS surname, conn.role AS role, ID(conn) AS id, show.title AS title
        RETURN name, surname, role, id, title
    """
    locate_connection_result = tx.run(locate_connection).data()
    return locate_connection_result


@api.route('/admin/connection/show/played', methods=['GET'])
def get_connections_played_route():
    """
    http GET http://127.0.0.1:5000/admin/connection/show/played
    :return: {}
    """
    with driver.session() as session:
        connections = session.read_transaction(get_connections_played)

    response = {'connections': connections}
    return jsonify(response)


def add_connection_played(tx, person_id, role, title):
    locate_person = "MATCH (person:Person) WHERE ID(person) = $person_id RETURN person"
    locate_person_result = tx.run(locate_person, person_id=person_id).data()

    locate_title = "MATCH (show:Show {title: $title}) RETURN show"
    locate_title_result = tx.run(locate_title, title=title).data()

    if locate_person_result and locate_title_result:
        create_connection = """
            MATCH (person:Person) WHERE ID(person) = $person_id
            MATCH (show:Show {title: $title})
            CREATE (person)-[:PLAYED {role: $role}]->(show)
        """
        tx.run(create_connection, person_id=person_id, role=role, title=title)
        return {'person': person_id, 'role': role, 'show': title}


@api.route('/admin/connection/show/played', methods=['POST'])
def add_connection_route():
    """
    http POST http://127.0.0.1:5000/admin/connection/show/played person_id=11 role="role" title="title"
    :return: {}
    """
    person_id = int(request.json['person_id'])
    role = request.json['role']
    show_title = request.json['title']

    with driver.session() as session:
        connection = session.write_transaction(add_connection_played, person_id, role, show_title)

    if not connection:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def put_connection_played_role(tx, the_id, role):
    locate_connection = "MATCH (:Person)-[conn:PLAYED]-(:Show) WHERE ID(conn) = $the_id RETURN conn"
    locate_connection_result = tx.run(locate_connection, the_id=the_id).data()

    if locate_connection_result:
        update_connection_body = """
            MATCH (:Person)-[conn:PLAYED]-(:Show)
            WHERE ID(conn) = $the_id
            SET conn.role = $role
        """
        tx.run(update_connection_body, the_id=the_id, role=role)
        return {'id': the_id, 'role': role}


@api.route('/admin/connection/show/played/<int:the_id>', methods=['PUT'])
def put_connection_played_role_route(the_id):
    """
    http PUT http://127.0.0.1:5000/admin/connection/show/played/<int:the_id> role="role"
    :param the_id: int
    :return: {}
    """
    role = request.json['role']

    with driver.session() as session:
        connection = session.write_transaction(put_connection_played_role, the_id, role)

    if not connection:
        response = {'message': 'Connection not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_connection_played(tx, the_id):
    locate_connection = "MATCH (:Show)-[conn:PLAYED]-(:Person) WHERE ID(conn) = $the_id RETURN conn"
    locate_connection_result = tx.run(locate_connection, the_id=the_id).data()

    if locate_connection_result:
        delete_connection = "MATCH (:Show)-[conn:PLAYED]-(:Person) WHERE ID(conn) = $the_id DELETE conn"
        tx.run(delete_connection, the_id=the_id)
        return {'id': the_id}


@api.route('/admin/connection/show/played/<int:the_id>', methods=['DELETE'])
def delete_connection_played_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/admin/connection/show/played/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        connection = session.write_transaction(delete_connection_played, the_id)

    if not connection:
        response = {'message': 'Connection not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /admin/connection/show/directed---------------------------------------------------------------------------------------


def get_connections_directed(tx):
    locate_connection = """
        MATCH (person:Person)-[conn:DIRECTED]-(show:Show)
        WITH person.name AS name, person.surname AS surname, ID(conn) AS id, show.title AS title
        RETURN name, surname, id, title
    """
    locate_connection_result = tx.run(locate_connection).data()
    return locate_connection_result


@api.route('/admin/connection/show/directed', methods=['GET'])
def get_connections_directed_route():
    """
    http GET http://127.0.0.1:5000/admin/connection/show/directed
    :return: {}
    """
    with driver.session() as session:
        connections = session.read_transaction(get_connections_directed)

    response = {'connections': connections}
    return jsonify(response)


def add_connection_directed(tx, person_id, title):
    locate_connection = """
        MATCH (person:Person)-[conn:DIRECTED]-(:Show {title: $title})
        WHERE ID(person) = $person_id
        RETURN conn
    """
    locate_connection_result = tx.run(locate_connection, title=title, person_id=person_id).data()

    if not locate_connection_result:
        create_connection = """
            MATCH (person:Person)
            WHERE ID(person) = $person_id
            MATCH (show:Show {title: $title})
            CREATE (person)-[:DIRECTED]->(show)
        """
        tx.run(create_connection, person_id=person_id, title=title)
        return {'person': person_id, 'show': title}


@api.route('/admin/connection/show/directed', methods=['POST'])
def add_connection_directed_route():
    """
    http POST http://127.0.0.1:5000/admin/connection/show/directed person_id=11 title="title"
    :return: {}
    """
    person_id = int(request.json['person_id'])
    title = request.json['title']

    with driver.session() as session:
        connection = session.write_transaction(add_connection_directed, person_id, title)

    if not connection:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_connection_directed(tx, the_id):
    locate_connection = "MATCH ()-[conn:DIRECTED]-() WHERE ID(conn) = $the_id RETURN conn"
    locate_connection_result = tx.run(locate_connection, the_id=the_id).data()

    if locate_connection_result:
        delete_connection = "MATCH ()-[conn:DIRECTED]-() WHERE ID(conn) = $the_id DELETE conn"
        tx.run(delete_connection, the_id=the_id)
        return {'id': the_id}


@api.route('/admin/connection/show/directed/<int:the_id>', methods=['DELETE'])
def delete_connection_directed_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/admin/connection/show/directed/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        connection = session.write_transaction(delete_connection_directed, the_id)

    if not connection:
        response = {'message': 'Connection not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /connection/review/likes----------------------------------------------------------------------------------------------


def get_connection_likes_review(tx):
    locate_connection = """
        MATCH (user:User)-[conn:LIKES]-(review:Review)-[:ABOUT]-(show:Show)
        WITH user.nick AS author, ID(conn) AS id, ID(review) AS review_id, show.title AS title
        RETURN author, id, review_id, title
    """
    locate_connection_result = tx.run(locate_connection).data()
    return locate_connection_result


@api.route('/connection/review/likes', methods=['GET'])
def get_connection_likes_review_route():
    """
    http GET http://127.0.0.1:5000/connection/review/likes
    :return: {}
    """
    with driver.session() as session:
        connections = session.read_transaction(get_connection_likes_review)

    response = {'connections': connections}
    return jsonify(response)


def add_connection_likes_review(tx, nick, review_id):
    locate_user = "MATCH (user:User {nick: $nick}) RETURN user"
    locate_user_result = tx.run(locate_user, nick=nick).data()

    locate_review = "MATCH (review:Review) WHERE ID(review) = $review_id RETURN review"
    locate_review_result = tx.run(locate_review, review_id=review_id).data()

    locate_connection = """
        MATCH (:User {nick: $nick})-[conn:LIKES]-(review:Review) WHERE ID(review) = $review_id RETURN conn
    """
    locate_connection_result = tx.run(locate_connection, nick=nick, review_id=review_id).data()

    if locate_user_result and locate_review_result and not locate_connection_result:
        create_connection = """
            MATCH (user:User {nick: $nick})
            MATCH (review:Review) WHERE ID(review) = $review_id
            CREATE (user)-[:LIKES]->(review)
        """
        tx.run(create_connection, nick=nick, review_id=review_id)
        return {'user': nick, 'review': review_id}


@api.route('/connection/review/likes', methods=['POST'])
def add_connection_likes_review_route():
    """
    http POST http://127.0.0.1:5000/connection/review/likes user="user" review_id=11
    :return: {}
    """
    nick = request.json['user']
    review_id = int(request.json['review_id'])

    with driver.session() as session:
        connection = session.write_transaction(add_connection_likes_review, nick, review_id)

    if not connection:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_connection_likes_review(tx, the_id):
    locate_connection = "MATCH (:User)-[conn:LIKES]-(:Review) WHERE ID(conn) = $the_id RETURN conn"
    locate_connection_result = tx.run(locate_connection, the_id=the_id).data()

    if locate_connection_result:
        remove_connection = "MATCH (:User)-[conn:LIKES]-(:Review) WHERE ID(conn) = $the_id DELETE conn"
        tx.run(remove_connection, the_id=the_id)
        return {'id': the_id}


@api.route('/connection/review/likes/<int:the_id>', methods=['DELETE'])
def delete_connection_likes_review_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/connection/review/likes/<int:the_id>
    :param the_id: int
    :return: {}
    """
    with driver.session() as session:
        connection = session.write_transaction(delete_connection_likes_review, the_id)

    if not connection:
        response = {'message': 'Connection not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /connection/review/comments-------------------------------------------------------------------------------------------


def get_review_comments(tx):
    locate_connection = """
        MATCH (user:User)-[comment:COMMENTS]-(review:Review)-[:ABOUT]-(show:Show)
        MATCH (author:User)-[:WROTE]-(review)
        WITH user.nick AS comment_author,
            comment.comment AS comment,
            ID(comment) AS id,
            show.title AS title,
            author.nick AS review_author
        RETURN comment_author, comment, id, title, review_author
    """
    locate_connection_result = tx.run(locate_connection).data()
    return locate_connection_result


@api.route('/connection/review/comments', methods=['GET'])
def get_review_comments_route():
    """
    http GET http://127.0.0.1:5000/connection/review/comments
    :return: {}
    """
    with driver.session() as session:
        connections = session.read_transaction(get_review_comments)

    response = {'connections': connections}
    return jsonify(response)


def add_review_comment(tx, nick, comment, review_id):
    locate_user = "MATCH (user:User {nick: $nick}) RETURN user"
    locate_user_result = tx.run(locate_user, nick=nick).data()

    locate_review = "MATCH (review:Review) WHERE ID(review) = $review_id RETURN review"
    locate_review_result = tx.run(locate_review, review_id=review_id).data()

    if locate_user_result and locate_review_result:
        create_connection = """
            MATCH (user:User {nick: $nick})
            MATCH (review:Review) WHERE ID(review) = $review_id
            CREATE (user)-[:COMMENTS {comment: $comment}]->(review)
        """
        tx.run(create_connection, nick=nick, review_id=review_id, comment=comment)
        return {'user': nick, 'comment': comment, 'review_id': review_id}


@api.route('/connection/review/comments', methods=['POST'])
def add_review_comment_route():
    """
    http POST http://127.0.0.1:5000/connection/review/comments user="user" comment="comment" review_id=10
    :return: {}
    """
    nick = request.json['user']
    comment = request.json['comment']
    review_id = int(request.json['review_id'])

    with driver.session() as session:
        connection = session.write_transaction(add_review_comment, nick, comment, review_id)

    if not connection:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def put_review_comment(tx, the_id, comment):
    locate_connection = "MATCH (:User)-[conn:COMMENTS]-(:Review) WHERE ID(conn) = $the_id RETURN conn"
    locate_connection_result = tx.run(locate_connection, the_id=the_id).data()

    if locate_connection_result:
        update_connection = """
            MATCH (:User)-[conn:COMMENTS]-(:Review)
            WHERE ID(conn) = $the_id
            SET conn.comment = $comment
        """
        tx.run(update_connection, the_id=the_id, comment=comment)
        return {'id': the_id, 'comment': comment}


@api.route('/connection/review/comments/<int:the_id>', methods=['PUT'])
def put_review_comment_route(the_id):
    """
    http PUT http://127.0.0.1:5000/connection/review/comments/<int:the_id> comment="comment"
    :param the_id: int
    :return: {}
    """
    comment = request.json['comment']

    with driver.session() as session:
        connection = session.write_transaction(put_review_comment, the_id, comment)

    if not connection:
        response = {'message': 'Connection not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_review_comment(tx, the_id):
    locate_connection = "MATCH (:User)-[comment:COMMENTS]-(:Review) WHERE ID(comment) = $the_id RETURN comment"
    locate_connection_result = tx.run(locate_connection, the_id=the_id).data()

    if locate_connection_result:
        delete_connection = "MATCH (:User)-[comment:COMMENTS]-(:Review) WHERE ID(comment) = $the_id DELETE comment"
        tx.run(delete_connection, the_id=the_id)
        return {'id': the_id}


@api.route('/connection/review/comments/<int:the_id>', methods=['DELETE'])
def delete_review_comment_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/connection/review/comments/<int:the_id>
    :param the_id:
    :return:
    """
    with driver.session() as session:
        connection = session.write_transaction(delete_review_comment, the_id)

    if not connection:
        response = {'message': 'Connection not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


# /admin/database/get/csv-----------------------------------------------------------------------------------------------


def get_database_csv(tx):
    get_database = "CALL apoc.export.csv.all(null, {stream:true}) YIELD data RETURN data"
    get_database_result = tx.run(get_database).data()
    return get_database_result[0]['data']


@api.route('/admin/database/get/csv', methods=['GET'])
def get_database_csv_route():
    """
    http GET http://127.0.0.1:5000/admin/database/get/csv
    :return: file
    """
    with driver.session() as session:
        string = session.read_transaction(get_database_csv)

    file = StringIO(string, '\n')
    return Response(file, mimetype='text/plain')


# /admin/database/get/json----------------------------------------------------------------------------------------------


def get_database_json(tx):
    get_database = "CALL apoc.export.json.all(null, {stream:true}) YIELD data RETURN data"
    get_database_result = tx.run(get_database).data()
    return get_database_result[0]['data']


@api.route('/admin/database/get/json', methods=['GET'])
def get_database_json_route():
    """
    http GET http://127.0.0.1:5000/admin/database/get/json
    :return: file
    """
    with driver.session() as session:
        string = session.read_transaction(get_database_json)

    file = StringIO(string, '\n')
    return Response(file, mimetype='text/plain')


if __name__ == '__main__':
    api.run()
