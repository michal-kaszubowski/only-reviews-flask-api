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
    query = "MATCH (m:Movie) WHERE m.title=$title RETURN m"
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


def add_movie(tx, title, year):
    query = "CREATE (m:Movie {title: $title, released: $released})"
    tx.run(query, title=title, released=year)


@api.route('/movies', methods=['POST'])
def add_movie_route():
    title = request.json['title']
    year = request.json['released']

    with driver.session() as session:
        session.write_transaction(add_movie, title, year)

    response = {'status': 'success'}
    return jsonify(response)


def update_movie(tx, title, new_title, new_year):
    query = "MATCH (m:Movie) WHERE m.title=$title RETURN m"
    result = tx.run(query, title=title).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Movie) WHERE m.title=$title SET m.title=$new_title, m.released=$new_year"
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
    query = "MATCH (m:Movie) WHERE m.title=$title RETURN m"
    result = tx.run(query, title=title).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Movie) WHERE m.title=$title DETACH DELETE m"
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


if __name__ == '__main__':
    api.run()
