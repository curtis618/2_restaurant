from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用於 flash 訊息

# 資料庫連接函數
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root', 
        password='', 
        database='FoodDelivery'
    )
    return connection
# orders details
@app.route('/order_details/<int:order_id>', methods=['GET'])
def order_details(order_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True) 
    cursor.execute('SELECT * FROM Orderitems WHERE order_id = %s', (order_id,))
    orderitems = cursor.fetchall()
    
    # Fetch menu names
    menu_names = {}
    for item in orderitems:
        cursor.execute('SELECT item_name FROM Menus WHERE menu_id = %s', (item['menu_id'],))
        menu_name = cursor.fetchone()
        if menu_name:
            menu_names[item['menu_id']] = menu_name['item_name']
    
    cursor.execute('SELECT * FROM Orders WHERE order_id = %s', (order_id,))
    order = cursor.fetchone()

    return render_template('order_detail.html', orderitems=orderitems, order=order, order_id=order_id, menu_names=menu_names)
@app.route('/restaurant/<int:restaurant_id>', methods=['GET'])
def rastaurant_profile(restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Restaurants WHERE restaurant_id = %s', (restaurant_id,))
    user = cursor.fetchall()
    cursor.close()
    connection.close()
    print(user)
    return render_template('profile.html', user=user)


@app.route('/restaurant/<int:restaurant_id>/menu', methods=['GET'])
def view_menu(restaurant_id=1):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Menus WHERE restaurant_id = %s', (restaurant_id,))
    menus = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('menu.html', menus=menus)

# 餐廳菜單上架 - 表單和插入資料庫
@app.route('/restaurant/<int:restaurant_id>/add_menu_item', methods=['GET', 'POST'])
def add_menu_item(restaurant_id):
    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        price = request.form['price']
        stock_quantity = request.form['stock_quantity']

        connection = get_db_connection()
        cursor = connection.cursor()
        insert_query = '''
            INSERT INTO Menus (restaurant_id, item_name, description, price, stock_quantity)
            VALUES (%s, %s, %s, %s, %s)
        '''
        restaurant_id = 1
        cursor.execute(insert_query, (restaurant_id, item_name, description, price, stock_quantity))
        connection.commit()
        cursor.close()
        connection.close()

        flash('菜單項目已成功上架', 'success')
        return redirect(url_for('view_menu', restaurant_id=restaurant_id))

    return render_template('add_menu_item.html', restaurant_id=restaurant_id)

# 確認收單的路由 - 顯示待確認的訂單
@app.route('/restaurant/<int:restaurant_id>/orders', methods=['GET', 'POST'])
def manage_orders(restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 獲取該餐廳的所有待確認訂單
    cursor.execute('''
        SELECT * FROM Orders
        WHERE restaurant_id = %s
    ''', (restaurant_id,))
    pending_orders = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('manage_orders.html', orders=pending_orders)

@app.route('/notify_customer/<int:order_id>', methods=['POST'])
def notify_customer(order_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE Orders SET status = %s WHERE order_id = %s', ('accepted', order_id))
    connection.commit()
    cursor.close()
    connection.close()
    flash('已通知顧客取餐', 'info')
    return redirect(url_for('manage_orders', restaurant_id=1))

@app.route('/check_order/<int:order_id>', methods=['POST'])
def check_order(order_id):    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE Orders SET status = %s WHERE order_id = %s', ('delivered', order_id))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('manage_orders', restaurant_id=1))

@app.route('/order_history/<int:restaurant_id>', methods=['GET'])
def order_history(restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Orders WHERE restaurant_id = %s', (restaurant_id,))
    orders = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('order_history.html', orders=orders)

#外送員
@app.route('/delivery/dashboard/<int:delivery_person_id>', methods=['GET'])
def delivery_dashboard(delivery_person_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 查询已完成订单数量
    cursor.execute('''
        SELECT COUNT(*) AS completed_count
        FROM Deliveries
        WHERE delivery_status = 'completed' AND delivery_person_id = %s
    ''', (delivery_person_id,))
    completed_result = cursor.fetchone()
    completed_count = completed_result['completed_count'] if completed_result else 0

    # 查询外送员基本信息
    cursor.execute('SELECT * FROM Users WHERE user_id = %s', (delivery_person_id,))
    delivery_person = cursor.fetchone()

    cursor.close()
    connection.close()

    if not delivery_person:
        return "外送員不存在", 404

    return render_template(
        'delivery_dashboard.html',
        delivery_person=delivery_person,
        delivery_person_id=delivery_person_id,
        completed_count=completed_count
    )

# 待配送订单
@app.route('/delivery/orders/<int:delivery_person_id>', methods=['GET'])
def view_delivery_orders(delivery_person_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 查询待配送订单
    cursor.execute('''
        SELECT d.delivery_id, d.order_id, o.customer_id, o.total_price, r.name AS restaurant_name
        FROM Deliveries d
        JOIN Orders o ON d.order_id = o.order_id
        JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
        WHERE d.delivery_status = 'pending'
    ''')
    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'delivery_orders.html',
        delivery_person_id=delivery_person_id,
        orders=orders
    )

# 接单操作
@app.route('/delivery/orders/<int:delivery_person_id>/<int:delivery_id>/accept', methods=['POST'])
def accept_delivery(delivery_person_id, delivery_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # 更新订单状态为 "in_progress" 并绑定外送员
    cursor.execute('''
        UPDATE Deliveries
        SET delivery_status = 'in_progress', delivery_person_id = %s, pickup_time = NOW()
        WHERE delivery_id = %s
    ''', (delivery_person_id, delivery_id))
    connection.commit()

    cursor.close()
    connection.close()

    flash('成功接单！', 'success')
    return redirect(url_for('view_delivery_orders', delivery_person_id=delivery_person_id))

# 已完成订单
@app.route('/delivery/orders/completed/<int:delivery_person_id>', methods=['GET'])
def completed_orders(delivery_person_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 查询已完成订单
    cursor.execute('''
        SELECT d.delivery_id, d.order_id, o.customer_id, o.total_price, r.name AS restaurant_name, d.delivery_time
        FROM Deliveries d
        JOIN Orders o ON d.order_id = o.order_id
        JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
        WHERE d.delivery_status = 'completed' AND delivery_person_id = %s
    ''', (delivery_person_id,))
    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'completed_orders.html',
        delivery_person_id=delivery_person_id,
        orders=orders
    )

# 外送员个人信息
@app.route('/delivery/profile/<int:delivery_person_id>', methods=['GET'])
def delivery_profile(delivery_person_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 查询外送员的个人信息
    cursor.execute('SELECT * FROM Users WHERE user_id = %s', (delivery_person_id,))
    delivery_person = cursor.fetchone()

    cursor.close()
    connection.close()

    if not delivery_person:
        return "外送員不存在", 404

    return render_template(
        'delivery_profile.html',
        delivery_person=delivery_person,
        delivery_person_id=delivery_person_id
    )


if __name__ == '__main__':
    app.run(debug=True)