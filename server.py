from flask import Flask, render_template, url_for, redirect, request, send_from_directory, make_response, session, escape
import data_manager, util
import os
from bcrypt import checkpw, hashpw, gensalt


app = Flask(__name__)
app.secret_key = os.urandom(16)
app.config['UPLOAD_PATH'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # maksymalna wielkosc uploadowanego obrazu
headers = ["Title", "Message", "Submission Time", "Views", "Votes"]
story_keys = ["title", "message", "submission_time", "view_number", "vote_number"]

FORM_USERNAME = 'username'
FORM_PASSWORD = 'password'
SESSION_USERNAME = 'username'




def swap_image(uploaded_file):
    """function to use when user can upload file"""
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], uploaded_file.filename))
        return os.path.join(app.config['UPLOAD_PATH'], uploaded_file.filename)  # question['image'] = ...


@app.route("/")
def main_page():
    questions = data_manager.get_questions(5)
    response = make_response(render_template("index.html", username = SESSION_USERNAME, headers=headers, questions=questions, story_keys=story_keys))
    # return render_template("index.html", headers=headers, questions=questions, story_keys=story_keys)
    return response



@app.route("/list")
def question_page():
    questions = data_manager.get_questions(None)
    if len(request.args) != 0:
        questions = data_manager.get_questions_by_order(request.args.get("order_by"),
                                                        request.args.get("order_direction"))
    return render_template("question_list.html", headers=headers, questions=questions, story_keys=story_keys)


@app.route("/search")
def display_search_question():
    search_phrase = request.args.get("search")
    questions = data_manager.get_questions_by_phrase(search_phrase)
    answers = data_manager.get_answers_by_phrase(search_phrase)
    answers_test = {}
    if len(search_phrase) == 0:
        return redirect(url_for("main_page"))
    for answer in answers:
        if not answer["question_id"] in answers_test.keys():
            answers_test[answer["question_id"]] = [answer]
        else:
            answers_test[answer["question_id"]].append(answer)
        if not answer["question_id"] in [x["id"] for x in questions]:
            questions.append(data_manager.get_question_by_id(answer["question_id"]))

    return render_template("search_page.html", questions=questions, answers=answers_test, search_phrase=search_phrase)


@app.route("/uploads/<filename>")
def get_img(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


def get_filename(path):
    file_name = os.path.split(path)[1]
    return file_name


app.jinja_env.globals.update(get_filename=get_filename)


@app.route("/question/<question_id>")
def display_question(question_id):
    if request.referrer != request.url:
        data_manager.views_updated(question_id)

    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answers_by_question_id(question_id)
    question_comments = data_manager.get_comments_by_question_id(question_id)
    answer_comments = data_manager.get_answer_comments_by_question_id(question_id)
    answers_headers = ["Votes' number", "Answer", "Submission time"]
    comment_headers = ["Submission time", "Message", "Edition counter"]
    question_tag = data_manager.get_tag_by_question_id(question_id)
    # users = data_manager.get_all_users_basic_info()

    return render_template("question.html", question=question,
                           answers=answers,
                           answers_headers=answers_headers,
                           question_comments=question_comments,
                           comment_headers=comment_headers,
                           answer_comments=answer_comments,
                           question_tag=question_tag,
                           # users=users
                           )


@app.route("/add")
def add_question_get():
    new_question = {
        "id": None,
        "title": "",
        "message": "",
        "image": "",
        "submission_time": None,
        "view_number": 0,
        "vote_number": 0
    }
    return render_template("add_update_question.html", question=new_question)


@app.route("/add/post", methods=["POST"])
def add_question_post():
    new_question = dict(request.form)
    new_question['submission_time'] = util.get_current_date_time()
    new_question["view_number"] = 0
    new_question["vote_number"] = 0

    uploaded_file = request.files['file']
    new_question['image'] = swap_image(uploaded_file)

    question_id = data_manager.add_question(new_question).get('id')
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>/edit")
def edit_question_get(question_id):
    question = data_manager.get_question_by_id(question_id)
    if question is None:
        return redirect(url_for("display_question", question_id=question_id))
    else:
        return render_template("add_update_question.html", question=question)


@app.route("/question/<int:question_id>/edit/post", methods=["POST"])
def edit_question_post(question_id):
    edited_question = dict(request.form)

    uploaded_file = request.files['file']
    edited_question['image'] = swap_image(uploaded_file)

    data_manager.update_question(edited_question)

    return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<question_id>/delete")
def delete_question(question_id):

    answer_pictures_paths = data_manager.get_answer_pictures_paths(question_id)
    util.delete_all_images(answer_pictures_paths)

    question_pictures_paths = data_manager.get_question_pictures_paths(question_id)
    util.delete_all_images(question_pictures_paths)

    if data_manager.has_question_comment(question_id) is not None:
        data_manager.delete_comment_for_question(question_id)
    data_manager.delete_question_from_question_tag(question_id)

    data_manager.delete_comment_for_answers_for_question(question_id)
    data_manager.delete_answers_for_question(question_id)

    data_manager.delete_question(question_id)

    return redirect(url_for("question_page"))


@app.route("/question/<question_id>/new_answer")
def add_answer(question_id):

    question = data_manager.get_question_by_id(question_id)
    new_answer = \
        {
            "answer_id": None,
            "submission_time": None,
            "view_number": 0,
            "vote_number": 0,
            "id": None,
            "message": "",
            "image": ""
        }
    return render_template("answer.html", question=question, answer=new_answer)


@app.route("/question/<int:question_id>/new_answer/post", methods=["POST"])
def add_answer_post(question_id):

    new_answer = dict(request.form)
    new_answer["submission_time"] = util.get_current_date_time()
    new_answer["question_id"] = question_id
    new_answer["vote_number"] = 0

    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], uploaded_file.filename))
        new_answer["image"] = os.path.join(app.config['UPLOAD_PATH'], uploaded_file.filename)

    answer_id = data_manager.add_answer(new_answer).get('id')

    return redirect(url_for("display_question", question_id=question_id, answer_id=answer_id))


