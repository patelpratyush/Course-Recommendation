from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from pdfminer.high_level import extract_text
import os
import database
import re


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
    username = extract_text_first_line(file_path)  # Adjusted to use function directly
    extracted_rows = extract_rows_below_keyword(file_path, 'Subject')  # Adjusted to use function directly
    
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

def extract_text_first_line(pdf_path):
    try:
        # Extract text from the PDF file
        with open(pdf_path, 'rb') as file:
            pdf_text = extract_text(file)

        # Split the text into lines
        lines = pdf_text.split('\n')
        print(lines) #testing code
        # Extract the text from the first line
        if lines:
            first_line_text = lines[12].strip()
            return first_line_text
        else:
            return None

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def extract_rows_below_keyword(pdf_path, keyword):
    try:
        # Define the words to exclude
        excluded_words = {'Main', 'List', 'Term', 'GPA', 'CEU', 'and', 'Type', 'End', 'Good', 'Fall', 'ted', 'Enac', 'The', 'New', 'Full', 'Web', 'Lin', 'Alg', 'Diff', 'Eqs', 'Data', 'Art', 'Lab', 'Heal', 'Eng', 'Age', 'with', 'TA-'}

        # Extract text from the PDF file
        with open(pdf_path, 'rb') as file:
            pdf_text = extract_text(file)

        # Split the text into lines
        lines = pdf_text.split('\n')

        word_pattern = r'\b[A-Z]{3,4}\b'

        # Search for the keyword
        rows = []
        keyword_found = False
        for line in lines:
            if keyword in line:
                keyword_found = True
                continue  # Skip the line with the keyword
            if keyword_found and line.strip():  # Check if keyword was found and the line is not empty
                # Split the line into words
                classes = re.findall(word_pattern, line)
                words = line.split()
                # Filter words based on length, exclusion list, and characters to exclude
                filtered_words = []
                for word in words:
                    if len(word) in (3, 4) and word.strip() not in excluded_words and not any(char in word for char in '/:.'):
                        if len(word) == 4 and word.isdigit():
                            continue
                        if word.isalpha() and not word.isupper():
                            continue
                        else:
                            filtered_words.append(word.strip())
                rows.extend(filtered_words)
                # print(filtered_words)

        return rows

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
