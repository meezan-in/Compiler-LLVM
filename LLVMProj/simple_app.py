from flask import Flask, render_template, request, jsonify
import os
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            source_code = request.form.get("source", "")
            opt_pass = request.form.get("opt_pass", "mem2reg")
            
            # Write source code to temporary file
            with open("temp.cpp", "w") as f:
                f.write(source_code)
            
            # Run clang
            clang_cmd = ["clang++", "-S", "-emit-llvm", "temp.cpp", "-o", "before.ll"]
            clang_result = subprocess.run(clang_cmd, capture_output=True, text=True)
            
            if clang_result.returncode != 0:
                raise Exception(f"Clang failed: {clang_result.stderr}")
            
            # Run opt
            opt_cmd = ["opt", "-S", f"-passes={opt_pass}", "before.ll", "-o", "after.ll"]
            opt_result = subprocess.run(opt_cmd, capture_output=True, text=True)
            
            if opt_result.returncode != 0:
                raise Exception(f"Opt failed: {opt_result.stderr}")
            
            # Read the results
            with open("before.ll") as f1, open("after.ll") as f2:
                before = f1.read()
                after = f2.read()
            
            # Clean up
            os.remove("temp.cpp")
            os.remove("before.ll")
            os.remove("after.ll")
            
            return jsonify({
                "success": True,
                "before": before,
                "after": after
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LLVM Pass Visualizer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            textarea {
                width: 100%;
                height: 200px;
                margin: 10px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: monospace;
            }
            select {
                width: 100%;
                padding: 8px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
            }
            button:hover {
                background-color: #45a049;
            }
            #result {
                margin-top: 20px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f8f8;
                white-space: pre-wrap;
                font-family: monospace;
                display: none;
            }
            .error {
                color: red;
                margin-top: 10px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LLVM Pass Visualizer</h1>
            <form id="optimizationForm">
                <div>
                    <label for="source">C++ Code:</label>
                    <textarea id="source" name="source" placeholder="Enter your C++ code here...">int main() {
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        sum += i;
    }
    return sum;
}</textarea>
                </div>
                <div>
                    <label for="opt_pass">Optimization Pass:</label>
                    <select id="opt_pass" name="opt_pass">
                        <option value="mem2reg">Memory to Register (mem2reg)</option>
                        <option value="loop-unroll">Loop Unrolling</option>
                        <option value="simplifycfg">Control Flow Simplification</option>
                    </select>
                </div>
                <button type="submit">Run Optimization Pass</button>
            </form>
            <div id="result"></div>
            <div id="error" class="error"></div>
        </div>

        <script>
            document.getElementById('optimizationForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const resultDiv = document.getElementById('result');
                const errorDiv = document.getElementById('error');
                resultDiv.style.display = 'none';
                errorDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: new URLSearchParams(new FormData(e.target))
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        resultDiv.innerHTML = '<h3>Before Optimization:</h3><pre>' + data.before + '</pre><h3>After Optimization:</h3><pre>' + data.after + '</pre>';
                        resultDiv.style.display = 'block';
                    } else {
                        errorDiv.textContent = data.error;
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'Error: ' + error.message;
                    errorDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080) 