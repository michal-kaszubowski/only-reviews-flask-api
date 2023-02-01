# Baza danych serwisu internetowego Only Reviews
## Funkcjonalność
Aplikacja umożliwia komunikację z grafową bazą danych Neo4j za pomocą protokołu HTTP.
W bazie danych znajdują się węzły Seriali (:Show) połączone relacją [:BELONGS]
z gatunkami, do których należą. Relacja [:BELONGS] jest wymagana do utworzenia węzła.<br />
Użytkownicy, których dane przechowywane są w węzłach typu :User mają możliwość pisania recenzji <b>obejrzanych</b>
seriali (:Review). Autor każdej recenzji jest z nią połączony relacją [:WROTE], z kolei recenzja łączy się z serialem
relacją [:ABOUT]. Dodatkowo wszyscy użytkownicy mogą pozostawiać swoje komentarze pod recenzjami za pomocą relacji
[:COMMENTS].<br />
Baza danych przechowywuje również informacje dotyczące obsady i reżyserów seriali w postaci węzłów typu :Person
połączonych z serialami odpowiednio relacjami [:PLAYED] z właściwością role oraz [:DIRECTED].<br />
Możliwe jest również pobranie całej bazy danych bądź wyników wybranych zapytań w postaci sformatowanej do standardów
CSV i JSON.<br />
Aplikacja pozwala również na zarekomendowanie seriali dla danych użytkowników.<br />

## Endpointy

### Genres
1. GET all genres in database:<br />
http GET http://127.0.0.1:5000/genres
2. Export all genres to CSV:<br />
http GET http://127.0.0.1:5000/admin/get/csv/genres
3. Export genres to JSON:<br />
http GET http://127.0.0.1:5000/admin/get/json/genres
4. Sort genres in alphabetic order (by name):<br />
http GET http://127.0.0.1:5000/genres/sort/by_name
5. Sort genres by name in reverse order:<br />
http GET http://127.0.0.1:5000/genres/sort/reverse/by_name
6. POST new genre:<br />
http POST http://127.0.0.1:5000/admin/genres genre="name"
7. There is no PUT 'cause :Genre don't have any properties.
8. DELETE genre by its ID:<br />
http DELETE http://127.0.0.1:5000/admin/genres/<int:the_id>

### Persons
1. GET all persons (person can be both actor and director but not a user):<br />
http GET http://127.0.0.1:5000/persons
2. Export all persons to CSV:<br />
http GET http://127.0.0.1:5000/admin/get/csv/persons
3. Export all to JSON:<br />
http GET http://127.0.0.1:5000/admin/get/json/persons
4. GET person by its name (name & surname):<br />
http GET http://127.0.0.1:5000/persons/find/by_name/<string:name>&<string:surname>
5. Sort persons by name:<br />
http GET http://127.0.0.1:5000/persons/sort/by_name
6. Sort persons by name in reverse order:<br />
http GET http://127.0.0.1:5000/persons/sort/reverse/by_name
7. Sort persons by played roles:<br />
http GET http://127.0.0.1:5000/persons/sort/by_roles
8. Sort persons by played roles in reverse order:<br />
http GET http://127.0.0.1:5000/persons/sort/reverse/by_roles
9. Sort persons by directed movies:<br />
http GET http://127.0.0.1:5000/persons/sort/by_directed
10. Sort persons by directed movies in reverse order:<br />
http GET http://127.0.0.1:5000/persons/sort/reverse/by_directed
11. GET person info by its ID:<br />
http GET http://127.0.0.1:5000/persons/<int:the_id>
12. POST new :Person node:<br />
http POST http://127.0.0.1:5000/admin/persons name="name" surname="surname" born=1999 photo="photoURL"
13. PUT persons info:<br />
http PUT http://127.0.0.1:5000/admin/persons/<int:the_id> name="name" surname="surname" born=1999 photo="photoURL"
14. DELETE :Person by ID:<br />
http DELETE http://127.0.0.1:5000/admin/persons/<int:the_id>

