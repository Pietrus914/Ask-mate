from typing import List, Dict

from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import datetime
import database_common


@database_common.connection_handler
def get_questions(cursor: RealDictCursor, limit: (None, int)) -> list:  # all questions: limit is None
    if limit is None:
        query = f"""
                SELECT *
                FROM question
                """
    else:
        query = f"""
                SELECT *
                FROM question
                ORDER BY submission_time DESC
                LIMIT {limit}
                """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_questions_by_order(cursor: RealDictCursor, order: str, direct: str):
    query = f"""
            SELECT *
            FROM question
            ORDER BY {order} {direct}
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_questions_by_phrase(cursor: RealDictCursor, phrase: str) -> list:
    query = f"""
                SELECT *
                FROM question
                WHERE LOWER(title) LIKE LOWER('%{phrase}%') or LOWER(message) LIKE LOWER('%{phrase}%')
                """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_phrase(cursor: RealDictCursor, phrase: str) -> list:
    query = f"""
                SELECT *
                FROM answer
                WHERE LOWER(message) LIKE LOWER('%{phrase}%')
                """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_question_by_id(cursor: RealDictCursor, question_id: int) -> list:
    query = f"""
        SELECT *
        FROM question
        WHERE id = {question_id}
        """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_answers_by_question_id(cursor: RealDictCursor, question_id: int) -> list:
    query = f"""
        SELECT *
        FROM answer
        WHERE question_id = {question_id}
        ORDER BY submission_time DESC
        """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_question(cursor: RealDictCursor, new_question: dict) -> dict:
    query = f"""
        INSERT INTO question (title, message, image, submission_time, view_number, vote_number)
        VALUES (%(title)s, %(message)s, %(image)s, %(submission_time)s, %(view_number)s, %(vote_number)s)
        RETURNING id
        """
    cursor.execute(query, new_question)
    return cursor.fetchone()


@database_common.connection_handler
def update_question(cursor: RealDictCursor, edited_question: dict):
    query = f"""
        UPDATE question 
        SET title = %(title)s, message = %(message)s, image = %(image)s
        WHERE id = %(id)s
        """
    cursor.execute(query, edited_question)


@database_common.connection_handler
def update_question_votes(cursor:RealDictCursor, question_id, difference: int):
    query = f"""
        UPDATE question
        SET vote_number = vote_number + {difference}
        WHERE id = {question_id}"""
    cursor.execute(query)
    return


@database_common.connection_handler
def views_updated(cursor: RealDictCursor, question_id: int):
    query= f"""
        UPDATE question
        SET view_number = view_number + 1
        WHERE id = {question_id}"""
    cursor.execute(query)

    return


@database_common.connection_handler
def delete_answers_for_question(cursor: RealDictCursor, question_id: int):
    query = f"""
        DELETE from answer
        WHERE question_id = {question_id}"""
    cursor.execute(query)
    return

@database_common.connection_handler
def delete_comment_for_question(cursor: RealDictCursor, question_id: int):
    query = f"""
            DELETE from comment
            WHERE question_id = {question_id}"""
    cursor.execute(query)
    return


@database_common.connection_handler
def delete_comment_for_answers_for_question(cursor: RealDictCursor, question_id: int):
    query = f"""
        DELETE from comment
        WHERE answer_id IN (
        SELECT id 
        FROM answer 
        WHERE question_id = {question_id})"""
    cursor.execute(query)
    return


@database_common.connection_handler
def delete_question_from_question_tag(cursor: RealDictCursor, question_id: int):
    query = f"""
            DELETE from question_tag
            WHERE question_id = {question_id}"""
    cursor.execute(query)
    return

@database_common.connection_handler
def has_question_comment(cursor: RealDictCursor, question_id: int):
    query = f"""
        SELECT id
        FROM comment 
        WHERE question_id = {question_id}"""
    cursor.execute(query)
    return cursor.fetchone()



@database_common.connection_handler
def has_answer_comment(cursor: RealDictCursor, answer_id: int):
    query = f"""
        SELECT id
        FROM comment 
        WHERE answer_id = {answer_id}"""
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def delete_comment_for_answer(cursor: RealDictCursor, answer_id: int):
    query = f"""
        DELETE from comment
        WHERE answer_id = {answer_id}"""
    cursor.execute(query)

@database_common.connection_handler
def delete_answer_from_answers(cursor: RealDictCursor, answer_id: int):
    query = f"""
        DELETE from answer
        WHERE id = {answer_id}"""
    cursor.execute(query)

    return


@database_common.connection_handler
def update_answer_votes(cursor: RealDictCursor, answer_id: int, difference: int):
    query = f"""
        UPDATE answer
        SET vote_number = vote_number + {difference}
        WHERE id = {answer_id}"""
    cursor.execute(query)
    return


@database_common.connection_handler
def get_answer_pictures_paths(cursor: RealDictCursor, question_id: int):
    query = f"""
        SELECT image
        FROM answer
        WHERE question_id = {question_id}"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_id_pictures_paths(cursor: RealDictCursor, answer_id):
    query = f"""
            SELECT image
            FROM answer
            WHERE id = {answer_id}"""
    cursor.execute(query)
    return cursor.fetchall()



