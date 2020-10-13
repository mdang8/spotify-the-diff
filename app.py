import os
from flask import Flask, jsonify, render_template
from src.server.lib import spotify_client
from src.server.lib import server_helper


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/playlists', methods=['POST'])
def playlists():
    """
    Route for returning user's playlist data. POST request body should contain the auth token and
    user id. The list of playlists objects returned only contains the relevant key-value pairs
    needed by the front-end.
    """

    playlists = spotify_client.get_user_playlists()
    formatted_playlists = server_helper.format_playlists(playlists)

    return jsonify(formatted_playlists)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 3000), debug=True)
