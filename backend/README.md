## API:

### Genres
1. GET all genres in database:<br />
http GET http://127.0.0.1:5000/genres
2. Sort genres in alphabetic order (by name):<br />
http GET http://127.0.0.1:5000/genres/sort/by_name
3. Sort genres by name in reverse order:<br />
http GET http://127.0.0.1:5000/genres/sort/reverse/by_name
4. POST new genre:<br />
http POST http://127.0.0.1:5000/admin/genres genre="name"
5. There is no PUT 'cause :Genre don't have any properties.
6. DELETE genre by its ID:<br />
http DELETE http://127.0.0.1:5000/admin/genres/<int:the_id>

### Persons
1. GET all persons (person can be both actor and director but not a user):<br />
http GET http://127.0.0.1:5000/persons
2. GET person by its name (name & surname):<br />
http GET http://127.0.0.1:5000/persons/find/by_name/<string:name>&<string:surname>
3. Sort persons by name:<br />
http GET http://127.0.0.1:5000/persons/sort/by_name
4. Sort persons by name in reverse order:<br />
http GET http://127.0.0.1:5000/persons/sort/reverse/by_name
5. Sort persons by played roles:<br />
http GET http://127.0.0.1:5000/persons/sort/by_roles
6. Sort persons by played roles in reverse order:<br />
http GET http://127.0.0.1:5000/persons/sort/reverse/by_roles
7. Sort persons by directed movies:<br />
http GET http://127.0.0.1:5000/persons/sort/by_directed
8. Sort persons by directed movies in reverse order:<br />
http GET http://127.0.0.1:5000/persons/sort/reverse/by_directed
9. GET person info by its ID:<br />
http GET http://127.0.0.1:5000/persons/<int:the_id>
10. POST new :Person node:<br />
http POST http://127.0.0.1:5000/admin/persons name="name" surname="surname" born=1999 photo="photoURL"
11. PUT persons info:<br />
http PUT http://127.0.0.1:5000/admin/persons/<int:the_id> name="name" surname="surname" born=1999 photo="photoURL"
12. DELETE :Person by ID:<br />
http DELETE http://127.0.0.1:5000/admin/persons/<int:the_id>

### Shows
1. GET shows:<br />
http GET http://127.0.0.1:5000/shows
2. GET top 5 shows by its score:<br />
http GET http://127.0.0.1:5000/shows/top
3. GET show by its title:<br />
http GET http://127.0.0.1:5000/shows/find/by_name/<string:title>
4. Sort shows by genre:<br />
http GET http://127.0.0.1:5000/shows/sort/by_genre
5. Sort shows by genre in reverse order:<br />
http GET http://127.0.0.1:5000/shows/sort/reverse/by_genre
6. Sort shows by name (aka. title):<br />
http GET http://127.0.0.1:5000/shows/sort/by_name
7. Sort shows by its title in reverse order:<br />
http GET http://127.0.0.1:5000/shows/sort/reverse/by_name
8. Sort shows by score (from greatest to smallest):<br />
http GET http://127.0.0.1:5000/shows/sort/by_score
9. Sort shows by score in reverse order:<br />
http GET http://127.0.0.1:5000/shows/sort/reverse/by_score
10. GET show details by ID:<br />
http GET http://127.0.0.1:5000/shows/<int:the_id>
11. POST new :Show:<br />
http POST http://127.0.0.1:5000/admin/shows title="title" genre="genre" photo="photoURL" trailer="trailerURL" episodes=10 released="01/12/2000" ended="01/12/2001"
12. PUT show info:<br />
http PUT http://127.0.0.1:5000/admin/shows/<int:the_id> title="title" genre="genre" photo="photoURL" trailer="trailerURL" episodes=10 released="01/12/2000" ended="01/12/2001"
13. DELETE show:<br />
http DELETE http://127.0.0.1:5000/admin/shows/<int:the_id>

### Users
1. GET all users:<br />
http GET http://127.0.0.1:5000/users
2. GET user by its name:<br />
http GET http://127.0.0.1:5000/users/find/by_name/<string:nick>
3. Sort users by its name (Big letters goes first):<br />
http GET http://127.0.0.1:5000/users/sort/by_name
4. Sort users by name in reverse order:<br />
http GET http://127.0.0.1:5000/users/sort/reverse/by_name
5. Sort users by activity (from the most active to least active):<br />
http GET http://127.0.0.1:5000/users/sort/by_activity
6. Sort users by activity in reverse order:<br />
http GET http://127.0.0.1:5000/users/sort/reverse/by_activity
7. GET top 3 users by activity:<br />
http GET http://127.0.0.1:5000/users/top
8. GET user details:<br />
http GET http://127.0.0.1:5000/users/<int:the_id>
9. POST new user:<br />
http POST http://127.0.0.1:5000/admin/users nick="nick" e_mail="e_mail" password="password" registered="01/12/2000" photo="photoURL"
10. PUT user info by ID:<br />
http PUT http://127.0.0.1:5000/admin/users/<int:the_id> nick="nick" e_mail="e_mail" password="password" registered="01/12/2000" photo="photoURL"
11. DELETE user by its ID:<br />
http DELETE http://127.0.0.1:5000/admin/users/<int:the_id>