@database_common.connection_handler
def get_question_pictures_paths(cursor: RealDictCursor, question_id: int):
    query = f"""
        SELECT image 
        FROM question
        WHERE id = {question_id}"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def delete_question(cursor: RealDictCursor, question_id: int):
    query = f"""
            DELETE from question
            WHERE id = {question_id}"""
    cursor.execute(query)
    return


@database_common.connection_handler
def get_comment_by_id(cursor: RealDictCursor, comment_id: int):
    query = f"""
                SELECT * from comment
                WHERE id = {comment_id}"""
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
# def add_question_comment(cursor: RealDictCursor, details: dict, fk_id, column: str):
#     query = f"""
#         INSERT INTO comment ({column}, message, submission_time)
#         VALUES ({fk_id}, {details["comment_message"]}, '{details["submission_time"]}' )
#         """
def add_question_comment(cursor: RealDictCursor, details: dict):
    query = f"""
        INSERT INTO comment (question_id, message, submission_time)
        VALUES ({details["question_id"]}, '{details["comment_message"]}', '{details["submission_time"]}' )
        """
    cursor.execute(query)
    return


@database_common.connection_handler
def update_comment(cursor: RealDictCursor, details: dict, comment_id):
    query = f"""
            UPDATE comment 
            SET message = '{details["comment_message"]}', 
                submission_time = '{details["submission_time"]}',
                edited_count = CASE 
                    WHEN edited_count IS NULL  THEN 1
                    ELSE edited_count + 1
                END
            WHERE id = {comment_id}
            """
    cursor.execute(query)
    return


@database_common.connection_handler
def delete_comment(cursor: RealDictCursor, comment_id: int):
    query = f"""
        DELETE FROM comment
        WHERE id = {comment_id} """
    cursor.execute(query)
    return


@database_common.connection_handler
def get_question_id_by_answer_id(cursor: RealDictCursor, answer_id: int):
    query = f"""
        SELECT question_id 
        FROM answer
        WHERE id = {answer_id}"""
    cursor.execute(query)
    return cursor.fetchone()["question_id"]


@database_common.connection_handler
def get_question_by_comment_id(cursor: RealDictCursor, comment_id: int):
    query = f"""
        SELECT *
        FROM question
        WHERE id IN (
        SELECT question_id
        FROM comment
        WHERE id = {comment_id})"""
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_answer_by_comment_id(cursor: RealDictCursor, comment_id: int):
    query = f"""
        SELECT *
        FROM answer
        WHERE id IN (
        SELECT answer_id
        FROM comment
        WHERE id = {comment_id})"""
    cursor.execute(query)
    return cursor.fetchone()


def get_question_id_by_comment_id(comment_id):
    if get_question_by_comment_id(comment_id) != None :
        return get_question_by_comment_id(comment_id).get("id")
    else:
        answer = get_answer_by_comment_id(comment_id)
        return get_question_id_by_answer_id(answer["id"])