### Shows
1. GET shows:<br />
http GET http://127.0.0.1:5000/shows
2. Export all shows to CSV:<br />
http GET http://127.0.0.1:5000/admin/get/csv/shows
3. Export shows to JSON:<br />
http GET http://127.0.0.1:5000/admin/get/json/shows
4. GET top 5 shows by its score:<br />
http GET http://127.0.0.1:5000/shows/top
5. Recommend shows for specified user:<br />
http GET http://127.0.0.1:5000/shows/recommend/<int:the_id>
6. GET show by its title:<br />
http GET http://127.0.0.1:5000/shows/find/by_name/<string:title>
7. Sort shows by genre:<br />
http GET http://127.0.0.1:5000/shows/sort/by_genre
8. Sort shows by genre in reverse order:<br />
http GET http://127.0.0.1:5000/shows/sort/reverse/by_genre
9. Sort shows by name (aka. title):<br />
http GET http://127.0.0.1:5000/shows/sort/by_name
10. Sort shows by its title in reverse order:<br />
http GET http://127.0.0.1:5000/shows/sort/reverse/by_name
11. Sort shows by score (from greatest to smallest):<br />
http GET http://127.0.0.1:5000/shows/sort/by_score
12. Sort shows by score in reverse order:<br />
http GET http://127.0.0.1:5000/shows/sort/reverse/by_score
13. GET show details by ID:<br />
http GET http://127.0.0.1:5000/shows/<int:the_id>
14. POST new :Show:<br />
http POST http://127.0.0.1:5000/admin/shows title="title" genre="genre" photo="photoURL" trailer="trailerURL" episodes=10 released="01/12/2000" ended="01/12/2001"
15. PUT show info:<br />
http PUT http://127.0.0.1:5000/admin/shows/<int:the_id> title="title" genre="genre" photo="photoURL" trailer="trailerURL" episodes=10 released="01/12/2000" ended="01/12/2001"
16. DELETE show:<br />
http DELETE http://127.0.0.1:5000/admin/shows/<int:the_id>

### Users
1. GET all users:<br />
http GET http://127.0.0.1:5000/users
2. Export all users to CSV:<br />
http GET http://127.0.0.1:5000/admin/get/csv/users
3. Export users to JSON:<br />
http GET http://127.0.0.1:5000/admin/get/json/users
4. GET user by its name:<br />
http GET http://127.0.0.1:5000/users/find/by_name/<string:nick>
5. Sort users by its name (Big letters goes first):<br />
http GET http://127.0.0.1:5000/users/sort/by_name
6. Sort users by name in reverse order:<br />
http GET http://127.0.0.1:5000/users/sort/reverse/by_name
7. Sort users by activity (from the most active to least active):<br />
http GET http://127.0.0.1:5000/users/sort/by_activity
8. Sort users by activity in reverse order:<br />
http GET http://127.0.0.1:5000/users/sort/reverse/by_activity
9. GET top 3 users by activity:<br />
http GET http://127.0.0.1:5000/users/top
10. GET user details:<br />
http GET http://127.0.0.1:5000/users/<int:the_id>
11. POST new user:<br />
http POST http://127.0.0.1:5000/admin/users nick="nick" e_mail="e_mail" password="password" registered="01/12/2000" photo="photoURL"
12. PUT user info by ID:<br />
http PUT http://127.0.0.1:5000/admin/users/<int:the_id> nick="nick" e_mail="e_mail" password="password" registered="01/12/2000" photo="photoURL"
13. DELETE user by its ID:<br />
http DELETE http://127.0.0.1:5000/admin/users/<int:the_id>

### Reviews
1. GET reviews:<br />
http GET http://127.0.0.1:5000/reviews
2. Export reviews to CSV:<br />
http GET http://127.0.0.1:5000/admin/get/csv/reviews
3. Export all to JSON:<br />
http GET http://127.0.0.1:5000/admin/get/json/reviews
4. Sort reviews by likes:<br />
http GET http://127.0.0.1:5000/reviews/sort/by_score
5. Sort reviews by likes in reverse order:<br />
http GET http://127.0.0.1:5000/reviews/sort/reverse/by_score
6. Sort reviews by amount of comments:<br />
http GET http://127.0.0.1:5000/reviews/sort/by_comments
7. Sort reviews by comments in reverse order:<br />
http GET http://127.0.0.1:5000/reviews/sort/reverse/by_comments
8. Sort reviews by title:<br />
http GET http://127.0.0.1:5000/reviews/sort/by_title
9. Sort reviews by title in reverse:<br />
http GET http://127.0.0.1:5000/reviews/sort/reverse/by_title
10. Sort reviews by its author:<br />
http GET http://127.0.0.1:5000/reviews/sort/by_author
11. Sort reviews by author in reverse:<br />
http GET http://127.0.0.1:5000/reviews/sort/reverse/by_author
12. GET review info:<br />
http GET http://127.0.0.1:5000/reviews/<int:the_id>
13. POST review:<br />
http POST http://127.0.0.1:5000/reviews user="nick" title="title" body="body"
14. PUT review's body:<br />
http PUT http://127.0.0.1:5000/reviews/<int:the_id> body="body"
15. DELETE review:<br />
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

### Export Database
1. To CSV:<br />
http GET http://127.0.0.1:5000/admin/get/csv/database
2. To JSON:<br />
http GET http://127.0.0.1:5000/admin/get/json/database