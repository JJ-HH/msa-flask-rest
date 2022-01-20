from flask import Flask, Response, request
from flask import json, jsonify
from flask_restx import Api, Resource, fields


app = Flask(__name__)
api = Api(app)
ns_movies = api.namespace('ns_movies', description='Movies API')

movie_data = api.model(
    'Movie Data',
    {
      "title": fields.String(description="Title of movie", required=True),
      "year": fields.Integer(description="Year released", required=True),
      "cast": fields.List(fields.String, description="Cast of movie", required=True),
      "poster": fields.Url(description="Image Url for poster", required=True),
      "description": fields.String(description="Description of movie", required=True)
    }
)

f = open("./movie_info.json", "r")
loaded_json = json.load(f)
movie_info = {f'{dct["title"]}-{dct["year"]}': dct for dct in loaded_json.get("movies_list")}


@ns_movies.route("/")
class movies(Resource):
    def get(self):
        return jsonify(movie_info)

    @api.expect(movie_data)
    def post(self):
        params = request.get_json()
        if (t := params.get("title", "")) and (y := params.get("year", "")):
            try:
                new_id  = f'{t}-{y}'
                movie_info[new_id] = params
            except:
                return Response(status=409)
        else:
            return Response(status=400)
        return Response(status=200)


@ns_movies.route("/<string:id>")
class movie_detail(Resource):
    def get(self, id):
        if id not in movie_info:
            return Response(status=404)
        return movie_info.get(id)

    def put(self):
        if id not in movie_info:
            return Response(status=404)
        return Response(status=200)

    def delete(self, id):
        try:
            del movie_info[id]
        except KeyError:
            return Response(status=404)
        return Response(status=200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
