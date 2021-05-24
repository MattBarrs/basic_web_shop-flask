from app import db

class customers(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    UserNumber = db.Column(db.Integer, index=True, unique=True, nullable=False)
    Address1 = db.Column(db.String(50), index=True, unique=False, nullable=False)
    Postcode = db.Column(db.String(10), index=True, unique=False, nullable=False)
    Password =  db.Column(db.String(50), index=True, unique=False, nullable=False)
    purchases = db.relationship('orders', backref='customers', lazy=True)


class orders(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    SaleId = db.Column(db.Integer, default=False, nullable=False)
    Quantity = db.Column(db.Integer, default=False, nullable=False)
    UserId = db.Column(db.Integer, db.ForeignKey('customers.UserNumber'), nullable=False)
    ProductId = db.Column(db.Integer, db.ForeignKey('items.Id'), nullable=False)



class items(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), index=True, unique=False, nullable=False)
    Details = db.Column(db.String(500), index=True, unique=False, nullable=False)
    Price = db.Column(db.Float, default=False, nullable=False)
    InStock = db.Column(db.Integer, default=False, nullable=False)
    orderItems = db.relationship('orders', backref='orders', lazy=True)
