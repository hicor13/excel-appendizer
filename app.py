import subprocess
import sys
import os

# --- AUTO-DEPENDENCY LOGIC ---
def install_dependencies():
    required_libraries = ['flask', 'pandas', 'openpyxl']
    for lib in required_libraries:
        try:
            __import__(lib)
        except ImportError:
            print(f"--- Dependency {lib} not found. Installing... ---")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# Run the installer before importing the libraries for the app
install_dependencies()

# Now it is safe to import them
import pandas as pd
from flask import Flask, render_template, request, send_file
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        val1 = request.form.get('col1_val')
        val2 = request.form.get('col2_val')

        if file and val1 and val2:
            # 1. Read Excel
            df = pd.read_excel(file)
            
            # 2. Append User Columns
            df['New_Column_A'] = val1
            df['New_Column_B'] = val2

            # 3. Rename first 4 headers
            new_headers = ["col_A", "col_B", "col_C", "col_D"]
            current_columns = list(df.columns)
            for i in range(min(4, len(current_columns))):
                current_columns[i] = new_headers[i]
            df.columns = current_columns

            # 4. Prepare CSV Download
            csv_data = df.to_csv(index=False)
            output = io.BytesIO(csv_data.encode('utf-8'))

            # 5. Dynamic Filename Logic
            safe_filename = "".join(c for c in val1 if c.isalnum() or c in " ._-").strip()
            if not safe_filename: safe_filename = "output"

            return send_file(
                output, 
                as_attachment=True, 
                download_name=f"{safe_filename}.csv",
                mimetype="text/csv"
            )

    return render_template('index.html')

if __name__ == '__main__':
    # The app will run on http://127.0.0.1:5000
    app.run(port=5000, debug=True)