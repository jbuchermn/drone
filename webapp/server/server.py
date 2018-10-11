import random
import http.client as httplib
from flask import Flask, render_template, request, Response

app = Flask(__name__, static_folder="../static/dist", template_folder="../static")

@app.route("/")
def index():
    return render_template("index.html", rand=random.randint(1, 100000))

@app.route("/janus", methods=["GET", "POST", "OPTIONS"])
@app.route("/janus/<path:p>", methods=["GET", "POST", "OPTIONS"])
def janus_proxy(p = ""):
    path = ""
    if request.query_string:
        path = "/janus/%s?%s" % (p, request.query_string)
    else:
        path = "/janus/" + p

    conn = httplib.HTTPConnection("localhost", 8088)
    conn.request(request.method, path, body=request.data, headers=dict(request.headers))
    resp = conn.getresponse()
    content = resp.read()

    return Response(response=content,
                    status=resp.status,
                    headers=dict(resp.headers),
                    content_type=resp.getheader('content-type'))

if __name__ == "__main__":
    # app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', ssl_context='adhoc')
