import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
from models import setup_db, Question, Category, db


QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs ... #Done
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow #Done
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: Create an endpoint to handle GET requests for all available categories. #Done.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    try:
      categories = Category.query.order_by(Category.type).all()
      
      category_result = {
        "success": True,
        'categories': {category.id: category.type for category in categories}
      }
      return jsonify(category_result)
    
    except:
      abort(404)
    finally:
      db.session.close()   
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions #Done.
  '''
  @app.route('/questions', methods=['GET'])
  def get_qestions():
    try:
     selection = Question.query.order_by(Question.id).all()
     categories = Category.query.all()
     current_questions = paginate_questions(request, selection)
     total_questions = len(selection)
     
     question_result = {
       'success': True,
       'questions': current_questions,
       'total_question': len(Question.query.all()),
       'categories': {category.id: category.type for category in categories},
       'current_category': None   
     }
     if (current_questions) == 0:
       abort(404)
     return jsonify(question_result)
    
    except:
      abort(400)
    finally:
      db.session.close()

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. #Done
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).first()
      question.delete()
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)
      
      delete_jquestion = {
        'success': True,
        'delete': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        'current_category': None
      }
      return jsonify(delete_jquestion)
    
    except: 
      abort(404)

  '''
  @TODO: 
  Create an endpoint to POST a new question,
  which will require the question and answer text, category, and difficulty score. #Done
  '''
  @app.route('/questions', methods=['POST'])
  def insert_questions():
    body = request.get_json()
    new_question = body.get('question', 0)
    new_answer = body.get('answer', 0)
    new_difficulty = body.get('difficulty', 0)
    category = body.get('category', 0)
    search_term = body.get('searchTerm', 0)
    
    try:
      if search_term:
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term))).all()
        if selection == []:
          abort(422)
        current_questions = paginate_questions(request, selection)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection)
        })
      else:
        question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=category)

        question.insert()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        return jsonify({
          'success': True,
          'created': question.id,
          'questions': current_questions,
          'total_questions': len(Question.query.all())
        })
    except:
      abort(422)
        
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category.#Done. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    try:
      category = Category.query.filter(Category.id == category_id).one_or_none()
      selection = Question.query.filter(Question.category == category.id).all()
      paginated = paginate_questions(request, selection)
      
      question_category = {
        'success': True,
        'questions': paginated,
        'total_questions': len(Question.query.all()),
        'current_category': category.id 
      }
      return jsonify(question_category)
    
    except:
      abort(404)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. #Done
  '''
  @app.route('/quizzes', methods=['POST'])
  def create_quizz():
    body = request.get_json()
    if not (body == None):
      quiz_cat = body.get('quiz_category')
      previous_question = body.get('previous_questions')
      if quiz_cat['type'] == 'click': task_questions = Question.query.filter(Question.id.notin_((previous_question))).all()
      else: 
        task_questions = Question.query.filter_by(category=quiz_cat['id']).filter(Question.id.notin_((previous_question))).all()

      next_question = task_questions[random.randrange(0, len(task_questions))].format() if len(task_questions) > 0 else None 
      
      quizz = {
        'success': True,
        'question': next_question
      }
    
      return jsonify(quizz)
    else:
      abort(422)
      
  '''
  @TODO: 
  Create error handlers for all expected errors. #Done
  including 404 and 422. 
  ''' 
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resource not found'
    }), 404

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    })
  
  @app.errorhandler(422)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable'
    })

  return app
