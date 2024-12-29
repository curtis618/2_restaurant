from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = '123TyU%^&'

# 資料庫連接函數
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root', 
        password='', 
        database='FoodDelivery'
    )
    return connection

@app.route('/')
def index():
    return redirect(url_for('login'))

# 註冊功能
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 檢查郵箱是否已被註冊
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('電子郵件已被註冊', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('register'))

        # 如果是外送員，獲取新的 delivery_person_id
        if role == '外送員':
            cursor.execute("SELECT MAX(delivery_person_id) as max_id FROM users WHERE role = '外送員'")
            result = cursor.fetchone()
            delivery_person_id = 1 if result['max_id'] is None else result['max_id'] + 1
            
            # 插入新用戶，包含 delivery_person_id
            cursor.execute(
                "INSERT INTO users (name, email, password, role, delivery_person_id) VALUES (%s, %s, %s, %s, %s)",
                (name, email, password, role, delivery_person_id)
            )
        else:
                
            # 非外送員用戶正常插入
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, password, role)
            )
        
        conn.commit()
        cursor.close()
        conn.close()

        flash('註冊成功！請登入', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# 登入功能
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and user['password'] == password:
            session['user_id'] = user['user_id']
            session['role'] = user['role']

            cursor.close()
            conn.close()

            if user['role'] == '外送員':
                return redirect(url_for('delivery_orders', delivery_id=user['user_id']))
            elif user['role'] == 'customer':
                return redirect(url_for('customer_dashboard',customer_id=user['user_id']))
            elif user['role'] == 'vendor':
                return redirect(url_for('manage_orders', restaurant_id=user['user_id']))
            elif user['role'] == 'platform':
                return redirect(url_for('platform_dashboard', platform_id=user['user_id']))
            else:
                flash('角色錯誤', 'danger')
        else:
            flash('電子郵件或密碼錯誤', 'danger')
            cursor.close()
            conn.close()

    return render_template('login.html')

# 餐廳功能
@app.route('/restaurant/<int:restaurant_id>/orders', methods=['GET', 'POST'])
def manage_orders(restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Orders WHERE restaurant_id = %s', (restaurant_id,))
    pending_orders = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('vendor/manage_orders.html', orders=pending_orders)

@app.route('/restaurant/<int:restaurant_id>', methods=['GET'])
def rastaurant_profile(restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Restaurants WHERE restaurant_id = %s', (restaurant_id,))
    user = cursor.fetchall()
    cursor.close()
    connection.close()
    print(user)
    return render_template('vendor/profile.html', user=user)

@app.route('/restaurant/<int:restaurant_id>/menu', methods=['GET'])
def view_menu(restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Menus WHERE restaurant_id = %s', (restaurant_id,))
    menus = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('vendor/menu.html', menus=menus)

@app.route('/restaurant/<int:restaurant_id>/add_menu_item', methods=['GET', 'POST'])
def add_menu_item(restaurant_id):
    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        price = request.form['price']
        stock_quantity = request.form['stock_quantity']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Menus (restaurant_id, item_name, description, price, stock_quantity) VALUES (%s, %s, %s, %s, %s)",
            (restaurant_id, item_name, description, price, stock_quantity)
        )
        connection.commit()
        cursor.close()
        connection.close()

        flash('菜單項目已成功上架', 'success')
        return redirect(url_for('view_menu', restaurant_id=restaurant_id))

    return render_template('vendor/add_menu_item.html', restaurant_id=restaurant_id)

@app.route('/order_details/<int:order_id>', methods=['GET'])
def order_details(order_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True) 
    cursor.execute('SELECT * FROM Orderitems WHERE order_id = %s', (order_id,))
    orderitems = cursor.fetchall()
    
    menu_names = {}
    for item in orderitems:
        cursor.execute('SELECT item_name FROM Menus WHERE menu_id = %s', (item['menu_id'],))
        menu_name = cursor.fetchone()
        if menu_name:
            menu_names[item['menu_id']] = menu_name['item_name']
    
    cursor.execute('SELECT * FROM Orders WHERE order_id = %s', (order_id,))
    order = cursor.fetchone()

    return render_template('vendor/order_detail.html', orderitems=orderitems, order=order, order_id=order_id, menu_names=menu_names)

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
    return render_template('vendor/order_history.html', orders=orders)




# 外送員 Dashboard
@app.route('/delivery/<int:delivery_person_id>/dashboard', methods=['GET'])
def delivery_dashboard(delivery_person_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 查詢已完成訂單數量
    cursor.execute('''
        SELECT COUNT(*) AS completed_count
        FROM Deliveries
        WHERE delivery_status = 'completed' AND delivery_person_id = %s
    ''', (delivery_person_id,))
    completed_result = cursor.fetchone()
    completed_count = completed_result['completed_count'] if completed_result else 0

    # 查詢外送員基本資訊
    cursor.execute('SELECT * FROM Users WHERE user_id = %s', (delivery_person_id,))
    delivery_person = cursor.fetchone()
    cursor.close()
    connection.close()


    return render_template(
        'delivery/delivery_dashboard.html',
        delivery_person=delivery_person,
        delivery_person_id=delivery_person_id,
        completed_count=completed_count
    )


# 待配送订单
@app.route('/delivery/<int:delivery_person_id>/orders', methods=['GET'])
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
        'delivery/view_delivery_orders.html',
        delivery_person_id=delivery_person_id,
        orders=orders
    )

# 接单操作
@app.route('/delivery/<int:delivery_person_id>/orders/<int:delivery_id>/accept', methods=['POST'])
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
        'delivery/completed_orders.html',
        delivery_person_id=delivery_person_id,
        orders=orders
    )

# 外送員路由
@app.route('/delivery/<int:delivery_id>/orders')
def delivery_orders(delivery_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if int(session['user_id']) != int(delivery_id):
        flash('無權訪問此頁面', 'danger')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 獲取待配送和配送中的訂單
    cursor.execute("""
        SELECT o.*, r.name as restaurant_name, c.address as customer_address 
        FROM Orders o 
        JOIN Restaurants r ON o.restaurant_id = r.restaurant_id 
        JOIN Customers c ON o.customer_id = c.customer_id 
        WHERE o.delivery_person_id = %s 
        AND o.status IN ('待配送', '配送中')
    """, (delivery_id,))
    
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('delivery_orders.html', orders=orders)

@app.route('/delivery/<int:delivery_id>/history')
def delivery_history(delivery_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if int(session['user_id']) != int(delivery_id):
        flash('無權訪問此頁面', 'danger')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 獲取已完成的訂單
    cursor.execute("""
        SELECT o.*, r.name as restaurant_name, c.address as customer_address 
        FROM Orders o 
        JOIN Restaurants r ON o.restaurant_id = r.restaurant_id 
        JOIN Customers c ON o.customer_id = c.customer_id 
        WHERE o.delivery_person_id = %s 
        AND o.status = '已送達'
    """, (delivery_id,))
    
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('delivery_history.html', orders=orders)

@app.route('/delivery/<int:delivery_id>/profile')
def delivery_profile(delivery_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if int(session['user_id']) != int(delivery_id):
        flash('無權訪問此頁面', 'danger')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 獲取外送員資料
    cursor.execute("""
        SELECT * FROM users 
        WHERE user_id = %s AND role = '外送員'
    """, (delivery_id,))
    
    profile = cursor.fetchone()
    
    # 獲取配送統計
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN status = '已送達' THEN 1 END) as completed_orders,
            COUNT(CASE WHEN status IN ('待配送', '配送中') THEN 1 END) as pending_orders
        FROM Orders 
        WHERE delivery_person_id = %s
    """, (delivery_id,))
    
    stats = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('delivery_profile.html', profile=profile, stats=stats)

@app.route('/delivery/<int:delivery_id>/update_status/<int:order_id>', methods=['POST'])
def update_delivery_status(delivery_id, order_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if int(session['user_id']) != int(delivery_id):
        flash('無權執行此操作', 'danger')
        return redirect(url_for('login'))
        
    status = request.form.get('status')
    if status not in ['配送中', '已送達']:
        flash('無效的狀態更新', 'danger')
        return redirect(url_for('delivery_orders', delivery_id=delivery_id))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE Orders 
        SET status = %s 
        WHERE order_id = %s AND delivery_person_id = %s
    """, (status, order_id, delivery_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('訂單狀態已更新', 'success')
    return redirect(url_for('delivery_orders', delivery_id=delivery_id))

# 平台管理功能
@app.route('/platform/<int:platform_id>/dashboard')
def platform_dashboard(platform_id):
    if 'user_id' not in session or session['role'] != 'platform':
        return redirect(url_for('login'))
    
    if int(session['user_id']) != int(platform_id):
        flash('無權訪問此頁面', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 獲取所有餐廳資訊
    cursor.execute("""
        SELECT r.*, u.name as owner_name 
        FROM restaurants r 
        JOIN users u ON r.owner_id = u.user_id
    """)
    restaurants = cursor.fetchall()
    
    # 獲取所有外送員資訊
    cursor.execute("""
        SELECT u.*, 
            COUNT(CASE WHEN d.delivery_time IS NOT NULL THEN 1 END) as completed_deliveries,
            COUNT(CASE WHEN d.delivery_time IS NULL THEN 1 END) as ongoing_deliveries
        FROM users u 
        LEFT JOIN deliveries d ON u.user_id = d.delivery_person_id
        WHERE u.role = '外送員'
        GROUP BY u.user_id
    """)
    delivery_persons = cursor.fetchall()
    
    # 獲取所有訂單資訊
    cursor.execute("""
        SELECT o.*, 
            c.name as customer_name,
            r.name as restaurant_name,
            u.name as delivery_person_name
        FROM orders o
        JOIN users c ON o.customer_id = c.user_id
        JOIN restaurants r ON o.restaurant_id = r.restaurant_id
        LEFT JOIN deliveries d ON o.order_id = d.order_id
        LEFT JOIN users u ON d.delivery_person_id = u.user_id
        ORDER BY o.order_date DESC
        LIMIT 10
    """)
    recent_orders = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('platform/dashboard.html', 
                         platform_id=platform_id,
                         restaurants=restaurants,
                         delivery_persons=delivery_persons,
                         recent_orders=recent_orders)

@app.route('/platform/<int:platform_id>/restaurants')
def manage_restaurants(platform_id):
    if 'user_id' not in session or session['role'] != 'platform':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, u.name as owner_name, u.email as owner_email
        FROM restaurants r
        JOIN users u ON r.owner_id = u.user_id
    """)
    restaurants = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('platform/restaurants.html', 
                         platform_id=platform_id,
                         restaurants=restaurants)

@app.route('/platform/<int:platform_id>/delivery_persons')
def manage_delivery_persons(platform_id):
    if 'user_id' not in session or session['role'] != 'platform':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.*, 
            COUNT(CASE WHEN d.delivery_time IS NOT NULL THEN 1 END) as completed_deliveries,
            COUNT(CASE WHEN d.delivery_time IS NULL THEN 1 END) as ongoing_deliveries
        FROM users u 
        LEFT JOIN deliveries d ON u.user_id = d.delivery_person_id
        WHERE u.role = '外送員'
        GROUP BY u.user_id
    """)
    delivery_persons = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('platform/delivery_persons.html', 
                         platform_id=platform_id,
                         delivery_persons=delivery_persons)

@app.route('/platform/<int:platform_id>/orders')
def manage_platform_orders(platform_id):
    if 'user_id' not in session or session['role'] != 'platform':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.*, 
            c.name as customer_name,
            r.name as restaurant_name,
            u.name as delivery_person_name
        FROM orders o
        JOIN users c ON o.customer_id = c.user_id
        JOIN restaurants r ON o.restaurant_id = r.restaurant_id
        LEFT JOIN deliveries d ON o.order_id = d.order_id
        LEFT JOIN users u ON d.delivery_person_id = u.user_id
        ORDER BY o.order_date DESC
    """)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('platform/orders.html', 
                         platform_id=platform_id,
                         orders=orders)

#客戶--------------------------------------------------------------------
@app.route('/customer/<int:customer_id>/dashboard', methods=['GET'])
def customer_dashboard(customer_id):
    connection =  get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('select * from users where user_id = %s', (customer_id,))
    dat = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('customer/customer_dashboard.html',data = dat,customer_id=customer_id)

#看餐廳
@app.route('/customer/<int:customer_id>/view_restaurant', methods=['GET'])
def customer_view_restaurant(customer_id):
    connection =  get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('select * from restaurants')
    dat= cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('customer/customer_view_restaurant.html', data=dat,customer_id=customer_id)

#待取餐
@app.route('/customer/<int:customer_id>/pickup', methods=['GET', 'POST'])
def customer_pickup(customer_id):
    connection =  get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM orders WHERE customer_id = %s AND status != %s ', (customer_id, 'all_completed'))
    pickup = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('customer/customer_pickup.html',data = pickup,customer_id=customer_id)

#取餐確認   
@app.route('/customer/<int:customer_id>/pickup_confirm/<int:order_id>', methods=['POST'])
def customer_pickup_confirm(customer_id, order_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE Orders SET status = %s WHERE order_id = %s', ('all_completed', order_id))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('customer_pickup', customer_id=customer_id))

#查看訂單
@app.route('/customer/<int:customer_id>/orders', methods=['GET', 'POST'])
def customer_orders(customer_id):
    connection =  get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
    SELECT o.*, 
           r.name AS restaurant_name,
           rv.review_id IS NOT NULL AS is_reviewed
    FROM Orders o
    JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
    LEFT JOIN Reviews rv ON o.order_id = rv.order_id
    WHERE o.customer_id = %s
    ORDER BY o.order_date DESC
    ''', (customer_id,))
    pickup = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('customer/customer_orders.html',data = pickup,customer_id=customer_id)

#評論紀錄
@app.route('/customer/<int:customer_id>/reviews', methods=['GET', 'POST'])
def customer_reviews(customer_id):    
    connection =  get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
        SELECT r.*, res.name AS restaurant_name 
        FROM reviews r 
        JOIN restaurants res ON r.restaurant_id = res.restaurant_id 
        WHERE r.customer_id = %s
    ''', (customer_id,))
    reviews = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('customer/customer_reviews.html',data = reviews,customer_id=customer_id)

#新增評論
@app.route('/customer/<int:order_id>/<int:customer_id>/<int:restaurant_id>/add_review', methods=['GET', 'POST'])
def customer_add_review(order_id,customer_id,restaurant_id):
    if request.method == 'POST':
        rating = request.form['rating']
        comment = request.form['comment']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO reviews (order_id,customer_id, restaurant_id, rating, comment) VALUES (%s,%s,%s,%s,%s)",
            (order_id, customer_id, restaurant_id, rating, comment)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('customer_reviews', customer_id=customer_id))

    return render_template('customer/customer_add_review.html',order_id = order_id,customer_id=customer_id,restaurant_id=restaurant_id)

#編輯評論
@app.route('/customer/<int:customer_id>/edit_review/<int:review_id>', methods=['GET', 'POST'])
def customer_edit_review(customer_id, review_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM reviews WHERE review_id = %s', (review_id,))
    dat = cursor.fetchone()

    if request.method == 'POST':
        rating = request.form['rating']
        review_text = request.form['comment']

        cursor.execute(
            "UPDATE reviews SET rating = %s, comment = %s WHERE review_id = %s",
            (rating, review_text, review_id)
        )
        connection.commit()
        cursor.close()
        connection.close()

        flash('評論已成功更新', 'success')
        return redirect(url_for('customer_reviews', customer_id=customer_id))

    return render_template('customer/customer_edit_reviews.html', review = dat, customer_id=customer_id, review_id=review_id)

#刪除評論
@app.route('/customer/<int:customer_id>/delete_review/<int:review_id>', methods=['POST'])
def customer_delete_review(customer_id, review_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM reviews WHERE review_id = %s', (review_id,))
    connection.commit()
    cursor.close()
    connection.close()
    flash('評論已成功刪除', 'success')
    return redirect(url_for('customer_reviews', customer_id=customer_id))

#查看菜單
@app.route('/customer/<int:restaurant_id>/view_menu', methods=['GET', 'POST'])
def customer_view_menu(restaurant_id):
    cus_id = session['user_id']
    connection =  get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM menus WHERE restaurant_id = %s', (restaurant_id,))
    menu = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('customer/customer_menu.html', menus=menu,restaurant_id = restaurant_id,customer_id = cus_id)

#下訂單
@app.route('/place_order/<int:restaurant_id>', methods=['POST'])
def place_order(restaurant_id):
    customer_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # 創建訂單
    cursor.execute(
        "INSERT INTO Orders (customer_id, restaurant_id, status, total_price) VALUES (%s, %s, %s, %s)",
        (customer_id, restaurant_id, 'accepted', 0)
    )
    connection.commit()
    # 獲取orders最近新增的ID
    cursor.execute('''
                    SELECT *FROM orders
                    ORDER BY order_id DESC
                    LIMIT 1;''')
    order_id = cursor.fetchone()['order_id']
    
    # 獲取菜單
    cursor.execute('SELECT * FROM menus WHERE restaurant_id = %s', (restaurant_id,))
    menus = cursor.fetchall()
    # 創建orderitems
    for menu in menus:
        menu_id = menu['menu_id']
        menu_price = menu['price']
        quantity = request.form.get(f"quantity_{menu_id}")
        # 如果數量不為0，則新增orderitems
        if int(quantity) != 0:
            cursor.execute(
                "INSERT INTO Orderitems (order_id, menu_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (order_id, menu_id, quantity, int(quantity)*int(menu_price))
            )
            connection.commit()          
        else:
            continue

    
    # 更新訂單總價
    cursor.execute('SELECT SUM(price) AS total_price FROM Orderitems WHERE order_id = %s', (order_id,))
    total_price = cursor.fetchone()['total_price']
    cursor.execute('UPDATE Orders SET total_price = %s WHERE order_id = %s', (total_price, order_id))
    connection.commit()

    cursor.close()
    connection.close()
    return redirect(url_for('customer_orders', customer_id=customer_id))

# 其他功能保持不變，例如平台管理、外送員管理等
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
