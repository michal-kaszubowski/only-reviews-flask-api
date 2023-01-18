import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from neo4j import GraphDatabase

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
    locate_genre = "MATCH (genre:Genre) RETURN genre"
    locate_genre_result = tx.run(locate_genre).data()

    genres = [result['genre']['name'] for result in locate_genre_result]
    return genres


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


def delete_genre(tx, name):
    locate_genre = "MATCH (genre:Genre {name: $name}) RETURN genre"
    locate_genre_result = tx.run(locate_genre, name=name).data()

    if locate_genre_result:
        remove_genre = "MATCH (genre:Genre {name: $name}) DETACH DELETE genre"
        tx.run(remove_genre, name=name)
        return {'name': name}


@api.route('/admin/genres/<string:name>', methods=['DELETE'])
def delete_genre_route(name):
    """
    http DELETE http://127.0.0.1:5000/admin/genres/<string:name>
    :param name: string
    :return: {}
    """
    with driver.session() as session:
        genre = session.write_transaction(delete_genre, name)

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
        WITH person, ID(person) AS id
        RETURN person, id
    """
    locate_person_result = tx.run(locate_person).data()

    persons = [{
        'name': result['person']['name'],
        'surname': result['person']['surname'],
        'born': result['person']['born'],
        'photo': result['person']['photo'],
        'id': result['id']
    } for result in locate_person_result]
    return persons


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


def get_person_info(tx, the_id):
    locate_person = """
        MATCH (person:Person)
        WHERE ID(person) = $the_id
        OPTIONAL MATCH (person)-[played:PLAYED]-(in:Show)
        OPTIONAL MATCH (person)-[:DIRECTED]-(what:Show)
        WITH person, collect(played) AS roles, collect(in) AS filmography, collect(what) AS directed
        RETURN person, roles, filmography, directed
    """
    locate_person_result = tx.run(locate_person, the_id=the_id).data()

    if locate_person_result:
        person = {
            'name': locate_person_result[0]['person']['name'],
            'surname': locate_person_result[0]['person']['surname'],
            'born': locate_person_result[0]['person']['born'],
            'photo': locate_person_result[0]['person']['photo'],
            'roles': locate_person_result[0]['roles'],
            'filmography': locate_person_result[0]['filmography'],
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
    http POST http://127.0.0.1:5000/admin/persons name="name" surname="surname" born=0000 photo="photoURL"
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
            SET person.name = $name, person.surname = $surname, person.born = $born, person.phot = $photo
        """
        tx.run(update_person, the_id=the_id, name=name, surname=surname, born=born, photo=photo).data()
        return {'name': name, 'surname': surname, 'born': born, 'photo': photo}


