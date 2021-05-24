# #!flask/bin/python
# import os
# import unittest

# from config import basedir
# from app import app, db
# from app.models import customers
# from app.views import save_customer

# class TestCase(unittest.TestCase):
#     def setUp(self):
#         app.config['TESTING'] = True
#         app.config['WTF_CSRF_ENABLED'] = False
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
#         self.app = app.test_client()
#         db.create_all()

#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()

#     def test_UniqueUsernumber(self):
#         u = customers(UserNumber =111, Address1 = '123 Avenue', Postcode = 'AB1 2BC', Password =  'password')
#         db.session.add(u)
#         db.session.commit()
#         form = u
#         save_customer(u, form, True)
#         assert UserNumber != 111
#         u = customers(UserNumber = UserNumber, Address1 = '456 Avenue', Postcode = 'AB3 17DC', Password =  'password1')
#         db.session.add(u)
#         db.session.commit()
#         save_customer(u)
#         assert UserNumber2 != 111
#         assert UserNumber2 != UserNumber

# if __name__ == '__main__':
#     unittest.main()