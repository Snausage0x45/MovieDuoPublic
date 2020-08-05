# Import all the things #
import json
import requests
from flask import Flask, render_template, request
import re


# Declare all the things #
app = Flask(__name__)
api_token = ''
api_base_url = 'https://api.themoviedb.org/3/search/person/'

# function declaration to get the shared movies
def getactorids(actor1st, actor2nd):
    url1 = api_base_url + '?api_key=' + api_token + '&query=' + actor1st
    url2 = api_base_url + '?api_key=' + api_token + '&query=' + actor2nd
    # Make the api calls to get the actor IDs #
    response1 = requests.get(
        url1
    )
    response2 = requests.get(
        url2
    )
    # Convert to JSON #
    response1text = response1.json()
    response2text = response2.json()
    # Get both actor IDs in both responses #
    userId1 = response1text['results'][0]['id']
    userId2 = response2text['results'][0]['id']
    # Look up Actor's full movie page from ID #
    userId1str = str(userId1)
    userId2str = str(userId2)
    # take the actor ID and look up all move credits for the actor #
    urlActor1 = 'https://api.themoviedb.org/3/person/' + userId1str + '/movie_credits' + '?api_key=' + api_token
    urlActor2 = 'https://api.themoviedb.org/3/person/' + userId2str + '/movie_credits' + '?api_key=' + api_token
    actorFull1 = requests.get(
        urlActor1
    )
    actorFull2 = requests.get(
        urlActor2
    )
    # take both actors movie credits, convert them to strings, cut out the movie IDs, then compare
    global actorcomparestr
    actorFull1json = actorFull1.json()
    actorFull2json = actorFull2.json()
    actorFull1jsonStr = str(actorFull1json)
    actorFull2jsonStr = str(actorFull2json)
    actorFull1cutIds = re.findall(r'id.:\s\d+', actorFull1jsonStr)
    actorFull2cutIds = re.findall(r'id.:\s\d+', actorFull2jsonStr)
    actorFull1cutIdsStr = str(actorFull1cutIds)
    actorFull2cutIdsStr = str(actorFull2cutIds)
    actorFull1cutNum = re.findall(r'\d+', actorFull1cutIdsStr)
    actorFull2cutNum = re.findall(r'\d+', actorFull2cutIdsStr)
    actorset1 = set(actorFull1cutNum)
    actorset2 = set(actorFull2cutNum)
    actorcompare = actorset1.intersection(actorset2)
    actorcomparestr = str(actorcompare)
    return actorcomparestr



# Declare function to look up movies based on shared list #
def getmovies(movieids):
    global movielookupfinal
    global reports
    movielookupfinal = []
    # RegEx to parseout movie IDs
    movielookupmakelist = re.findall(r'\d+', movieids)
    for movie in movielookupmakelist:
        movieLookUpBuild = 'https://api.themoviedb.org/3/movie/' + movie + '?api_key=' + api_token + "&append_to_response=images"
        movieLookUp = requests.get(
            movieLookUpBuild
        )
        movielookupjson = movieLookUp.json()
        # build the json object of each shared entry
        # https://image.tmdb.org/t/p/original/mhZIcRePT7U8viFQVjt1ZjYIsR4.jpg #
        movie_json = {"title": movielookupjson['title'],
                      "overview": movielookupjson['overview'],
                      "rating": movielookupjson['vote_average'],
                      "release_date": movielookupjson['release_date'],
                      "poster": movielookupjson['poster_path']
                      }
        # Append to varaible to build list of movies
        movielookupfinal.append(movie_json)
        # print(movielookupfinal)
    return movielookupfinal


@app.route("/", methods=["POST", "GET"])
def hello():
    if request.method == "POST":
        # get the actors from the form
        actor1Pre = request.form["nm"]
        actor2Pre = request.form["nm2"]
        # change spaces to + for the api calls
        actor1 = actor1Pre.replace(" ", "+")
        actor2 = actor2Pre.replace(" ", "+")
        # run both functions with the inputs
        getactorids(actor1, actor2)
        getmovies(actorcomparestr)
        titles = ()
        overview = ()
        rating = ()
        release_date = ()
        poster = ()
        # check if variable is populated or not
        if movielookupfinal:
            for count in range(0, len(movielookupfinal)):
                print(movielookupfinal[count]['title'])
                titles1 = movielookupfinal[count]['title']
                overview1 = movielookupfinal[count]['overview']
                rating1 = movielookupfinal[count]['rating']
                release_date1 = movielookupfinal[count]['release_date']
                poster1 = movielookupfinal[count]['poster']
                if poster1 is None:
                    poster1 = "/notNull"
                poster3 = "https://image.tmdb.org/t/p/original" + poster1
                titles += titles1,
                overview += overview1,
                rating += rating1,
                release_date += release_date1,
                poster += poster3,
                # print([v for k, v in movielookupfinal[count].items()])
        else:
            titles += "None!",
            overview += "These two actors have not been in a move together",
            rating += "N/A",
            release_date += "Never",
            poster += "",
        return render_template("base.html", conTitle=titles, conOverview=overview, conRating=rating, conRelease=release_date, conPoster=poster, conLen=len(titles))
    else:
        return render_template("home.html")


if __name__ == "__main__":
    app.run()