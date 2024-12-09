from flask import Flask, render_template, request, redirect, url_for, flash
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

# restaurant profile
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
    print(pending_orders)
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

if __name__ == '__main__':
    app.run(debug=True)
