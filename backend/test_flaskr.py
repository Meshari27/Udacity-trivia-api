import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""#zzzzzZZZZZZZboooooo

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #category get_test #Done
    def test_get_categories(self): #OK
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_404_sent_request_beyond_vaild_category_page(self): #OK
        res = self.client().get('/categories/69')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    

    #question get test #Done
    def test_get_questions(self): #OK
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_question'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    def test_404_request_beyond_vaild_question_page(self): #SAD
        res = self.client().get('/questions?page=69')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    # test delete question
    def test_delete_question(self): 
        res = self.client().delete('questions/3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['delete'], 3)
        self.assertTrue(data['total_questions'])

    def test_404_question_does_not_exist(self): #OK
        res = self.client().delete('/questions/69')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    # test create question
    def test_create_questions(self): #OK
        new_question = {
            'id' : 43,
            'questions': 'whoami',
            'answer': 'mesho',
            'difficulty': 3,
            'category': 3  
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_405_create_question_not_allowed(self):
        new_question = {
            'id' : 10000,
           'questions': 'boo',
            'answer': 'boo',
            'difficulty': 3,
            'category': 3  
        }
        res = self.client().post('questions/68', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'method not allowed')


    # test search question
    def test_question_search(self): #OK
        res = self.client().post('/questions', json={'searchTerm': 'who'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_question_search_without_result(self):
        res = self.client().post('/questions', json={'searchTerm': 'xzzzz'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    # test get questions based on category
    def test_get_question_by_categoty(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_questions_category_not_found(self): #OK
        res = self.client().get('/categories/69/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # test quiz
    def test_play_quiz(self):
        res = self.client().post('/quizzes', json={'previous_questions': [12, 13], 'quiz_category': {'type': 'History', 'id': 4}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_play_quiz_failed(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

