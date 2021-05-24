from app import app, models, forms, db, login_manager

from flask import flash, render_template, request, redirect, session, current_app
from db_create import  db_session
from sqlalchemy import func

import datetime
import json

@app.route('/', methods=['GET', 'POST'])
def homePage():
    if logged_in():
        results = models.items.query.all() #Get all items in database
        rows = models.orders.query.count() #Count number of orders
        p = models.items.query.all()

        if request.method == 'POST':

            #Create order id, plus one of max Id, if no orders id = 1
            if(rows>0):
                orderSaleId = models.orders.query.order_by(models.orders.SaleId.desc()).first()
                newSaleId = 1 + int(orderSaleId.SaleId)
            else:
                newSaleId = 1

            #Loop thorugh all item id's
            qry = models.items.query.distinct(models.items.Id).all()
            for itemIndex in qry:
                #Get quantity, validate, if ok add to order
                Quantity = request.form.get(str(itemIndex.Id))


                if Quantity is not None and int(Quantity)>0:
                    item = models.items.query.get(itemIndex.Id)

                    #If invalid request e.g. not enough stock it will aboandon purchase
                    if(item.InStock - int(Quantity) < 0):
                        flash("Not Enough Stock, order rejected!")
                        db.session.rollback()
                        return redirect('/')

                    else:

                        orderItem = models.orders()
                        orderItem.SaleId = newSaleId
                        orderItem.UserId = session['session_ID']
                        orderItem.ProductId =  item.Id
                        orderItem.Quantity = Quantity

                        item.InStock = item.InStock - int(Quantity)
                        if(item.InStock <5):
                            with open("info.log","a") as fo:
                                fo.write("Item [{}] has low stock. Order more\n".format(item.Id))

                        db.session.add(orderItem)

            db.session.commit()
            flash("Order created!!!")

            #Write to log informing of new order
            with open("info.log","a") as fo:
                fo.write("User [{}] Created Order @ [{}] \n".format(session.get('session_ID'), datetime.datetime.now()) )
                print(request.form.get(itemIndex))


        columnNames = ["Name", "Details", "Price", "InStock"]
        return render_template('results_wC.html', columns =columnNames, items = results, title = "Home Page", header1 = "Home Page" )
    else:
        return redirect('/login')

#Edit student
@app.route('/edit_account', methods=['GET', 'POST'])
def edit_account():
    if logged_in():
        form = forms.EditAccountForm(request.form)

        if request.method == 'POST':
            Id = session.get('session_ID')
            customer = models.customers.query.filter(models.customers.UserNumber == Id).first()

            #Validate current password is not null and matches current password.
            if(form.newPassword.data=="")or(form.currentPassword.data=="") or (form.currentPassword.data != customer.Password):
                flash('Empty dataset or incorrect password')

                #Write to log about invalid attempt
                with open("info.log","a") as fo:
                    fo.write("User [{}] Attempt to change password @ [{}] \n".format(session.get('session_ID'), datetime.datetime.now()) )

                flash('Incorrect password')
                return redirect('/')
            else: #Otherwise change password
                customer.Password = form.newPassword.data
                db.session.commit()

                flash('Account updated successfully!')
                with open("info.log","a") as fo:
                    fo.write("User [{}] Password Changed @ [{}] \n".format(session.get('session_ID'), datetime.datetime.now()) )

                return redirect('/')
        return render_template('edit_account.html', form=form)
    else:
        return redirect('/login')




#======================================Product Functions====================================
@app.route('/products_outOfStock', methods=['GET', 'POST'])
def products_outOfStock():
    if logged_in():
        results = []
        qry = models.items.query.filter(models.items.InStock==0)
        results = qry.all()
        columnNames = ["Name", "Details", "Price", "InStock"]

        return render_template('results.html', columns =columnNames, items = results, title = "Out of Stock Products", header1 = "Out of Stock Products"  )
    else:
        return redirect('/login')

@app.route('/products_inStock', methods=['GET', 'POST'])
def products_inStock():
    if logged_in():
        qry = models.items.query.filter(models.items.InStock>=1)
        results = qry.all()
        columnNames = ["Name", "Details", "Price", "InStock"]
        return render_template('results_wC.html', columns =columnNames, items = results,title = "Instock Products", header1 = "Instock Products" )
    else:
        return redirect('/login')


@app.route('/products_OrderSearch', methods=['GET', 'POST'])
def products_OrderSearch():
    #Checks that admin is logged in.
    if logged_in() and session.get('admin') and session.get('admin') == True:
        results = []

        if request.method == 'POST':
             productId =  request.form.get("itemId")
             productId = int(productId)
             maxProductId = int(models.items.query.order_by(models.items.Id.desc()).first().Id)
             qry = models.orders.query.join(models.items, models.orders.ProductId == models.items.Id).add_columns(models.items.Name,models.orders.ProductId, models.orders.UserId, models.orders.SaleId, models.items.Details, models.orders.Quantity)

             if productId <=0 or productId> maxProductId:
                 flash("Incorrect input (max Id: {} )".format(maxProductId))
                 results = qry.order_by(models.orders.Quantity.desc()).all()
             else:
                  results = qry.filter(models.orders.ProductId == productId).order_by(models.orders.Quantity.desc())
        else:
            qry = models.orders.query.join(models.items, models.orders.ProductId == models.items.Id).add_columns(models.items.Name,models.orders.ProductId, models.orders.UserId, models.orders.SaleId, models.items.Details, models.orders.Quantity)
            results = qry.order_by(models.orders.Quantity.desc()).all()

        columnNames = ["ProductId", "Name", "UserId","SaleId", "Quantity"]
        return render_template('results_items.html', columns =columnNames, items = results,title = "Order Search", header1 = "Order Search" )
    else:
        flash("Admin rights required")
        return redirect('/')