@api.route('/admin/persons/<int:the_id>', methods=['PUT'])
def put_person_info_route(the_id):
    """
    http PUT http://127.0.0.1:5000/admin/persons/<int:the_id> name="name" surname="surname" born=0000 photo="photoURL"
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
    locate_title = "MATCH (show:Show)-[:BELONGS]-(genre:Genre) RETURN show, genre"
    locate_title_result = tx.run(locate_title).data()

    shows = [{
        'title': result['show']['title'],
        'genre': result['genre']['name'],
        'photo': result['show']['photo'],
        'episodes': result['show']['episodes'],
        'released': result['show']['released'],
        'ended': result['show']['ended']
    } for result in locate_title_result]
    return shows


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


def get_show_info(tx, title):
    locate_title = """
        MATCH (show:Show {title: $title})-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[:DIRECTED]-(director:Person)
        OPTIONAL MATCH (show)-[:PLAYED]-(actor:Person)
        OPTIONAL MATCH (show)-[:LIKES]-(user:User)
        OPTIONAL MATCH (show)-[:ABOUT]-(review:Review)
        WITH show,
            genre,
            ID(show) AS id,
            director.name AS name,
            director.surname AS surname,
            collect(actor) AS cast,
            count(user) AS likes,
            collect(review) AS reviews
        RETURN show, genre, id, name, surname, cast, likes, reviews
    """
    locate_title_result = tx.run(locate_title, title=title).data()

    if locate_title_result:
        show = {
            'id': locate_title_result[0]['id'],
            'title': locate_title_result[0]['show']['title'],
            'genre': locate_title_result[0]['genre']['name'],
            'photo': locate_title_result[0]['show']['photo'],
            'episodes': locate_title_result[0]['show']['episodes'],
            'released': locate_title_result[0]['show']['released'],
            'ended': locate_title_result[0]['show']['ended'],
            'director': {
                'name': locate_title_result[0]['name'],
                'surname': locate_title_result[0]['surname']
            },
            'cast': [{'name': actor['name'], 'surname': actor['surname']} for actor in locate_title_result[0]['cast']],
            'likes': locate_title_result[0]['likes'],
            'reviews': locate_title_result[0]['reviews']
        }
        return show


@api.route('/shows/<string:title>', methods=['GET'])
def get_show_info_route(title):
    """
    http GET http://127.0.0.1:5000/shows/<string:title>
    :param title: string
    :return: {}
    """
    with driver.session() as session:
        show = session.read_transaction(get_show_info, title)

    if not show:
        response = {'message': 'Show not found!'}
        return jsonify(response)
    else:
        response = {'show': show}
        return jsonify(response)


# /admin/shows----------------------------------------------------------------------------------------------------------


def add_show(tx, title, genre, photo, episodes, released, ended):
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
                episodes: $episodes,
                released: $released,
                ended:$ended
            })-[:BELONGS]->(genre)
        """
        tx.run(create_show, title=title, genre=genre, photo=photo, episodes=episodes, released=released, ended=ended)
        return {
            'title': title,
            'genre': genre,
            'photo': photo,
            'episodes': episodes,
            'released': released,
            'ended': ended
        }


@api.route('/admin/shows', methods=['POST'])
def add_show_route():
    """
    http POST http://127.0.0.1:5000/admin/shows title="title" genre="genre" photo="photoURL" episodes=00
    released="01/12/2000" ended="01/12/2001"
    :return: {}
    """
    title = request.json['title']
    genre = request.json['genre']
    photo = request.json['photo']
    episodes = request.json['episodes']
    released = request.json['released']
    ended = request.json['ended']

    with driver.session() as session:
        show = session.write_transaction(add_show, title, genre, photo, episodes, released, ended)

    if not show:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def put_show_info(tx, the_id, title, genre, photo, episodes, released, ended):
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
            episodes=episodes,
            released=released,
            ended=ended
        )
        return {'the_id': the_id}


@api.route('/admin/shows/<int:the_id>', methods=['PUT'])
def put_show_info_route(the_id):
    """
    http PUT http://127.0.0.1:5000/admin/shows/<int:the_id> title="title" genre="genre" photo="photoURL" episodes=00
    released="01/12/2000" ended="01/12/2001"
    :param the_id: int
    :return: {}
    """
    title = request.json['title']
    genre = request.json['genre']
    photo = request.json['photo']
    episodes = request.json['episodes']
    released = request.json['released']
    ended = request.json['ended']

    with driver.session() as session:
        show = session.write_transaction(put_show_info, the_id, title, genre, photo, episodes, released, ended)

    if not show:
        response = {'message': 'Invalid arguments!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_show(tx, title):
    locate_title = "MATCH (show:Show {title: $title}) RETURN show"
    locate_title_result = tx.run(locate_title, title=title).data()

    if locate_title_result:
        remove_show = "MATCH (show:Show {title: $title}) DETACH DELETE show"
        tx.run(remove_show, title=title)
        return {'title': title}


@api.route('/admin/shows/<string:title>', methods=['DELETE'])
def delete_show_route(title):
    with driver.session() as session:
        show = session.write_transaction(delete_show, title)

    if not show:
        response = {'message': 'Show not found!'}
        return jsonify(response)
    else:
        response = {'status': 'success'}
        return jsonify(response)


if __name__ == '__main__':
    api.run()