@database_common.connection_handler
def add_answer_comment(cursor: RealDictCursor, details: dict):
    query = f"""
        INSERT INTO comment (answer_id, message, submission_time)
        VALUES ({details["answer_id"]}, '{details["comment_message"]}', '{details["submission_time"]}') """
    cursor.execute(query)
    return


@database_common.connection_handler
def get_comments_by_question_id(cursor: RealDictCursor, question_id: int):
    query = f"""
            SELECT *
            FROM comment
            WHERE question_id = {question_id}
            ORDER BY submission_time DESC"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_comments_by_question_id(cursor: RealDictCursor, question_id: int):
    query = f"""
            SELECT *
            FROM comment
            WHERE answer_id IN (
            SELECT id 
            FROM answer 
            WHERE question_id = {question_id})
            ORDER BY submission_time DESC"""

    cursor.execute(query)
    return cursor.fetchall()


# @database_common.connection_handler
# def delete_question_id_form_question_tag(cursor: RealDictCursor, question_id: int):
#     query = f"""
#             DELETE from question_tag
#             WHERE question_id = {question_id}"""
#     cursor.execute(query)
#     return



#
# @database_common.connection_handler
# def get_question_id(cursor: RealDictCursor) -> list:
#     query = f"""
#         SELECT MAX(id)
#         FROM question
#         """
#     cursor.execute(query)
#     return cursor.fetchone().values()

@database_common.connection_handler
def add_answer(cursor: RealDictCursor, new_answer: dict):
    query = f"""
            INSERT INTO  answer (submission_time, vote_number, question_id, message, image)
            VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s)
            RETURNING id
            """
    cursor.execute(query, new_answer)
    return cursor.fetchone()


@database_common.connection_handler
def get_answer_by_id(cursor: RealDictCursor, answer_id: int) -> list:
    query = f"""
        SELECT *
        FROM answer
        WHERE id = {answer_id}
        """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def update_answer(cursor: RealDictCursor, answer_id: int, edited_answer: dict):
    query = f"""
            UPDATE answer
            SET message = %(message)s, image = %(image)s
            WHERE id = {answer_id}
            """
    cursor.execute(query, edited_answer)


@database_common.connection_handler
def add_question_tag(cursor: RealDictCursor, tag_name: dict):
    query = f"""
        INSERT INTO tag ("name")
        VALUES (%(tag_message)s)
        RETURNING id
        """
    cursor.execute(query, tag_name)
    return cursor.fetchone()


@database_common.connection_handler
def add_question_tag_id(cursor: RealDictCursor, tag_id: int, question_id: int):
    query = f"""
        INSERT INTO question_tag (question_id, tag_id)
        VALUES ({question_id}, {tag_id})
        """
    cursor.execute(query)
    return

@database_common.connection_handler
def get_tag_by_question_id(cursor: RealDictCursor, question_id: int):
    query = f"""
            SELECT *
            FROM tag
            WHERE id IN (
            SELECT tag_id
            FROM question_tag
            WHERE question_id = {question_id})
            
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_question_id_by_tag_id(cursor: RealDictCursor, tag_id: int):
    query = f"""
        SELECT question_id 
        FROM question_tag
        WHERE tag_id = {tag_id}"""
    cursor.execute(query)
    return cursor.fetchone()["question_id"]


@database_common.connection_handler
def delete_tag(cursor: RealDictCursor, tag_id: int):
    query = f"""
        DELETE FROM question_tag
        WHERE tag_id = {tag_id} """
    cursor.execute(query)
    return

@database_common.connection_handler
def get_tag_to_list(cursor: RealDictCursor):
    query = f"""
        SELECT "name"
        FROM tag
        """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def check_for_user(cursor: RealDictCursor, email: str):
    query = """
        SELECT *
        FROM forum_user
        WHERE mail = (%(email)s)
        """
    cursor.execute(query, email)
    return cursor.rowcount > 0
