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


def reduce_genres(results, type_reduce):
    tmp0 = results.pop(0)
    tmp1 = tmp0[type_reduce]
    tmp1['genre'] = [tmp0['genre']['name']]
    acc = [tmp1]

    for each in results:
        if acc[0]['title'] == each[type_reduce]['title']:
            acc[0]['genre'].append(each['genre']['name'])
        else:
            tmp = each[type_reduce]
            tmp['genre'] = [each['genre']['name']]
            acc.insert(0, tmp)

    return acc


def swap_person(input_array):
    tmp = input_array['person']
    if input_array['relation'] == 'DIRECTED':
        tmp['directed'] = [input_array['title']]
        tmp['played'] = []
    else:
        tmp['directed'] = []
        tmp['played'] = [(input_array['title'], input_array['role'])]

    return tmp


def get_movies(tx):
    query = "MATCH (movie:Movie)-[:BELONGS_TO]-(genre:Genre) RETURN movie, genre"
    results = tx.run(query).data()
    if not results:
        return None
    else:
        return reduce_genres(results, 'movie')


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
        return reduce_genres(result, 'movie')


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
    locate_movie = "MATCH (m:Movie {title: $title}) RETURN m"
    locate_movie_result = tx.run(locate_movie, title=title).data()

    if locate_movie_result:
        query = """
            MATCH (movie:Movie {title: $title})-[rel:BELONGS_TO]-(:Genre)
            DELETE rel
            SET movie.title=$new_title, movie.released=$new_year, movie.photo=$new_photo
        """
        tx.run(query, title=title, new_title=new_title, new_year=new_year, new_photo=new_photo)

        for each in new_genre:
            locate_genre = "MATCH (m:Genre {name: $name}) RETURN m"
            locate_genre_result = tx.run(locate_genre, name=each).data()
            if not locate_genre_result:
                return None
            else:
                query = """
                    MATCH (movie:Movie {title: $title}), (genre:Genre {name: $name})
                    CREATE (movie)-[:BELONGS_TO]->(genre)
                """
                tx.run(query, title=title, name=each)

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


def get_shows(tx):
    # error when empty!!!
    query = "MATCH (show:Show)-[:BELONGS_TO]-(genre:Genre) RETURN show, genre"
    results = tx.run(query).data()
    if not results:
        return None
    else:
        return reduce_genres(results, 'show')


@api.route('/shows', methods=['GET'])
def get_shows_route():
    with driver.session() as session:
        shows = session.read_transaction(get_shows)

    response = {'shows': shows}
    return jsonify(response)


def get_show(tx, title):
    query = "MATCH (show:Show {title: $title})-[:BELONGS_TO]-(genre:Genre) RETURN show, genre"
    result = tx.run(query, title=title).data()

    if not result:
        return None
    else:
        return reduce_genres(result, 'show')


@api.route('/shows/<string:title>', methods=['GET'])
def get_show_route(title):
    with driver.session() as session:
        show = session.read_transaction(get_show, title)

    if not show:
        response = {'message': 'Show not found'}
        return jsonify(response), 404
    else:
        response = {'show': show}
        return jsonify(response)


def add_show(tx, title, released, ended, episodes, photo, genre):
    query = "CREATE (:Show {title: $title, released: $released, ended: $ended, episodes: $episodes, photo: $photo})"
    tx.run(query, title=title, released=released, ended=ended, episodes=episodes, photo=photo)

    for each in genre:
        locate_genre = "MATCH (m:Genre {name: $name}) RETURN m"
        locate_genre_result = tx.run(locate_genre, name=each).data()
        if not locate_genre_result:
            return None
        else:
            query = """
                MATCH (show:Show {title: $title}), (genre:Genre {name: $name})
                CREATE (show)-[:BELONGS_TO]->(genre)
            """
            tx.run(query, title=title, name=each)

    return {'title': title, 'released': released, 'ended': ended, 'episodes': episodes, 'photo': photo, 'genre': genre}


