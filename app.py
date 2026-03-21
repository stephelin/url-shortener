from flask import Flask, request, redirect

app = Flask(__name__)

url_map = {}

@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.json.get('url')
    short = str(len(url_map) + 1)
    url_map[short] = long_url
    return {"short_url": short}

@app.route('/<short>')
def redirect_url(short):
    return redirect(url_map.get(short, "/"))

if __name__ == '__main__':
    app.run(debug=True)
