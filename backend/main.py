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
    locate_genre = """
        MATCH (genre:Genre)
        WITH *, ID(genre) AS id
        RETURN genre, id
    """
    locate_genre_result = tx.run(locate_genre).data()

    genres = [{
        'name': result['genre']['name'],
        'id': result['id']
    } for result in locate_genre_result]
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
    locate_title = """
        MATCH (show:Show)-[:BELONGS]-(genre:Genre)
        OPTIONAL MATCH (show)-[like:LIKES]-(:User)
        WITH *, ID(show) AS id, count(like) AS score
        RETURN show, genre, id, score
    """
    locate_title_result = tx.run(locate_title).data()

    shows = [{
        'title': result['show']['title'],
        'genre': result['genre']['name'],
        'photo': result['show']['photo'],
        'episodes': result['show']['episodes'],
        'released': result['show']['released'],
        'ended': result['show']['ended'],
        'id': result['id']
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
            director.name AS name,
            director.surname AS surname,
            collect(played.role) AS roles,
            collect(actor) AS cast,
            count(user) AS score,
            collect(review) AS reviews,
            collect(author) AS authors
        RETURN show, genre, id, name, surname, roles, cast, score, reviews, authors
    """
    locate_title_result = tx.run(locate_title, the_id=the_id).data()

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
            'cast': [{
                'name': locate_title_result[0]['cast'][i]['name'],
                'surname': locate_title_result[0]['cast'][i]['surname'],
                'as': locate_title_result[0]['roles'][i]
            } for i in range(0, len(locate_title_result[0]['cast']))],
            'score': locate_title_result[0]['score'],
            'reviews': [{
                'author': locate_title_result[0]['authors'][i]['nick'],
                'body': locate_title_result[0]['reviews'][i]['body']
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
    http DELETE http://127.0.0.1:5000/admin/shows/<string:title>
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


def get_user_info(tx, the_id):
    locate_user = """
        MATCH (user:User)
        WHERE ID(user) = $the_id
        OPTIONAL MATCH (user)-[:SEEN]-(seen:Show)
        OPTIONAL MATCH (user)-[:LIKES]-(liked:Show)
        OPTIONAL MATCH (user)-[:WANTS_TO_WATCH]-(to_watch:Show)
        OPTIONAL MATCH (user)-[:WROTE]-(review:Review)
        WITH user,
            ID(user) AS id,
            collect(seen.title) AS seen_shows,
            collect(liked.title) AS favourite,
            collect(to_watch.title) AS watchlist,
            collect(review) AS reviews
        RETURN user, id, seen_shows, favourite, watchlist, reviews
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
            'reviews': locate_user_result[0]['reviews']
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
    :return:
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


def add_review(tx, the_id, title, body):
    locate_user = "MATCH (user:User) WHERE ID(user) = $the_id RETURN user"
    locate_user_result = tx.run(locate_user, the_id=the_id).data()

    locate_title = "MATCH (show:Show {title: $title}) RETURN show"
    locate_title_result = tx.run(locate_title, title=title).data()

    if locate_user_result and locate_title_result:
        create_review = """
            MATCH (user:User) WHERE ID(user) = $the_id
            MATCH (show:Show {title: $title})
            CREATE (show)<-[:ABOUT]-(:Review {body: $body})<-[:WROTE]-(user)
        """
        tx.run(create_review, the_id=the_id, title=title, body=body)
        return {'user_id': the_id, 'title': title}


@api.route('/reviews/<int:the_id>', methods=['POST'])
def add_review_route(the_id):
    """
    http POST http://127.0.0.1:5000/reviews/<int:the_id> title="title" body="body"
    :param the_id: int
    :return: {}
    """
    title = request.json['title']
    body = request.json['body']

    with driver.session() as session:
        review = session.write_transaction(add_review, the_id, title, body)

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
        MATCH (user:User)-[:SEEN]-(show:Show)
        WITH user.nick AS nick, ID(user) AS id, show.title AS title
        RETURN nick, id, title
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
    http POST http://127.0.0.1:5000/connection/seen nick="nick" title="title"
    :return: {}
    """
    nick = request.json['nick']
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
        WITH user.nick AS nick, ID(conn) AS id, show.title AS title
        RETURN nick, id, title
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
    http POST http://127.0.0.1:5000/connection/show/likes nick="nick" title="title"
    :return: {}
    """
    nick = request.json['nick']
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
        WITH user.nick AS nick, ID(conn) AS id, show.title AS title
        RETURN nick, id, title
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
    http POST http://127.0.0.1:5000/connection/show/wants_to_watch nick="nick" title="title"
    :return: {}
    """
    nick = request.json['nick']
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


# /admin/connection/played----------------------------------------------------------------------------------------------


def get_connections_played(tx):
    locate_connection = """
        MATCH (person:Person)-[conn:PLAYED]-(show:Show)
        WITH person.name AS name, person.surname AS surname, conn.role AS role, ID(conn) AS id, show.title AS title
        RETURN name, surname, role, id, title
    """
    locate_connection_result = tx.run(locate_connection).data()
    return locate_connection_result


@api.route('/admin/connection/played', methods=['GET'])
def get_connections_played_route():
    """
    http GET http://127.0.0.1:5000/admin/connection/played
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


@api.route('/admin/connection/played', methods=['POST'])
def add_connection_route():
    """
    http POST http://127.0.0.1:5000/admin/connection/played/ person_id=00 role="role" title="title"
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


def delete_connection_played(tx, the_id):
    locate_connection = "MATCH (:Show)-[conn:PLAYED]-(:Person) WHERE ID(conn) = $the_id RETURN conn"
    locate_connection_result = tx.run(locate_connection, the_id=the_id).data()

    if locate_connection_result:
        delete_connection = "MATCH (:Show)-[conn:PLAYED]-(:Person) WHERE ID(conn) = $the_id DELETE conn"
        tx.run(delete_connection, the_id=the_id)
        return {'id': the_id}


@api.route('/admin/connection/played/<int:the_id>', methods=['DELETE'])
def delete_connection_played_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/admin/connection/played/<int:the_id>
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


# /admin/connection/directed--------------------------------------------------------------------------------------------


def get_connections_directed(tx):
    locate_connection = """
        MATCH (person:Person)-[conn:DIRECTED]-(show:Show)
        WITH person.name AS name, person.surname AS surname, ID(conn) AS id, show.title AS title
        RETURN name, surname, id, title
    """
    locate_connection_result = tx.run(locate_connection).data()
    return locate_connection_result


@api.route('/admin/connection/directed', methods=['GET'])
def get_connections_directed_route():
    """
    http GET http://127.0.0.1:5000/admin/connection/directed
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


@api.route('/admin/connection/directed', methods=['POST'])
def add_connection_directed_route():
    """
    http POST http://127.0.0.1:5000/admin/connection/directed person_id=00 title="title"
    :return: {}
    """
    person_id = int(request.json['person_id'])
    show_title = request.json['title']

    with driver.session() as session:
        connection = session.write_transaction(add_connection_directed, person_id, show_title)

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


@api.route('/admin/connection/directed/<int:the_id>', methods=['DELETE'])
def delete_connection_directed_route(the_id):
    """
    http DELETE http://127.0.0.1:5000/admin/connection/directed/<int:the_id>
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


if __name__ == '__main__':
    api.run()