@api.route('/shows', methods=['POST'])
def add_show_route():
    title = request.json['title']
    released = request.json['released']
    ended = request.json['ended']
    episodes = request.json['episodes']
    photo = request.json['photo']
    genre = request.json['genre']

    with driver.session() as session:
        session.write_transaction(add_show, title, released, ended, episodes, photo, genre)

    response = {'status': 'success'}
    return jsonify(response)


def update_show(tx, title, new_title, new_released, new_ended, new_episodes, new_photo, new_genre):
    locate_show = "MATCH (m:Show {title: $title}) RETURN m"
    locate_show_result = tx.run(locate_show, title=title).data()

    if locate_show_result:
        query = """
            MATCH (show:Show {title: $title})-[rel:BELONGS_TO]-(:Genre)
            DELETE rel
            SET 
                show.title=$new_title,
                show.released=$new_released,
                show.ended=$new_ended,
                show.episodes=$new_episodes,
                show.photo=$new_photo
        """
        tx.run(
            query,
            title=title,
            new_title=new_title,
            new_released=new_released,
            new_ended=new_ended,
            new_episodes=new_episodes,
            new_photo=new_photo
        )

        for each in new_genre:
            locate_genre = "MATCH (m:Genre {name: $name}) RETURN m"
            locate_genre_result = tx.run(locate_genre, name=each).data()
            if not locate_genre_result:
                return None
            else:
                query = """
                    MATCH (show:Show {title: $title}), (genre:Genre {name: $name})
                    CREATE (show)-[:BELONGS_TO]->(genre)
                """
                tx.run(query, title=title, name=each)

        return {
            'title': new_title,
            'released': new_released,
            'ended': new_ended,
            'episodes': new_episodes,
            'photo': new_photo,
            'genre': new_genre
        }
    else:
        return None


@api.route('/shows/<string:title>', methods=['PUT'])
def update_show_route(title):
    new_title = request.json['title']
    new_released = request.json['released']
    new_ended = request.json['ended']
    new_episodes = request.json['episodes']
    new_photo = request.json['photo']
    new_genre = request.json['genre']

    with driver.session() as session:
        show = session.write_transaction(
            update_show,
            title,
            new_title,
            new_released,
            new_ended,
            new_episodes,
            new_photo,
            new_genre
        )

    if not show:
        response = {'message': 'Show or Genre not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_show(tx, title):
    query = "MATCH (m:Show {title: $title}) RETURN m"
    result = tx.run(query, title=title).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Show {title: $title}) DETACH DELETE m"
        tx.run(query, title=title)
        return {'title': title}


