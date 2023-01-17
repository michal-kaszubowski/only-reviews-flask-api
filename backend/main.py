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


# /genres---------------------------------------------------------------------------------------------------------------


def get_genres(tx):
    locate_genre = "MATCH (genre:Genre) RETURN genre"
    locate_genre_result = tx.run(locate_genre).data()

    genres = [{'name': result['genre']['name']} for result in locate_genre_result]
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


if __name__ == '__main__':
    api.run()
