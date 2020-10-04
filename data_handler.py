import datetime
import connection
import os

'''function that gets an item from list of dictionary, id ->string type'''
def get_item_by_id(items,id):
    for item in items:
        if item["id"] == id:
            return item

    return None


'''prepare a question for displaying: time format -> db'''
def prepare_question_for_display(question_id):
    all_questions = connection.read_csv("sample_data/question.csv")
    question = get_item_by_id(all_questions, question_id)
    # question["submission_time"] = transform_timestamp(question["submission_time"])

    return question


'''function that gets all answers for a given question  -> db'''
def get_answers_for_question(answers,question_id):
    all_answers = []
    for answer in answers:
        if answer["question_id"] == question_id:
            all_answers.append(answer)

    return all_answers


'''prepare answers for displaying: time format -> db'''
def prepare_answers_for_display(question_id):
    all_answers = connection.read_csv("sample_data/answer.csv")
    answers = get_answers_for_question(all_answers, question_id)
    # for answer in answers:
        # czy to nie spowoduje komplikacji przy zapisywaniu do pliku csv?
        # chyba nie powinno, bo updateować bedziemy tylko te pozycje, które się zmieniają,
        # a submission_time nie będzie edytowalne. Druga opcja taka, że
        #  znowu trzeba  będzie użyć datetime, żeby wygenerować timestamp do zapisu do csv
        # answer["submission_time"] = transform_timestamp(answer["submission_time"])
    return answers


'''function that deletes a given item from a list of dictionaries'''
def delete_item_from_items(items, item_id):
    for item in items:
        if item["id"] == item_id:
            items.remove(item)
            return items


'''delete answer for a given question from answers  -> db'''
def delete_answer_from_answers(question_id, answer_id):
     all_answers = connection.read_csv("sample_data/answer.csv")
     for answer in all_answers:
        if answer["question_id"] == question_id and answer["id"] == answer_id:
                if answer.get("image") != None:
                    if os.path.exists(answer["image"]):
                        os.remove(answer["image"])
                all_answers.remove(answer)
                return all_answers

''' -> '''
def delete_all_answers_for_question(question_id):
    all_answers = connection.read_csv("sample_data/answer.csv")
    updated_answers = []
    for answer in all_answers:
        if answer["question_id"] == question_id:
            if answer.get("image") != None:
                if os.path.exists(answer["image"]):
                    os.remove(answer["image"])
        else:
            updated_answers.append(answer)

    return updated_answers


'''function that adds vote up'''
def add_vote_up(items,item_id,down=None):
    for item in items:
        if item["id"] == item_id:
            # if down:
            #     item["vote_number"] = item.get("vote_number", 0) - 1
            # else:
            item["vote_number"] = int(item.get("vote_number", 0))+1
            return items


'''function that substract vote'''
def substract_vote(items,item_id):
    for item in items:
        if item["id"] == item_id:
            item["vote_number"] = int(item.get("vote_number", 0)) - 1
            return items


'''function that finds next number for id'''
def get_new_id(questions):
    tmp_id = 0
    for question in questions:
        if int(question['id']) > tmp_id:
            tmp_id = int(question['id'])

    return tmp_id + 1

#def get_new_id_answer(answers):
#    tmp_id = 0
#    for answer in answers:
#        if int(answer['id']) > tmp_id:
#            tmp_id = int(answer['id'])

#    return tmp_id + 1
# '''function that adds new question to list of questions'''
# def add_question(new_question,questions):
#     # questions = read_csv("sample_data/question.csv")
#     new_questions_list = questions.append(new_question)
#     return new_questions_list


'''function that updates question'''
def update_question(edited_question):
    questions = connection.read_csv("sample_data/question.csv")
    for question in questions:
        if question["id"] == edited_question["id"]:
            question["title"] = edited_question["title"]
            question["message"] = edited_question["message"]
            question["image"] = edited_question["image"]

    return questions


'''function that returns current data & time'''
def get_current_timestamp():
    now = datetime.datetime.now()
    return int(datetime.datetime.timestamp(now))

'''function that returns current data & time'''
def get_current_date_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

'''upadtes answers votes  -> db'''
def update_votes(items,item_id,post_result):
    for item in items:
        if item["id"] == item_id:
            if post_result["vote_answer"] == "vote_down":
                item["vote_number"] = int(item.get("vote_number", 0)) - 1
            elif post_result["vote_answer"] == "vote_up":
                item["vote_number"] = int(item.get("vote_number", 0)) +1
            return items


def views_updated(item_id):
    question_list = connection.read_csv("sample_data/question.csv")
    for question in question_list:
        if question["id"] == item_id:
            question["view_number"] = int(question["view_number"]) + 1
            break
    connection.write_csv("sample_data/question.csv", question_list)


def sorting_questions(questions_list, order_by, order_direction):
    if questions_list[0][order_by].isdigit():
        sorted_questions = sorted(questions_list, key=lambda k: int(k[order_by]))
    else:
        sorted_questions = sorted(questions_list, key=lambda k: k[order_by].lower(), )
    if order_direction == "desc":
        sorted_questions.reverse()
    return sorted_questions


'''switch timestamp to a nice date string'''
def transform_timestamp(timestamp):
    date_time = datetime.datetime.fromtimestamp(int(timestamp))
    time_formatted = date_time.strftime('%d-%b-%Y (%H:%M:%S)')

    return time_formatted


def delete_img(item_id):   # nie działą
    item = prepare_question_for_display(item_id)
    path = item.get('image')
    # file_path = os.path.join(app.config['UPLOAD_PATH'], file_path)  jeśli jest znana tylko nazwa pliku
    if os.path.exists(path):
        os.remove(path)
    else:
        return  # jak tu zrobić informację (osobny route?) czy raise exept i z server.py przekierowac gdzies?


if __name__ == "__main__":
    s = connection.read_csv("sample_data/question.csv")
    print(s)
    d = sorting_questions(s, "title", "view_number")
    print(d)