@api.route('/shows/<string:title>', methods=['DELETE'])
def delete_show_route(title):
    with driver.session() as session:
        show = session.write_transaction(delete_show, title)

    if not show:
        response = {'message': 'Show not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


def get_persons(tx):
    query = """
        MATCH (person:Person)-[rel:PLAYED|DIRECTED]-(m)
        WITH person, TYPE(rel) AS relation, m.title AS title, rel.who AS role
        RETURN person, relation, title, role
    """
    results = tx.run(query).data()
    if not results:
        return None
    else:
        tmp = results.pop(0)
        acc = [swap_person(tmp)]

        for each in results:
            if acc[0]['name'] == each['person']['name']:
                if each['relation'] == 'DIRECTED':
                    acc[0]['directed'].append(each['title'])
                else:
                    acc[0]['played'].append((each['title'], each['role']))
            else:
                acc.insert(0, swap_person(each))

        return acc


@api.route('/persons', methods=['GET'])
def get_persons_route():
    with driver.session() as session:
        persons = session.read_transaction(get_persons)

    response = {'persons': persons}
    return jsonify(response)


def add_person(tx, name, born):
    query = "CREATE (:Person {name: $name, born: $born})"
    tx.run(query, name=name, born=born)

    return {'name': name, 'born': born}


@api.route('/persons', methods=['POST'])
def add_person_route():
    name = request.json['name']
    born = request.json['born']

    with driver.session() as session:
        session.write_transaction(add_person, name, born)

    response = {'status': 'success'}
    return jsonify(response)


def add_connection_played(tx, name, played_in, who):
    locate_person = "MATCH (m:Person {name: $name}) RETURN m"
    locate_person_result = tx.run(locate_person, name=name).data()

    if locate_person_result:
        locate_title = "MATCH (m {title: $title}) RETURN m"
        locate_title_result = tx.run(locate_title, title=played_in).data()

        if not locate_title_result:
            return None
        else:
            query = """
                MATCH (person:Person {name: $name}), (m {title: $title})
                CREATE (person)-[:PLAYED {who: $who}]->(m)
            """
            tx.run(query, name=name, title=played_in, who=who)

        return {'name': name, 'title': played_in, 'role': who}
    else:
        return None


@api.route('/persons/played', methods=['POST'])
def add_connection_played_route():
    name = request.json['name']
    title = request.json['title']
    role = request.json['role']

    with driver.session() as session:
        session.write_transaction(add_connection_played, name, title, role)

    response = {'status': 'success'}
    return jsonify(response)


def add_connection_directed(tx, name, directed):
    locate_person = "MATCH (m:Person {name: $name}) RETURN m"
    locate_person_result = tx.run(locate_person, name=name).data()

    if locate_person_result:
        locate_title = "MATCH (m {title: $title}) RETURN m"
        locate_title_result = tx.run(locate_title, title=directed).data()

        if not locate_title_result:
            return None
        else:
            query = """
                MATCH (person:Person {name: $name}), (m {title: $title})
                CREATE (person)-[:DIRECTED]->(m)
            """
            tx.run(query, name=name, title=directed)

        return {'name': name, 'directed': directed}
    else:
        return None


@api.route('/persons/directed', methods=['POST'])
def add_connection_directed_route():
    name = request.json['name']
    title = request.json['title']

    with driver.session() as session:
        session.write_transaction(add_connection_directed, name, title)

    response = {'status': 'success'}
    return jsonify(response)


def update_person(tx, name, new_name, new_year):
    query = "MATCH (m:Person {name: $name}) RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Person {name: $name}) SET m.name=$new_name, m.born=$new_year"
        tx.run(query, name=name, new_name=new_name, new_year=new_year)
        return {'name': new_name, 'born': new_year}


@api.route('/persons/<string:name>', methods=['PUT'])
def update_person_route(name):
    new_name = request.json['name']
    new_year = request.json['born']

    with driver.session() as session:
        person = session.write_transaction(update_person, name, new_name, new_year)

    if not person:
        response = {'message': 'Person not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


def update_connection_played(tx, name, title, role, new_title, new_role):
    locate_connection = "MATCH (:Person {name: $name})-[conn:PLAYED {who: $role}]-({title: $title}) RETURN conn"
    locate_connection_result = tx.run(locate_connection, name=name, role=role, title=title).data()

    if locate_connection_result:
        query = """
            MATCH (person:Person {name: $name})-[conn:PLAYED {who: $role}]-(m {title: $title}), (new {title: $new_title})
            WITH person, conn, m, new
            DELETE conn
            CREATE (person)-[:PLAYED {who: $new_role}]->(new)
        """
        tx.run(query, name=name, title=title, role=role, new_title=new_title, new_role=new_role)

        return {
            'person': name,
            'title': new_title,
            'role': new_role
        }
    else:
        return None


@api.route('/persons/played/<string:name>&<string:title>&<string:role>', methods=['PUT'])
def update_connection_played_route(name, title, role):
    new_title = request.json['title']
    new_role = request.json['role']

    with driver.session() as session:
        connection = session.write_transaction(update_connection_played, name, title, role, new_title, new_role)

    if not connection:
        response = {'message': 'Relation not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


def delete_person(tx, name):
    query = "MATCH (m:Person {name: $name}) RETURN m"
    result = tx.run(query, name=name).data()

    if not result:
        return None
    else:
        query = "MATCH (m:Person {name: $name}) DETACH DELETE m"
        tx.run(query, name=name)
        return {'name': name}


@api.route('/persons/<string:name>', methods=['DELETE'])
def delete_person_route(name):
    with driver.session() as session:
        person = session.write_transaction(delete_person, name)

    if not person:
        response = {'message': 'Person not found'}
        return jsonify(response), 404
    else:
        response = {'status': 'success'}
        return jsonify(response)


if __name__ == '__main__':
    api.run()
