import os
from flask import Flask, jsonify, render_template, request
from src.server.lib.spotify_client import SpotifyClient
from src.server.lib import server_helper


app = Flask(__name__)
client = SpotifyClient()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/public/playlists', methods=['POST'])
def public_playlists():
    """
    Route for returning a user's public playlist data. The POST request body should contain the
    user id. The list of playlist objects returned only contains the relevant key-value pairs
    needed by the front-end.

    Example request body (application/json):
        {
            "user-id": "wizzler"
        }
    """

    req_data = request.get_json()
    res_data = {'data': None}
    status_code = 0

    if 'user-id' not in req_data:
        res_data['data'] = 'Error: request body missing a user ID.'
        status_code = 400
        return jsonify(res_data), status_code

    playlists = client.get_user_playlists(req_data['user-id'])
    playlists = client.extract_items_from_paging_obj(playlists, [])

    try:
        res_data['data'] = server_helper.format_playlists(playlists)
        status_code = 200
    except:
        res_data['data'] = 'Error: there was a problem formatting the data.'
        status_code = 500
    finally:
        return jsonify(res_data), status_code


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 3000), debug=True)
