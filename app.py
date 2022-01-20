from doctest import debug_script
from email.policy import strict
from flask import Flask, Response, request, abort
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
                if new_id in movie_info.keys():
                    abort(status=409, description='Already Exists.')

                movie_info[new_id] = params
                for p in params:
                    if p not in movie_data.keys():
                        raise KeyError
            except:
                abort(status=400, description='Bad parameters')
        else:
            abort(status=400, description='Missing Title or Year.')
        return Response(status=200)


@ns_movies.route("/<string:id>")
class movie_detail(Resource):
    def get(self, id):
        if id not in movie_info:
            abort(status=404, description=f"Movie '{id}' doesn't exists.")
        return movie_info.get(id)
    
    @api.expect(movie_info)
    def put(self, id):
        if id not in movie_info:
            abort(status=404, description=f"Movie '{id}' doesn't exists.")
        if not (params := request.get_json()):
            abort(status=400, description='No parameters')
        
        for p in params:
            if p not in movie_data.keys():
                abort(status=400, description='Bad parameters')
        for p in params:
            movie_info[id][p] = params[p]
        return Response(status=200)

    def delete(self, id):
        try:
            del movie_info[id]
        except KeyError:
            abort(status=404, description=f"Movie '{id}' doesn't exists.")
        return Response(status=200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
