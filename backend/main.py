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
    query = "MATCH (m:Movie) RETURN m"
    results = tx.run(query).data()
    movies = [{'title': result['m']['title'], 'released': result['m']['released']} for result in results]
    return movies


@api.route('/movies', methods=['GET'])
def get_movies_route():
    with driver.session() as session:
        movies = session.read_transaction(get_movies)

    response = {'movies': movies}
    return jsonify(response)


def get_movie(tx, title):
    query = "MATCH (m:Movie {title: $title}) RETURN m"
    result = tx.run(query, title=title).data()

    if not result:
        return None
    else:
        return {'title': result[0]['m']['title'], 'released': result[0]['m']['released']}


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


def add_movie(tx, title, year, genre):
    query = "MATCH (m:Genre {name: $name}) RETURN m"
    result = tx.run(query, name=genre).data()

    if not result:
        return None
    else:
        query = """
            MATCH (g:Genre {name: $name})
            CREATE (:Movie {title: $title, released: $released})-[:BELONGS_TO]->(g)
        """
        tx.run(query, name=genre, title=title, released=year)
        return {'title': title, 'released': year, 'genre': genre}


@api.route('/movies', methods=['POST'])
def add_movie_route():
    title = request.json['title']
    year = request.json['released']
    genre = request.json['genre']

    with driver.session() as session:
        session.write_transaction(add_movie, title, year, genre)

    response = {'status': 'success'}
    return jsonify(response)


def update_movie(tx, title, new_title, new_year):
    query = "MATCH (m:Movie {title: $title}) RETURN m"
    result = tx.run(query, title=title).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Movie {title: $title}) SET m.title=$new_title, m.released=$new_year"
        tx.run(query, title=title, new_title=new_title, new_year=new_year)
        return {'title': new_title, 'year': new_year}


@api.route('/movies/<string:title>', methods=['PUT'])
def update_movie_route(title):
    new_title = request.json['title']
    new_year = request.json['released']

    with driver.session() as session:
        movie = session.write_transaction(update_movie, title, new_title, new_year)

    if not movie:
        response = {'message': 'Movie not found'}
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
