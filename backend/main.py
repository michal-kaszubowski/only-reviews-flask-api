import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect, render_template
from neo4j import GraphDatabase

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

URI = os.environ.get("URI")
USERNAME = os.environ.get("UNAME")
PASSWORD = os.environ.get("PASSWORD")

driver = GraphDatabase.driver(uri=URI, auth=(USERNAME, PASSWORD))
api = Flask(__name__)
driver.verify_connectivity()


def get_movies(tx):
    query = "MATCH (movie:Movie)-[:BELONGS_TO]-(genre:Genre) RETURN movie, genre"
    results = tx.run(query).data()
    movies = [
        {
            'title': result['movie']['title'],
            'released': result['movie']['released'],
            'photo': result['movie']['photo'],
            'genre': result['genre']['name']
        } for result in results
    ]
    return movies


@api.route('/movies', methods=['GET'])
def get_movies_route():
    with driver.session() as session:
        movies = session.read_transaction(get_movies)

    response = {'movies': movies}
    return jsonify(response)


def get_movie(tx, title):
    query = "MATCH (movie:Movie {title: $title})-[:BELONGS_TO]-(genre:Genre) RETURN movie, genre"
    result = tx.run(query, title=title).data()

    if not result:
        return None
    else:
        return {
            'title': result[0]['movie']['title'],
            'released': result[0]['movie']['released'],
            'photo': result[0]['movie']['photo'],
            'genre': result[0]['genre']['name']
        }


@api.route('/movies/<string:title>', methods=['GET'])
def get_movie_route(title):
    with driver.session() as session:
        movie = session.read_transaction(get_movie, title)

    if not movie:
        response = {'message': 'Movie not found'}
        return jsonify(response), 404
    else:
        response = {'movie': movie}
        return jsonify(response)


def add_movie(tx, title, year, photo, genre):
    query = "CREATE (:Movie {title: $title, released: $released, photo: $photo})"
    tx.run(query, title=title, released=year, photo=photo)

    for each in genre:
        query = "MATCH (m:Genre {name: $name}) RETURN m"
        result = tx.run(query, name=each).data()
        if not result:
            return None
        else:
            query = """
                MATCH (movie:Movie {title: $title}), (genre:Genre {name: $name})
                CREATE (movie)-[:BELONGS_TO]->(genre)
            """
            tx.run(query, title=title, name=each)

    return {'title': title, 'released': year, 'photo': photo, 'genre': genre}


@api.route('/movies', methods=['POST'])
def add_movie_route():
    title = request.json['title']
    year = request.json['released']
    photo = request.json['photo']
    genre = request.json['genre']

    with driver.session() as session:
        session.write_transaction(add_movie, title, year, photo, genre)

    response = {'status': 'success'}
    return jsonify(response)


def update_movie(tx, title, new_title, new_year, new_photo, new_genre):
    query_movie = "MATCH (m:Movie {title: $title}) RETURN m"
    result_movie = tx.run(query_movie, title=title).data()
    query_genre = "MATCH (m:Genre {name: $name}) RETURN m"
    result_genre = tx.run(query_genre, name=new_genre).data()

    if result_movie or result_genre:
        query = """
            MATCH (movie:Movie {title: $title})-[oldRel:BELONGS_TO]-(:Genre)
            DELETE oldRel
            SET movie.title=$new_title, movie.released=$new_year, movie.photo=$new_photo
            WITH movie
            MATCH (genre:Genre {name: $new_genre})
            CREATE (movie)-[:BELONGS_TO]->(genre)
        """
        tx.run(query, title=title, new_title=new_title, new_year=new_year, new_photo=new_photo, new_genre=new_genre)
        return {'title': new_title, 'year': new_year, 'photo': new_photo, 'genre': new_genre}
    else:
        return None


@api.route('/movies/<string:title>', methods=['PUT'])
def update_movie_route(title):
    new_title = request.json['title']
    new_year = request.json['released']
    new_photo = request.json['photo']
    new_genre = request.json['genre']

    with driver.session() as session:
        movie = session.write_transaction(update_movie, title, new_title, new_year, new_photo, new_genre)

    if not movie:
        response = {'message': 'Movie or Genre not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_movie(tx, title):
    query = "MATCH (m:Movie {title: $title}) RETURN m"
    result = tx.run(query, title=title).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Movie {title: $title}) DETACH DELETE m"
        tx.run(query, title=title)
        return {'title': title}


@api.route('/movies/<string:title>', methods=['DELETE'])
def delete_movie_route(title):
    with driver.session() as session:
        movie = session.write_transaction(delete_movie, title)

    if not movie:
        response = {'message': 'Movie not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


def get_genres(tx):
    query = "MATCH (m:Genre) RETURN m"
    results = tx.run(query).data()
    movies = [{'name': result['m']['name']} for result in results]
    return movies


@api.route('/genres', methods=['GET'])
def get_genres_route():
    with driver.session() as session:
        genres = session.read_transaction(get_genres)

    response = {'genres': genres}
    return jsonify(response)


def get_genre(tx, name):
    query = "MATCH (m:Genre {name: $name}) RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        return {'name': result[0]['m']['name']}


@api.route('/genres/<string:name>', methods=['GET'])
def get_genre_route(name):
    with driver.session() as session:
        genre = session.read_transaction(get_genre, name)

    if not genre:
        response = {'message': 'Genre not found'}
        return jsonify(response), 404
    else:
        response = {'genre': genre}
        return jsonify(response)


def add_genre(tx, name):
    query = "CREATE (:Genre {name: $name})"
    tx.run(query, name=name)


@api.route('/genres', methods=['POST'])
def add_genre_route():
    name = request.json['name']

    with driver.session() as session:
        session.write_transaction(add_genre, name)

    response = {'status': 'success'}
    return jsonify(response)


def update_genre(tx, name, new_name):
    query = "MATCH (m:Genre {name: $name}) RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Genre {name: $name}) SET m.name=$new_name"
        tx.run(query, name=name, new_name=new_name)
        return {'name': new_name}


@api.route('/genres/<string:name>', methods=['PUT'])
def update_genre_route(name):
    new_name = request.json['name']

    with driver.session() as session:
        genre = session.write_transaction(update_genre, name, new_name)

    if not genre:
        response = {'message': 'Genre not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_genre(tx, name):
    query = "MATCH (m:Genre {name: $name}) RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Genre {name: $name}) DETACH DELETE m"
        tx.run(query, name=name)
        return {'name': name}


@api.route('/genres/<string:name>', methods=['DELETE'])
def delete_genre_route(name):
    with driver.session() as session:
        movie = session.write_transaction(delete_genre, name)

    if not movie:
        response = {'message': 'Genre not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


if __name__ == '__main__':
    api.run()