#++++++++++++++++++++++++++++++++++++++++Adding New records Functions ++++++++++++++++++++++++++++++++++++++++
#Add a new task
@app.route('/new_customer', methods=['GET', 'POST'])
def new_customer():
    form = forms.NewCustomerForm(request.form)

    if request.method == 'POST' and form.validate():
        customer = models.customers()
        save_customer(customer, form, new=True)

        return redirect('/')
    return render_template('new_customer.html', form=form)


#Add a new product
@app.route('/new_product', methods=['GET', 'POST'])
def new_product():
    if logged_in() and session.get('admin') and session.get('admin') == True:
        form = forms.NewProductForm(request.form)

        if request.method == 'POST' and form.validate():
            item = models.items()
            save_product(item, form, new=True)

            return redirect('/')

        return render_template('new_product.html', form=form)
    else:
        flash("Admin rights required")
        return redirect('/')

@app.route('/view_orders', methods=['GET', 'POST'])
def view_orders():
    if logged_in():
        qry = models.orders.query.join(models.items, models.orders.ProductId == models.items.Id).add_columns(models.items.Name, models.orders.SaleId, models.items.Details, models.items.Price, models.orders.Quantity)
        results = qry.filter(models.orders.UserId == session['session_ID']).all()

        columnNames = ["SaleId", "Name", "Details", "Price", "Quantity"]

        return render_template('results.html', columns =columnNames, items = results,title = "View Orders", header1 = "View Orders" )
    else:
        return redirect('/login')

#_______________________________________LOGIN/OUT FUNCTIONS_________________________
def logged_in():
    if not session.get('logged_in') or session.get('session_ID')==0 or session.get('session_ID') == None:
        with open("info.log","a") as fo:
            fo.write("Attempt to view page not logged in.  [{}] \n".format(datetime.datetime.now()) )
        return False
        #form = forms.LoginForm(request.form)
        #return render_template('login.html', form=form)
    else:
        return True

@app.route('/login', methods=['GET', 'POST'])
def login():
    session['logged_in'] = False
    session['admin'] = False
    session['session_ID'] = 0

    form = forms.LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        POST_Usernumber= form.userNumber.data
        POST_Password= form.password.data
        qry = models.customers.query.filter(models.customers.UserNumber.in_([POST_Usernumber]), models.customers.Password.in_([POST_Password]) )
        result = qry.first()

        if result:
            with open("info.log","a") as fo:
                fo.write("User [{}] Logged in @ [{}] \n".format(POST_Usernumber, datetime.datetime.now()) )

            session['logged_in'] = True
            session['session_ID'] = POST_Usernumber

            if POST_Usernumber == 9999:
                with open("info.log","a") as fo:
                    fo.write("Admin logged in @ [{}] \n".format(datetime.datetime.now()) )
                session['admin'] = True

            flash('Successfully logged in user {}.'.format(form.userNumber.data))
            return redirect('/')
        else:
            with open("info.log","a") as fo:
                fo.write("Failed Login Attempt @ [{}] \n".format(datetime.datetime.now()) )
            flash('Incorrect login')

    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    with open("info.log","a") as fo:
        fo.write("User [{}] Logged Out @ [{}] \n".format(session.get('session_ID'), datetime.datetime.now()) )
    session['logged_in'] = False
    session['session_ID'] = 0
    session['admin']= False

    return redirect('/login')


#____________________________________________SAVE FUNCTIONS___________________________________________
def save_product(item, form, new=False):
    if new:
        if(form.name.data=="")or(form.details.data=="")or(form.price.data=="")or(form.inStock.data=="")or(form.inStock.data<0)or(form.price.data<0) :
            flash("Incorect data, product not added")
            return redirect('/')
        else:
            item.Name = form.name.data
            item.Details = form.details.data
            item.Price = form.price.data
            item.InStock = form.inStock.data

            db.session.add(item)
            # commit the data to the database

            db.session.commit()
            flash('Product created successfully!')

def save_customer(customer, form, new=False):
    if new:
        qry = models.customers.query.filter(models.customers.UserNumber.in_([form.userNumber.data]))
        result = qry.first()

        if result:
            flash("Customer Number already in use!")
            return redirect('/login')
        else:
            #if(form.userNumber.data=="")and(form.address1.data=="")and(form.postcode.data=="")and(form.password.data==""):
            #    return redirect('/')
            #else:
            customer.UserNumber = form.userNumber.data
            customer.Address1 = form.address1.data
            customer.Postcode = form.postcode.data
            customer.Password= form.password.data
            flash('Customer added successfully!')
            with open("info.log","a") as fo:
                    fo.write("New user account [{}]  created @ [{}] \n".format(customer.UserNumber, datetime.datetime.now()) )
            db.session.add(customer)
            # commit the data to the database

            db.session.commit()

def save_purchase(purchase,itemsPurchased, form, new=False):
    purchase.UserId = session.get('session_ID')
    if new:
        db.session.add(purchase)

        for item in itemsPurchased:
            item.SaleId = purchase.Id
            item.Quantity = form.Quantity.data
            item.ProductId = form.ProductId.data
        if new:
            db.session.add(customer)
        # commit the data to the database
        db.session.commit()
