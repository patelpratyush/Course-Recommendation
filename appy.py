from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
import database
import re
import time

if __name__ == "__main__":
    def retry_click(element):
        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                element.click()
                break
            except StaleElementReferenceException:
                retries += 1

    def wait_for_requisites(driver):
        try:
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//strong[text()="Requisites and Restrictions"]')))
            WebDriverWait(driver, 1).until(EC.staleness_of(driver.find_element(By.XPATH, '//strong[text()="Requisites and Restrictions"]')))
        except:
            pass

    def get_subject_and_course_number(driver, list_subjects, list_course_numbers):
        while True:
            updated_reg_soup = BeautifulSoup(driver.page_source, 'lxml')
            reg_table = updated_reg_soup.find('table', id='table1')
            reg_tbody = reg_table.find('tbody')
            reg_tr = reg_tbody.find_all('tr')

            for tr in reg_tr:
                subject_td = tr.find('td', {'data-content': 'Subject'})
                course_num_td = tr.find('td', {'data-content': 'Course Number'})
                if subject_td and course_num_td:
                    list_subjects.append(subject_td.text.strip())
                    list_course_numbers.append(course_num_td.text.strip())

            next_button = driver.find_elements(By.CSS_SELECTOR, 'button[title="Next"]:not([disabled])')
            if next_button:
                next_button[0].click()
                time.sleep(3)
            else:
                break

    registrar = 'https://reg-prod.ec.ucmerced.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=search&_gl=1*tpyu75*_ga*Mjg4NjM1MDMwLjE2MTMwNzk1MDE.*_ga_TSE2LSBDQZ*MTcwNjg1NDcwOC44Mi4xLjE3MDY4NTQ4NTAuNjAuMC4w'
    driver3 = webdriver.Chrome()
    driver3.get(registrar)
    reg_soup = BeautifulSoup(driver3.page_source, 'lxml')

    reg_home = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="javascript:void(0)"]')))
    retry_click(reg_home)

    results_list = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.ID, "select2-results-1")))

    first_item = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.ID, "select2-result-label-2")))
    retry_click(first_item)

    continue_button = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.ID, "term-go")))
    retry_click(continue_button)

    subject_drop = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "select2-choices")))
    retry_click(subject_drop)
    cse_select = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.ID, "CSE")))
    retry_click(cse_select)

    WebDriverWait(driver3, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "form-end-controls")))

    search_button = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.ID, "search-go")))
    retry_click(search_button)

    page_size = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "page-size-select")))
    retry_click(page_size)
    size_select = Select(WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "page-size-select"))))
    size_select.select_by_value('50')

    time.sleep(3)

    updated_reg_soup = BeautifulSoup(driver3.page_source, 'lxml')

    WebDriverWait(driver3, 10).until(
        EC.presence_of_element_located((By.ID, "table1"))
    )

    term = updated_reg_soup.find('h4', class_='search-results-header').text.split(':')[1].strip()

    reg_table = updated_reg_soup.find('table', id='table1')
    reg_tbody = reg_table.find('tbody')
    reg_tr = reg_tbody.find_all('tr')

    courses = []
    course_num = []

    get_subject_and_course_number(driver3, courses, course_num)

    combined_courses = [f'{subject} {number}' for subject, number in zip(courses, course_num)]
    combined_courses = list(set(combined_courses))
    print(combined_courses)

def extract_rows_below_keyword(pdf_path, keyword):
    try:
        excluded_words = {'Main', 'List', 'Term', 'GPA', 'CEU', 'and', 'Type', 'End', 'Good', 'Fall', 'ted', 'Enac', 'The', 'New', 'Full', 'Web', 'Lin', 'Alg', 'Diff', 'Eqs', 'Data', 'Art', 'Lab', 'Heal', 'Eng', 'Age', 'with', 'TA-'}

        with open(pdf_path, 'rb') as file:
            pdf_text = extract_text(file)

        lines = pdf_text.split('\n')

        word_pattern = r'\b[A-Z]{3,4}\b'

        rows = []
        keyword_found = False
        for line in lines:
            if keyword in line:
                keyword_found = True
                continue
            if keyword_found and line.strip():
                classes = re.findall(word_pattern, line)
                words = line.split()
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

        return rows

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def extract_text_first_line(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_text = extract_text(file)

        lines = pdf_text.split('\n')
        print(lines)
        if lines:
            first_line_text = lines[12].strip()
            return first_line_text
        else:
            return None

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