### Reviews
1. GET reviews:<br />
http GET http://127.0.0.1:5000/reviews
2. Sort reviews by likes:<br />
http GET http://127.0.0.1:5000/reviews/sort/by_score
3. Sort reviews by likes in reverse order:<br />
http GET http://127.0.0.1:5000/reviews/sort/reverse/by_score
4. Sort reviews by amount of comments:<br />
http GET http://127.0.0.1:5000/reviews/sort/by_comments
5. Sort reviews by comments in reverse order:<br />
http GET http://127.0.0.1:5000/reviews/sort/reverse/by_comments
6. Sort reviews by title:<br />
http GET http://127.0.0.1:5000/reviews/sort/by_title
7. Sort reviews by title in reverse:<br />
http GET http://127.0.0.1:5000/reviews/sort/reverse/by_title
8. Sort reviews by its author:<br />
http GET http://127.0.0.1:5000/reviews/sort/by_author
9. Sort reviews by author in reverse:<br />
http GET http://127.0.0.1:5000/reviews/sort/reverse/by_author
10. GET review info:<br />
http GET http://127.0.0.1:5000/reviews/<int:the_id>
11. POST review:<br />
http POST http://127.0.0.1:5000/reviews user="nick" title="title" body="body"
12. PUT review's body:<br />
http PUT http://127.0.0.1:5000/reviews/<int:the_id> body="body"
13. DELETE review:<br />
http DELETE http://127.0.0.1:5000/reviews/<int:the_id>

### Show Connections
1. SEEN:
   * GET connections:<br />
   http GET http://127.0.0.1:5000/connection/show/seen
   * POST new connection:<br />
   http POST http://127.0.0.1:5000/connection/show/seen user="user" title="title"
   * There is no PUT 'cause connection has no attributes.
   * DELETE connection by ID:<br />
   http DELETE http://127.0.0.1:5000/connection/show/seen/<int:the_id>
2. LIKES:
    * GET all connections LIKES:<br />
   http GET http://127.0.0.1:5000/connection/show/likes
    * POST connection:<br />
   http POST http://127.0.0.1:5000/connection/show/likes user="user" title="title"
    * No PUT = no properties.
    * DELETE connection by ID:<br />
   http DELETE http://127.0.0.1:5000/connection/show/likes/<int:the_id>
3. WANTS_TO_WATCH:
    * GET connections:<br />
   http GET http://127.0.0.1:5000/connection/show/wants_to_watch
    * POST connection:<br />
   http POST http://127.0.0.1:5000/connection/show/wants_to_watch user="user" title="title"
    * DELETE connection:<br />
   http DELETE http://127.0.0.1:5000/connection/show/wants_to_watch/<int:the_id>
4. PLAYED:
    * GET:<br />
   http GET http://127.0.0.1:5000/admin/connection/show/played
    * POST new:<br />
   http POST http://127.0.0.1:5000/admin/connection/show/played person_id=11 role="role" title="title"
    * PUT connection's info:<br />
   http PUT http://127.0.0.1:5000/admin/connection/show/played/<int:the_id> role="role"
    * DELETE:<br />
   http DELETE http://127.0.0.1:5000/admin/connection/show/played/<int:the_id>
5. DIRECTED:
    * GET:<br />
   http GET http://127.0.0.1:5000/admin/connection/show/directed
    * POST:<br />
   http POST http://127.0.0.1:5000/admin/connection/show/directed person_id=11 title="title"
    * No PUT, no attributes.
    * DELETE:<br />
   http DELETE http://127.0.0.1:5000/admin/connection/show/directed/<int:the_id>

### Review Connections
1. LIKES:
   * GET:<br />
   http GET http://127.0.0.1:5000/connection/review/likes
   * POST:<br />
   http POST http://127.0.0.1:5000/connection/review/likes user="user" review_id=11
   * No PUT, no properties.
   * DELETE:<br />
   http DELETE http://127.0.0.1:5000/connection/review/likes/<int:the_id>
2. COMMENTS:
   * GET:<br />
   http GET http://127.0.0.1:5000/connection/review/comments
   * POST:<br />
   http POST http://127.0.0.1:5000/connection/review/comments user="user" comment="comment" review_id=10
   * PUT comment's body:<br />
   http PUT http://127.0.0.1:5000/connection/review/comments/<int:the_id> comment="comment"
   * DELETE:<br />
   http DELETE http://127.0.0.1:5000/connection/review/comments/<int:the_id>