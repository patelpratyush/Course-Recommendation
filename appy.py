from hmac import trans_36
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select
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
            except StaleElementReferenceException: #if nothing happens
                retries += 1

    def wait_for_requisites(driver):
        try:
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//strong[text()="Requisites and Restrictions"]')))
            WebDriverWait(driver, 1).until(EC.staleness_of(driver.find_element(By.XPATH, '//strong[text()="Requisites and Restrictions"]'))) #wait till element is stable and not changing
        except:
            pass

    # website1 = 'https://catalog.ucmerced.edu/preview_program.php?catoid=22&poid=2703&returnto=2226'

    # driver = webdriver.Chrome()
    # driver.get(website1)
    # driver.implicitly_wait(5)
    # # updated_page = driver.page_source
    # # result = requests.get(website1)
    # # content = result.text 

    # soup = BeautifulSoup(driver.page_source, 'lxml') 
    # # print(soup.prettify())
    # core_boxes = soup.find_all('div', class_='acalog-core')

    # course_codes = []
    # course_titles = []

    # for core_box in core_boxes:
    #     if core_box.find(re.compile(r"h2|h3")).text == 'Transfer Students':
    #         continue
    #     course_boxes = core_box.find_all('li', class_='acalog-course')
    #     for course_box in course_boxes:
    #         course_name_tag = course_box.find('a')

    #         if course_name_tag:
    #             full_course_name = course_name_tag.text
    #             course_code, course_title = full_course_name.split(":", 1)

    #             course_codes.append(course_code)  # Add course code to the list
    #             course_titles.append(course_title.strip())  # Add course title to the list

    # print(course_codes)
    # print(course_titles)

    # elements = driver.find_elements(By.XPATH, '//a[contains(@onclick, "showCourse")]')
    # course_reqs = []
    # for element in elements: 
    #     retry_click(element)
    #     wait_for_requisites(driver)
    # # driver.implicitly_wait(5)
    # # updated_page_after_click = driver.page_source 
    # click_soup = BeautifulSoup(driver.page_source, 'lxml')

    # req_core_boxes = click_soup.find_all('div', class_='acalog-core')

    # for req_core_box in req_core_boxes:
    #     if req_core_box.find(re.compile(r"h2|h3")).text == 'Transfer Students':
    #         continue
    #     reqs = req_core_box.find_all('strong', string='Requisites and Restrictions')
    #     for req in reqs:
    #         prereqs = []
    #         next_sibling = req.find_next_sibling('br')
    #         if next_sibling and 'Prerequisite Courses:' in next_sibling.next_sibling:
    #             prereq_string = next_sibling.next_sibling.strip()

    #             prereq_string = prereq_string.split(":", 1)[1].strip() #get the second half of the text
    #             prereq_string = prereq_string.replace("(", "")
    #             prereq_string = prereq_string.replace(")", "")

    #             for prereq in re.split(r"and|or", prereq_string):
    #                 if prereq is not None:
    #                     prereq = prereq.strip("()")
    #                     prereq = prereq.strip()
    #                 if prereq and prereq != 'equivalent exam' and len(prereq) <= 9:
    #                     prereqs.append(prereq)
                
    #             course_reqs.append(prereqs)
    #         else:
    #             course_reqs.append(['None'])
            

    # print(course_reqs)

    # #ADD COURSE AND PREREQ
    # # for course_code, course_title, prerequisite in zip(course_codes, course_titles, course_reqs):
    # #     for prereq in prerequisite:
    # #         if not database.course_exists(prereq) and len(prereq) <= 9 and prereq!='None':
    # #             database.add_course(prereq, '')

    # # for course_code, course_title, prerequisite in zip(course_codes, course_titles, course_reqs):
    # #     if not database.course_exists(course_code):
    # #         database.add_course(course_code, course_title)
    # #         database.add_prerequisites(prerequisite, course_code)
    # #     else:
    # #         if not database.has_prerequisite(course_code):
    # #             database.add_prerequisites(prerequisite, course_code)

    # #CSE WEBSITE
    # cse_website = 'https://catalog.ucmerced.edu/content.php?filter%5B27%5D=CSE&filter%5B29%5D=&filter%5Bkeyword%5D=&filter%5B32%5D=1&filter%5Bcpage%5D=1&cur_cat_oid=22&expand=&navoid=2224&search_database=Filter#acalog_template_course_filter'

    # driver2 = webdriver.Chrome()
    # driver2.get(cse_website)
    # # driver.implicitly_wait(5)
    # # updated_cse_page = driver2.page_source

    # cse_soup = BeautifulSoup(driver2.page_source, 'lxml')

    # cse_course_codes = []
    # cse_course_titles = []
    # cse_core_boxes = cse_soup.find_all('a', href=re.compile(r'^preview_course')) #^ means start of href is preview course
    # for cse_core_box in cse_core_boxes:
    #     full_cse_course_name = cse_core_box.text
    #     cse_course_code, cse_course_title = full_cse_course_name.split(":", 1)

    #     cse_course_codes.append(cse_course_code)
    #     cse_course_titles.append(cse_course_title.strip())

    # print(cse_course_codes)
    # print(cse_course_titles)


    # cse_elements = driver2.find_elements(By.XPATH, '//a[contains(@onclick, "showCourse")]')
    # for cse_element in cse_elements:
    #     retry_click(cse_element)
    #     wait_for_requisites(driver2)
    # # driver2.implicitly_wait(5)
    # # updated_cse_page_after_click = driver2.page_source
    #     click_cse_soup = BeautifulSoup(driver2.page_source, 'lxml')

    #     cse_reqs = click_cse_soup.find_all('strong', string='Requisites and Restrictions')

    #     cse_course_reqs = []
    #     for cse_req in cse_reqs:
    #         cse_prereqs = []
    #         next_cse_sibling = cse_req.find_next_sibling('br')
    #         if next_cse_sibling and 'Prerequisite Courses:' in next_cse_sibling.next_sibling:
    #             cse_prereq_string = next_cse_sibling.next_sibling.strip()

    #             cse_prereq_string = cse_prereq_string.split(":", 1)[1].strip() #get the second half of the text
    #             cse_prereq_string = cse_prereq_string.strip("()")

    #             for cse_prereq in re.split(r"and|or", cse_prereq_string):
    #                 if cse_prereq is not None:
    #                     cse_prereq = cse_prereq.strip("()")
    #                     cse_prereq = cse_prereq.strip()
    #                 if cse_prereq and cse_prereq != 'equivalent exam' and len(cse_prereq) <= 9:
    #                     cse_prereqs.append(cse_prereq)
                
    #             cse_course_reqs.append(cse_prereqs)
    #         else:
    #             cse_course_reqs.append(['None'])
            

    # print(cse_course_reqs)

    # # ADD COURSE AND PREREQ
    # # for cse_course_code, cse_course_title, cse_prerequisite in zip(cse_course_codes, cse_course_titles, cse_course_reqs):
    # #     for prereq in cse_prerequisite:
    # #         if not database.course_exists(prereq) and len(prereq) <= 9 and prereq!='None':
    # #             database.add_course(prereq, '')

    # # for cse_course_code, cse_course_title, cse_prerequisite in zip(cse_course_codes, cse_course_titles, cse_course_reqs):
    # #     if not database.course_exists(cse_course_code):
    # #         database.add_course(cse_course_code, cse_course_title)
    # #         database.add_prerequisites(cse_prerequisite, cse_course_code)
    # #     else:
    # #         if not database.has_prerequisite(cse_course_code):
    # #             database.add_prerequisites(cse_prerequisite, cse_course_code) 


    #REGISTRAR CODE
    def get_subject_and_course_number(driver, list_subjects, list_course_numbers):
        while True:
            # Find all tr tags within the tbody
            updated_reg_soup = BeautifulSoup(driver.page_source, 'lxml')
            reg_table = updated_reg_soup.find('table', id='table1')
            reg_tbody = reg_table.find('tbody')
            reg_tr = reg_tbody.find_all('tr')
            
            # Extract subject and course number
            for tr in reg_tr:
                subject_td = tr.find('td', {'data-content': 'Subject'})
                course_num_td = tr.find('td', {'data-content': 'Course Number'})
                if subject_td and course_num_td:
                    list_subjects.append(subject_td.text.strip())
                    list_course_numbers.append(course_num_td.text.strip())

            # Check if the "Next" button is enabled
            next_button = driver.find_elements(By.CSS_SELECTOR, 'button[title="Next"]:not([disabled])')
            if next_button:
                # Click on the "Next" button
                next_button[0].click()  # Assuming only one "Next" button exists
                time.sleep(3)  # Wait for the page to load
            else:
                break  # Break the loop if the "Next" button is disabled

    registrar = 'https://reg-prod.ec.ucmerced.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=search&_gl=1*tpyu75*_ga*Mjg4NjM1MDMwLjE2MTMwNzk1MDE.*_ga_TSE2LSBDQZ*MTcwNjg1NDcwOC44Mi4xLjE3MDY4NTQ4NTAuNjAuMC4w'
    driver3 = webdriver.Chrome()
    driver3.get(registrar)
    reg_soup = BeautifulSoup(driver3.page_source, 'lxml')

    # Open dropdown
    reg_home = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="javascript:void(0)"]')))
    retry_click(reg_home)

    # Wait for dropdown items to appear
    results_list = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.ID, "select2-results-1")))

    # Click the first item in the dropdown
    first_item =  WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.ID, "select2-result-label-2")))
    retry_click(first_item)

    # Click on continue 
    continue_button = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.ID, "term-go")))  
    retry_click(continue_button)

    #TEMP CSE TRIAL
    subject_drop = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "select2-choices")))
    retry_click(subject_drop)
    cse_select = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.ID, "CSE")))
    retry_click(cse_select)
    #TEMP CSE TRIAL

    #click search
    WebDriverWait(driver3, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "form-end-controls")))  # Ensure button is present

    # Click search button
    search_button = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.ID, "search-go")))
    retry_click(search_button)

    #Click page size
    page_size = WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "page-size-select")))
    retry_click(page_size)
    #Use selenium's module for select tag specific funciton
    size_select = Select(WebDriverWait(driver3, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "page-size-select"))))
    size_select.select_by_value('50')

    time.sleep(3) #HAD TO ADD THIS IN ORDER FOR SCRIPT TO FIND THE TAGS

    updated_reg_soup = BeautifulSoup(driver3.page_source, 'lxml')




    WebDriverWait(driver3, 10).until(
        EC.presence_of_element_located((By.ID, "table1"))
    )

    term = updated_reg_soup.find('h4', class_='search-results-header').text.split(':')[1].strip()

    # print(updated_reg_soup.prettify())
    reg_table = updated_reg_soup.find('table', id='table1')
    reg_tbody = reg_table.find('tbody')
    reg_tr = reg_tbody.find_all('tr')


    courses = []
    course_num = []




    get_subject_and_course_number(driver3, courses, course_num)


    # print(courses)
    # print(course_num)
    combined_courses = [f'{subject} {number}' for subject, number in zip(courses, course_num)]
    combined_courses = list(set(combined_courses))
    print(combined_courses)

    # database.add_schedule(combined_courses)
    #END REGISTRAR CODE

