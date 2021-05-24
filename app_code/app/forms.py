from wtforms import Form, StringField, FloatField, IntegerField, PasswordField, SelectField

class NewProductForm(Form):
    name = StringField('Name')
    details = StringField('Details')
    price = FloatField("Price")
    inStock = IntegerField("InStock")

class SearchOrders(Form):
     itemId = IntegerField("ItemId")

class NewCustomerForm(Form):
    userNumber = StringField('UserNumber')
    address1 = StringField('Address1')
    postcode = StringField('Postcode')
    password = PasswordField("Password")

class EditAccountForm(Form):
    currentPassword = PasswordField("CurrentPassword")
    newPassword = PasswordField("NewPassword")

class LoginForm(Form):
    userNumber = IntegerField('UserNumber')
    password = PasswordField("Password")
