from flask import Flask, render_template_string

app = Flask(__name__)

# 1. Main Home Page Route
@app.route('/')
def home():
    with open("college.html", "r", encoding="utf-8") as f:
        return f.read()

# 2. About Us Route (Opens when you click 'About us')
@app.route('/about')
def about():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>About Us - KMGGP</title>
        <style>
            body { font-family: 'Poppins', sans-serif; background: #f7fafc; margin: 50px; color: #2d3748; }
            .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); max-width: 600px; margin: 0 auto; }
            h1 { color: #2b6cb0; }
            a { display: inline-block; margin-top: 20px; color: #3182ce; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>About Our Institute</h1>
            <p>KM Mayawati Government Girls Polytechnic, Badalpur was established in 2002 to provide top-tier technical education for women.</p>
            <a href="/">← Back to Home</a>
        </div>
    </body>
    </html>
    """)

# 3. Courses Route (Opens when you click 'Courses')
@app.route('/courses')
def courses():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Courses - KMGGP</title>
        <style>
            body { font-family: 'Poppins', sans-serif; background: #f7fafc; margin: 50px; color: #2d3748; }
            .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); max-width: 600px; margin: 0 auto; }
            h1 { color: #2b6cb0; }
            li { margin: 10px 0; font-weight: bold; }
            a { display: inline-block; margin-top: 20px; color: #3182ce; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Departments Offered</h1>
            <ul>
                <li>💻 Computer Science and Engineering</li>
                <li>📡 Information Technology</li>
                <li>⚡ Electronics Engineering</li>
            </ul>
            <a href="/">← Back to Home</a>
        </div>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(port=8000, debug=True)
