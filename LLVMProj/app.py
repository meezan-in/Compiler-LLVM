from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        source_code = request.form.get("source", "")
        opt_pass = request.form.get("opt_pass", "mem2reg")
        return jsonify({
            "message": "Code received",
            "source": source_code,
            "pass": opt_pass
        })
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080) 