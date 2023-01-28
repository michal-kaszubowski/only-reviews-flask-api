## API:

### Genres
1. GET all genres in database:<br />
http GET http://127.0.0.1:5000/genres
2. POST new genre:<br />
http POST http://127.0.0.1:5000/admin/genres genre="name"
3. There is no PUT 'cause :Genre don't have any properties.
4. DELETE genre by its ID:<br />
http DELETE http://127.0.0.1:5000/admin/genres/<int:the_id>

### Persons
1. GET all persons (person can be both actor and director but not a user):<br />
http GET http://127.0.0.1:5000/persons
2. GET person info by its ID:<br />
http GET http://127.0.0.1:5000/persons/<int:the_id>
3. POST new :Person node:<br />
http POST http://127.0.0.1:5000/admin/persons name="name" surname="surname" born=1999 photo="photoURL"
4. PUT persons info:<br />
http PUT http://127.0.0.1:5000/admin/persons/<int:the_id> name="name" surname="surname" born=1999 photo="photoURL"
5. DELETE :Person by ID:<br />
http DELETE http://127.0.0.1:5000/admin/persons/<int:the_id>

### Shows
1. GET shows:<br />
http GET http://127.0.0.1:5000/shows
2. GET top 5 shows by its score:<br />
http GET http://127.0.0.1:5000/shows/top
3. GET show by its title:<br />
http GET http://127.0.0.1:5000/shows/find/by_name/<string:title>
4. GET show details by ID:<br />
http GET http://127.0.0.1:5000/shows/<int:the_id>
5. POST new :Show:<br />
http POST http://127.0.0.1:5000/admin/shows title="title" genre="genre" photo="photoURL" trailer="trailerURL" episodes=10 released="01/12/2000" ended="01/12/2001"
6. PUT show info:<br />
http PUT http://127.0.0.1:5000/admin/shows/<int:the_id> title="title" genre="genre" photo="photoURL" trailer="trailerURL" episodes=10 released="01/12/2000" ended="01/12/2001"
7. DELETE show:<br />
http DELETE http://127.0.0.1:5000/admin/shows/<int:the_id>

### Users
1. GET all users:<br />
http GET http://127.0.0.1:5000/users
2. GET user details:<br />
http GET http://127.0.0.1:5000/users/<int:the_id>
3. POST new user:<br />
http POST http://127.0.0.1:5000/admin/users nick="nick" e_mail="e_mail" password="password" registered="01/12/2000" photo="photoURL"
4. PUT user info by ID:<br />
http PUT http://127.0.0.1:5000/admin/users/<int:the_id> nick="nick" e_mail="e_mail" password="password" registered="01/12/2000" photo="photoURL"
5. DELETE user by its ID:<br />
http DELETE http://127.0.0.1:5000/admin/users/<int:the_id>

### Reviews
1. GET reviews:<br />
http GET http://127.0.0.1:5000/reviews
2. GET review info:<br />
http GET http://127.0.0.1:5000/reviews/<int:the_id>
3. POST review:<br />
http POST http://127.0.0.1:5000/reviews user="nick" title="title" body="body"
4. PUT review's body:<br />
http PUT http://127.0.0.1:5000/reviews/<int:the_id> body="body"
5. DELETE review:<br />
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