# TRANSCRIPT PARSE CODE
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

# #unofficial transcript needs to be downloaded from using the print from the website
# pdfPath = '/Users/JustinLy/Desktop/Independen Study/CSE Course Database/Emily Le Print from website.pdf'
# keyword = 'Subject'  
# extracted_rows = extract_rows_below_keyword(pdfPath, keyword)
# username = extract_text_first_line(pdfPath)
# print(username) 
# # print(extracted_rows)

# if extracted_rows:
#     subjects = []
#     course_numbers = []

#     # Initialize a set to keep track of used integers
#     used_integers = set()

#     for item in extracted_rows:
#         if item.isalpha():
#             subject = item
#             subjects.append(subject)
#         else:
#             course_number = item
#             course_numbers.append(course_number)

#     # Combine the subjects and course numbers into a single list
#     combined_subject_course = [f"{subject} {course_number}" for subject, course_number in zip(subjects, course_numbers)]

#     for subject_course in combined_subject_course:
#         print(subject_course)
# else:
#     print("Keyword not found or error occurred.")

# # database.insert_user_and_courses(username, combined_subject_course)

# recommendations = database.recommendation('Bob')
# for course_id, course_code, course_title in recommendations:
#     print(f"{course_code}: {course_title}")


# database.add_course_for_user('Bob', 'CSE 005')