@app.route("/question/<int:question_id>/<int:answer_id>/edit-answer")
def edit_answer_get(question_id, answer_id):

    question = data_manager.get_question_by_id(question_id)

    answer = data_manager.get_answer_by_id(answer_id)

    if answer is None:
        return redirect(url_for("display_question", question_id=question_id))
    else:
        return render_template("add_update_answer.html", question=question, answer=answer)


@app.route("/question/<int:question_id>/<int:answer_id>/edit-answer", methods=["POST"])
def edit_answer_post(question_id, answer_id):

    edited_answer = dict(request.form)

    uploaded_file = request.files['file']
    edited_answer['image'] = swap_image(uploaded_file)

    data_manager.update_answer(answer_id, edited_answer)

    return redirect(url_for("display_question", question_id=question_id, answer_id=answer_id))


@app.route("/answer/<question_id>/<answer_id>/delete")
def delete_answer(question_id, answer_id):

    answer_pictures_paths = data_manager.get_answer_id_pictures_paths(answer_id)
    util.delete_all_images(answer_pictures_paths)

    if data_manager.has_answer_comment(answer_id) is not None:
        data_manager.delete_comment_for_answer(answer_id)

    data_manager.delete_answer_from_answers(answer_id)

    return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<question_id>/<forum_user>/vote_up", methods=["POST"])
def question_vote(question_id, forum_user):
    post_result = dict(request.form)["vote_question"]
    difference = util.get_difference_of_votes(post_result)
    data_manager.update_question_votes(question_id, difference)
    data_manager.gain_reputation_by_question("question", forum_user, post_result)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/answer/<question_id>/<answer_id>/<forum_user>/vote_up", methods=["POST"])
def answer_vote(question_id, answer_id, forum_user):
    post_result = dict(request.form)["vote_answer"]
    # print(post_result)
    difference = util.get_difference_of_votes(post_result)
    data_manager.update_answer_votes(answer_id, difference)
    data_manager.gain_reputation_by_question("answer", forum_user, post_result)
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/question/<question_id>/new-comment', methods=["GET", "POST"])
def new_question_comment(question_id):
    if request.method == "POST":
        details = dict(request.form)
        details["submission_time"] = util.get_current_date_time()
        # if 'email' in session:
        #     details["user_id"] = data_manager.get_user_id_by_mail(session["mail"])
        # teraz chwilowo dodany mail w formie stringa
        details["user_id"] = data_manager.get_user_id_by_mail("witam@gmail.com")
        data_manager.add_question_comment(details)

        return redirect(url_for("display_question", question_id=question_id))
    if request.method == "GET":
        question = data_manager.get_question_by_id(question_id)
        return render_template("add_comment.html",
                               item=question,
                               item_type="question",
                               url=url_for('new_question_comment', question_id=question_id))
                               # item_id = 'question_id')


