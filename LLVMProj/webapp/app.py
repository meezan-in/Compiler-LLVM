from flask import Flask, render_template, request, jsonify
import os
from webapp.enhanced_ir_diff import IRDiffTool

app = Flask(__name__)

# Configure upload folder for C++ files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the IRDiffTool
ir_diff_tool = IRDiffTool()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'cpp', 'cc', 'cxx'}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    ai_summary = None
    key_changes = None
    side_by_side_diff = None
    annotated_diff = None
    llvm_diff = None

    if request.method == 'POST':
        source_code = ""
        uploaded_file = None

        if 'cppFile' in request.files:
            uploaded_file = request.files['cppFile']
            if uploaded_file and allowed_file(uploaded_file.filename):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
                uploaded_file.save(filepath)
                with open(filepath, 'r') as f:
                    source_code = f.read()
            else:
                return jsonify({"success": False, "error": "Invalid file type."})
        else:
            source_code = request.form['source']
        
        opt_pass = request.form['opt_pass']

        try:
            # Generate IR and run optimization
            ir_diff_tool.run_clang(source_code, "before.ll")
            ir_diff_tool.run_opt(opt_pass, "before.ll", "after.ll")
            
            # Get various diff outputs
            side_by_side_diff = ir_diff_tool.generate_side_by_side_diff("before.ll", "after.ll")
            annotated_diff = ir_diff_tool.generate_annotated_diff("before.ll", "after.ll")
            llvm_diff = ir_diff_tool.run_llvm_diff("before.ll", "after.ll")

            # Generate AI summary
            ai_analysis = ir_diff_tool.generate_ai_summary("before.ll", "after.ll", opt_pass)
            ai_summary = ai_analysis['summary']
            key_changes = ai_analysis['key_changes']
            
            # Read raw output (after.ll content)
            with open("after.ll", "r") as f:
                result = f.read()

            # Clean up temp files
            os.remove("before.ll")
            os.remove("after.ll")

            # Render the template with results
            return render_template('index.html',
                                   result=result,
                                   side_by_side_diff=side_by_side_diff,
                                   annotated_diff=annotated_diff,
                                   llvm_diff=llvm_diff,
                                   ai_summary=ai_summary,
                                   key_changes=key_changes)

        except Exception as e:
            return render_template('index.html', error=str(e))

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
