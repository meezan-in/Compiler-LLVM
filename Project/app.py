from flask import Flask, request, render_template, redirect, url_for
import os
import subprocess
import difflib
from flask import send_from_directory

app = Flask(__name__)


UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            source_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(source_path)

            before_ll = os.path.join(GENERATED_FOLDER, "before.ll")
            after_ll = os.path.join(GENERATED_FOLDER, "after.ll")
            diff_path = os.path.join(GENERATED_FOLDER, "diff_output.txt")

            subprocess.run(["clang", "-S", "-emit-llvm", source_path, "-o", before_ll], check=True)
            subprocess.run(["opt", "-O2", before_ll, "-S", "-o", after_ll], check=True)

            # Generate unified diff
            with open(before_ll) as f1, open(after_ll) as f2:
                before = f1.readlines()
                after = f2.readlines()
            diff = difflib.unified_diff(before, after, fromfile="before.ll", tofile="after.ll")

            with open(diff_path, "w") as f:
                f.writelines(diff)

            return redirect(url_for("view_diff"))

    return render_template("index.html")

@app.route("/diff")
def view_diff():
    return render_template("diff.html")
@app.route('/generated/<path:filename>')
def serve_generated_file(filename):
    return send_from_directory(app.config['GENERATED_FOLDER'], filename)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(GENERATED_FOLDER, exist_ok=True)
    app.run(debug=True)
