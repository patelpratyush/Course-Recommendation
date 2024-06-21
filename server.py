from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os
import database

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            recommendations = process_transcript(file_path)
            return render_template('recommendations.html', recommendations=recommendations)

def process_transcript(file_path):
    username = appy.extract_text_first_line(file_path)
    extracted_rows = appy.extract_rows_below_keyword(file_path, 'Subject')
    
    if extracted_rows:
        subjects = []
        course_numbers = []
        
        for item in extracted_rows:
            if item.isalpha():
                subject = item
                subjects.append(subject)
            else:
                course_number = item
                course_numbers.append(course_number)
        
        combined_subject_course = [f"{subject} {course_number}" for subject, course_number in zip(subjects, course_numbers)]
        recommendations = database.recommendation(username)
        
        # Add user and courses to the database
        database.insert_user_and_courses(username, combined_subject_course)
        
        return recommendations
    else:
        return []

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