@app.route('/comment/<comment_id>/edit', methods=["POST"])
def update_comment_post(comment_id):
    if request.method == "POST":
        details = dict(request.form)
        details["submission_time"] = util.get_current_date_time()

        data_manager.update_comment(details, comment_id)
        question_id = data_manager.get_question_id_by_comment_id(comment_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route('/comment/<comment_id>/edit', methods=["GET"])
def update_comment_get(comment_id):
    comment = data_manager.get_comment_by_id(comment_id)
    # question_id = data_manager.get_question_id_by_comment_id(comment_id)
    if comment.get("question_id") != None:
        question = data_manager.get_question_by_comment_id(comment_id)
        return render_template("update_comment.html",
                               comment=comment,
                               item=question,
                               item_type="question")
                               # url_forr = url_for('update_question_comment', question_id = question["id"]),
                               # url = 'update_comment_post')

    elif comment.get("answer_id") != None:
        answer = data_manager.get_answer_by_comment_id(comment_id)
        return render_template("update_comment.html",
                               comment=comment,
                               item=answer,
                               item_type="answer")
                               # url='update_comment_post')


@app.route('/comments/<comment_id>/delete')
def delete_comment(comment_id):
    question_id = data_manager.get_question_id_by_comment_id(comment_id)
    data_manager.delete_comment(comment_id)
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/answer/<answer_id>/new-comment', methods=["GET", "POST"])
def new_answer_comment(answer_id):
    if request.method == "POST":
        details = dict(request.form)
        details["submission_time"] = util.get_current_date_time()

        data_manager.add_answer_comment(details)
        question_id = data_manager.get_question_id_by_answer_id(answer_id)
        return redirect(url_for("display_question", question_id=question_id))

    if request.method == "GET":
        answer = data_manager.get_answer_by_id(answer_id)
        return render_template("add_comment.html",
                               item=answer,
                               item_type="answer",
                               url=url_for('new_answer_comment', answer_id=answer_id))
                               # item_id = 'answer_id')


@app.route('/question/<question_id>/new-tag', methods=["GET", "POST"])
def add_tag(question_id):
    print(request.form)
    if request.method == "POST":

        tag_name = dict(request.form)

        tag_id = data_manager.add_question_tag(tag_name).get('id')
        data_manager.add_question_tag_id(tag_id, question_id)

        return redirect(url_for("display_question", question_id=question_id, tag_id=tag_id))

    if request.method == "GET":
        possible_tags = []
        all_tags = data_manager.get_tag_to_list()
        tags_in_question = data_manager.get_tag_from_question(question_id)

        for tag in all_tags:
            if tag not in tags_in_question:
                possible_tags.append(tag)
        print(possible_tags)
        return render_template("add_tag.html", question_id=question_id, possible_tags=possible_tags)


@app.route('/question/<question_id>/old-tag', methods=["POST"])
def add_old_tag(question_id):

    tag_name = dict(request.form)
    tag_old_id = data_manager.get_tag_id_by_name(tag_name['tag_name']).get('id')
    data_manager.add_question_tag_id(tag_old_id, question_id)

    return redirect(url_for("display_question", question_id=question_id))


@app.route('/tags/<tag_id>/delete')
def delete_tag(tag_id):
    question_id = data_manager.get_question_id_by_tag_id(tag_id)
    data_manager.delete_tag(tag_id)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/tags")
def tags_page():
    tags = data_manager.get_tag_to_list()

    return render_template("tag_list.html", tag_headers=tag_headers, tags=tags, story_keys=story_keys)


@app.route('/registration/<ver>')
@app.route('/registration')
def registration_user(ver=None):
    return render_template("registration.html", ver=ver)


@app.route('/registration/post', methods=["POST"])
def registration_user_post():
    email = dict(request.form)
    email['email'] = email['email'].lower()
    if data_manager.check_for_user(email):
        return redirect(url_for("registration_user", ver="exist"))
    else:
        email['submission_time'] = util.get_current_date_time()
        data_manager.add_new_user(email)
    return redirect(url_for("main_page"))


@app.route('/users', methods=["GET"])
def display_users():
    # if 'user_id' in session:
    #     table_headers = ["ID", "User name", "Reputation", "Registration date",
    #                      "Added question", "Added answers", "Added comments"]

    # table_headers = ["ID", "User name", "Reputation", "Registration date",
    #                  "Added question", "Added answers", "Added comments"]
    if session.get(FORM_USERNAME):
        all_users = data_manager.get_all_users()
        return render_template('users.html', users=all_users)
    else:
        return redirect(url_for('login_user'))


@app.route('/user/<user_id>')
def display_user(user_id):

    if session.get(FORM_USERNAME):
        user = data_manager.get_user_details(user_id)
        activities = data_manager.get_dict_user_activities(user_id)
        return render_template('user.html', user=user, activities=activities)
    else:
        return redirect(url_for('login_user'))


@app.route('/login/<ver>')
@app.route('/login')
def login_user(ver=None):
    response = make_response(render_template('login.html', ver = ver, username = FORM_USERNAME, password = FORM_PASSWORD))
    return response

@app.route('/login/post', methods=['POST'])
def login_user_post():
    email = request.form[FORM_USERNAME]
    pwd = request.form[FORM_PASSWORD]

    check_email = data_manager.validate_login(email, pwd)
    if check_email:
        session[SESSION_USERNAME] = email
        user_id = data_manager.get_user_id_by_mail(email)
        session['user_id'] = user_id
        return redirect(url_for('main_page'))
    else:
        return redirect(url_for('login_user', ver="bad"))

@app.route('/logout/')
def logout():
    session.pop(SESSION_USERNAME)
    return redirect(url_for('main_page'))

if __name__ == "__main__":
    app.run()





tag_headers = ["Tag name", "number of question"]