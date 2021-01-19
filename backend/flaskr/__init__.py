import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

import pdb
import json



# to do
# error: 400, 500
# test

#---------------
# settings
#---------------

QUESTIONS_PER_PAGE = 10


#---------------
# utility functions
#---------------

def paginate_questions(request, selection, items_per_page=8):
  page = request.args.get('page',1,type=int)
  start = (page - 1) * items_per_page
  end = start + items_per_page

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

"""
def queryResult_to_dict(query_object):

  # get list of data attributes
  data_attrs = [attribute for attribute in dir(query_object)\
                  if (attribute[0:1] not in ['_']\
                       and attribute not in\
                       ['query','query_class','metadata'])]
  outdict = {key:value for key, value in query_object.items()\
                       if key in data_attrs}
  
  return outdict
"""

#---------------
# app
#---------------
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)  #, resources={r"*/api/*": {origins:'*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers','GET, POST, PATCH, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods = ['GET'])
  def get_categories():
    query_categories = Category.query.all()

    if query_categories == None:
        abort(404)
   
    output = {}
    categories = [category.type for category in query_categories]
    output['categories'] = categories

    return jsonify(output)
 

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods = ['GET'])
  def get_questions():
      # get updated questions from db
      query_questions = Question.query.all()

      current_questions = paginate_questions(request,\
                                             query_questions,\
                                             items_per_page=5)
      if len(current_questions)==0:
        abort(404)

      questions = []
      for question in current_questions:
        question_dict={}
        question_dict['id'] = question['id']
        question_dict['question'] = question['question']
        question_dict['answer'] = question['answer']
        question_dict['category'] = question['category']
        question_dict['difficulty'] = question['difficulty']
        questions.append(question_dict)

      # get categories
      query_categories = Category.query.all()
      categories = [category.type for category in query_categories]

      output={}
      output['questions'] = questions
      output['total_questions'] = len(query_questions)
      output['categories'] = categories
      output['current_category'] = 'all'
      return jsonify(output)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<q_id>', methods = ['DELETE'])
  def delete_question(q_id):
      if request.method!='DELETE':
        abort(405)
      try:
        # get question id
        delete_id = int(q_id)

        # get question to be deleted
        query_question = Question.query\
                                .filter(Question.id==delete_id)\
                                .first()

        if query_question == None:
          abort(404)

        # delete question
        query_question.delete()
    
        # do not return anything
        return '',204

      except:
        abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods = ['POST'])
  def insert_question():

      # get new question from form
      #----------------------------

      result_dict = request.get_json()
      #search_term = result_dict['searchTerm']

      # id is the last id from table in db +1
      try:
        new_id = Question.query.order_by(Question.id.desc()).first().id+1
      except:
        new_id = 1
      id_val = new_id
      question = result_dict['question']
      answer = result_dict['answer']
      difficulty = result_dict['difficulty']
      category = result_dict['category']

      # instantiate new question object
      #new_question = Question(id=id_val,\
      new_question = Question(question=question,\
                       answer=answer,\
                       category=category,\
                       difficulty=difficulty)

      # save new question
      try:
        new_question.insert()
      
        # return new question
        return jsonify(result_dict)
    
        # do not return anything
        #return '',204
      except:
        abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():

    # initialize response (dict)
    output = {}

    # query for name in db
    #search_term = request.form['search_term']
    result_dict = request.get_json()
    search_term = result_dict['searchTerm']
    # add '%' characters to search term
    search_formatted=f'%{search_term}%'
    # query from db - case insensitive 'ilike'
    query_results = Question.query\
                      .filter(Question.question.ilike(search_formatted))\
                      .all()    

    # store of each result
    questions = []
    for question in query_results:
      question_dict={}
      question_dict['id'] = question.id
      question_dict['question'] = question.question
      question_dict['answer'] = question.answer
      question_dict['category'] = question.category
      question_dict['difficulty'] = question.difficulty
      questions.append(question_dict)
    

    output={}
    output['questions'] = questions
    output['total_questions'] = len(query_results)
    output['categories'] = [result.category for result in query_results]
    output['current_category'] = 'fill1'

    return jsonify(output)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<id_cat>/questions", methods=['GET'])
  def get_questions_by_cat(id_cat):
    if request.method!='GET':
      abort(405)
    query_categories = Category\
                .query\
                .filter_by(id=int(id_cat)+1)\
                .first()
    cat_name = query_categories.type
    query_questions = Question.query\
                              .filter(Question.category==int(id_cat)+1)\
                              .all()
    questions = []
    for question in query_questions:
      question_dict={}
      question_dict['id'] = question.id
      question_dict['question'] = question.question
      question_dict['answer'] = question.answer
      question_dict['category'] = question.category
      question_dict['difficulty'] = question.difficulty
      questions.append(question_dict)

    # get categories

    output={}
    output['questions'] = questions
    output['total_questions'] = len(query_questions)
    output['current_category'] = cat_name

    #pdb.set_trace()
    return jsonify(output)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route("/quizzes", methods=['POST'])
  def play_quiz():

    # get data from post request (category, previous questions)
    request_dict = request.get_json()
    current_cat_id = int(request_dict['quiz_category']['id'])+1
    ids_previous = request_dict['previous_questions']
    # select current question: from current category and selected id
    
    # select current id
    query_questions = Question.query\
                        .filter(Question.category==current_cat_id)\
                        .all()
  
    ids_remaining = [question.id for question in query_questions\
                                 if question.id not in ids_previous]

    # draw current question
    #if len(ids_remaining)>0:
    index_drawn = random.randint(0,len(ids_remaining)-1)
    id_drawn = ids_remaining[index_drawn]
    current_question = Question.query\
                        .filter(Question.id==id_drawn)\
                        .first()
    #current_question = query_questions[index_drawn]

    # save current question in output
    question_dict={}
    question_dict['id'] = current_question.id
    question_dict['question'] = current_question.question
    question_dict['answer'] = current_question.answer
    question_dict['category'] = current_question.category
    question_dict['difficulty'] = current_question.difficulty

    output = {}
    output['question'] = question_dict

    return jsonify(output)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "not found"
                    }), 404


  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "bad request"
                    }), 400

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
                    "success": False, 
                    "error": 405,
                    "message": "method not allowed"
                    }), 405



  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "server error"
                    }), 500

  return app

    