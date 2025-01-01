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
        database='fooddelivery'
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


        else:
                
            # 非外送員用戶正常插入
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, password, role)
            )
            if role == 'vendor':
                owner_id = cursor.lastrowid
                cursor.execute("INSERT INTO Restaurants (name,address,owner_id) VALUES (%s,%s,%s)", ("新餐廳"," ",owner_id))
                cursor.execute("SELECT * FROM Restaurants WHERE owner_id = %s",(owner_id,))
                restaurant = cursor.fetchone()
                cursor.execute("UPDATE users SET restaurant_id = %s WHERE user_id = %s", (restaurant['restaurant_id'],owner_id))

        
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
        print(user)

        if user and user['password'] == password:
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            session['restaurant_id'] = user['restaurant_id']
            session['delivery_person_id']=user['user_id']

            cursor.close()
            conn.close()

            if user['role'] == 'delivery_person':
                return redirect(url_for('delivery_dashboard', delivery_person_id=user['user_id']))
            elif user['role'] == 'customer':
                return redirect(url_for('customer_dashboard',customer_id=user['user_id']))
            elif user['role'] == 'vendor':
                return redirect(url_for('manage_orders', restaurant_id=user['restaurant_id']))
            elif user['role'] == 'platform':
                return redirect(url_for('platform_dashboard', platform_id=user['user_id']))
            else:
                flash('角色錯誤', 'danger')
        else:
            flash('電子郵件或密碼錯誤', 'danger')
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/restaurant/<int:restaurant_id>/orders', methods=['GET', 'POST'])
def manage_orders(restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Restaurants WHERE restaurant_id = %s', (restaurant_id,))
    restaurant = cursor.fetchone()
    if restaurant['name'] == '新餐廳':
        return redirect(url_for('restaurant_edit_profile'))
    query = """
        SELECT o.order_id, o.customer_id, o.total_price, o.status, u.name, o.restaurant_id
        FROM Orders o
        JOIN Users u ON o.customer_id = u.user_id
        WHERE o.restaurant_id = %s
    """

    cursor.execute(query, (restaurant_id,))
    pending_orders = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('vendor/manage_orders.html', restaurant_id=restaurant_id, orders=pending_orders)


@app.route('/restaurant/<int:restaurant_id>', methods=['GET'])
def restaurant_profile(restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Restaurants WHERE restaurant_id = %s', (restaurant_id,))
    user = cursor.fetchall()
    cursor.close()
    connection.close()
    print(user)
    return render_template('vendor/profile.html', restaurant_id=restaurant_id, user=user)

@app.route('/restaurant/<int:restaurant_id>/menu', methods=['GET'])
def view_menu(restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Menus WHERE restaurant_id = %s', (restaurant_id,))
    menus = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('vendor/menu.html', restaurant_id=restaurant_id, menus=menus)

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

@app.route('/accept_order/<int:order_id>/<int:restaurant_id>', methods=['POST'])
def accept_order(order_id, restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute('UPDATE Orders SET status = %s WHERE order_id = %s', ('pending', order_id))
        connection.commit()
        flash('接单成功并成功扣除库存', 'info')
    except Exception as e:
        # 捕获所有异常并回滚
        connection.rollback()
        app.logger.error(f"Error occurred: {str(e)}")  # 记录详细错误信息
        flash('接单失败，请稍后重试', 'danger')
    finally:
        cursor.close()
        connection.close()

    # 返回到订单管理页面
    return redirect(url_for('manage_orders', restaurant_id=restaurant_id))


#訂單完成通知取餐
@app.route('/notify_customer/<int:order_id>/<int:restaurant_id>', methods=['POST'])
def notify_customer(order_id, restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE Orders SET status = %s WHERE order_id = %s', ('notify', order_id))
    connection.commit()
    cursor.close()
    connection.close()
    flash('通知顧客取餐', 'info')
    return redirect(url_for('manage_orders', restaurant_id=restaurant_id))

#外送員已取餐
@app.route('/check_order/<int:order_id>/<int:restaurant_id>', methods=['POST'])
def check_order(order_id, restaurant_id):    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE Orders SET status = %s WHERE order_id = %s', ('get_completed', order_id))
    connection.commit()
    cursor.close()
    connection.close()
    flash('外送員已取餐', 'info')
    return redirect(url_for('manage_orders', restaurant_id=restaurant_id))

@app.route('/order_history/<int:restaurant_id>', methods=['GET'])
def order_history(restaurant_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Orders WHERE restaurant_id = %s', (restaurant_id,))
    orders = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('vendor/order_history.html', restaurant_id=restaurant_id, orders=orders)

#編輯個人資料
@app.route('/edit_profile', methods=['GET', 'POST'])
def restaurant_edit_profile():
    user_id = session.get('user_id')
    
    if not user_id:
        flash('請先登入', 'danger')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # 取得當前用戶資料
        cursor.execute("SELECT * FROM restaurants WHERE owner_id = %s", (user_id,))
        user = cursor.fetchone()

        if request.method == 'POST':
            name = request.form['name']
            address = request.form['address']
            phone = request.form['phone']

            if not user:
                # 如果找不到用戶資料，則插入新資料
                cursor.execute("INSERT INTO restaurants (name, address, phone, owner_id) VALUES (%s, %s, %s, %s)", (name, address, phone, user_id))
                connection.commit()

                # 插入後更新 users 表中的 restaurant_id
                cursor.execute("SELECT * FROM restaurants WHERE owner_id = %s", (user_id,))
                restaurant = cursor.fetchone()
                cursor.execute("UPDATE users SET restaurant_id = %s WHERE user_id = %s", (restaurant['restaurant_id'], user_id))
                connection.commit()

                flash('個人資料更新成功', 'success')
                print('個人資料更新成功')
                return redirect(url_for('restaurant_profile', restaurant_id=restaurant['restaurant_id']))  # 更新後跳轉回個人資料頁面

            else:
                # 如果用戶已經有餐廳資料，則更新資料
                cursor.execute("UPDATE restaurants SET name = %s, address = %s, phone = %s WHERE owner_id = %s", (name, address, phone, user_id))
                connection.commit()
                
                flash('個人資料更新成功', 'success')
                print('個人資料更新成功')
                return redirect(url_for('restaurant_profile', restaurant_id=user['restaurant_id']))  # 更新後跳轉回個人資料頁面

    except Exception as e:
        print(e)
        # 如果有錯誤，回滾並顯示錯誤
        connection.rollback()
        flash(f'更新失敗: {str(e)}', 'danger')

    finally:
        cursor.close()
        connection.close()

    return render_template('vendor/edit_profile.html', restaurant_id = user['restaurant_id'], user=user)



#外送員面板
@app.route('/delivery/<int:delivery_person_id>/dashboard', methods=['GET'])
def delivery_dashboard(delivery_person_id):
    if session.get('user_id') != delivery_person_id or session.get('role') != 'delivery_person':
        flash('無權訪問此頁面', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 查询已完成订单数量
    cursor.execute('''
        SELECT COUNT(*) AS completed_count
        FROM Orders
        WHERE delivery_person_id = %s AND status = 'completed'
    ''', (delivery_person_id,))
    completed_result = cursor.fetchone()
    completed_count = completed_result['completed_count'] if completed_result else 0

    # 查询外送员基本信息
    cursor.execute('SELECT * FROM Users WHERE user_id = %s', (delivery_person_id,))
    delivery_person = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('delivery/delivery_dashboard.html', delivery_person=delivery_person, completed_count=completed_count)



# 待配送订单
@app.route('/delivery/<int:delivery_person_id>/orders', methods=['GET'])
def view_delivery_orders(delivery_person_id):
    # 确认当前用户是否是对应的外送员
    if session.get('user_id') != delivery_person_id or session.get('role') != 'delivery_person':
        flash('無權查看此頁面', 'danger')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # 获取待配送订单（状态为 'notify' 且未被接单）
        cursor.execute("""
            SELECT o.order_id, o.customer_id, o.total_price, o.status, r.name AS restaurant_name
            FROM Orders o
            JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
            WHERE o.delivery_person_id IS NULL
        """)
        orders = cursor.fetchall()
        

        cursor.execute("""
            SELECT o.order_id, o.customer_id, o.total_price, o.status, r.name AS restaurant_name
            FROM Orders o
            JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
            WHERE o.delivery_person_id = %s
        """,(delivery_person_id,))
        get_orders=cursor.fetchall()
        print(orders)

        # 输出调试信息
        app.logger.debug(f"Orders fetched for delivery_person_id={delivery_person_id}: {orders}")

    except Exception as e:
        app.logger.error(f"Error fetching orders: {e}")
        orders = []
        flash('無法獲取訂單列表，請稍後再試', 'danger')

    finally:
        cursor.close()
        connection.close()

    return render_template('delivery/view_delivery_orders.html', orders=orders, delivery_person_id=delivery_person_id,get_orders=get_orders)


#接單
@app.route('/delivery/<int:delivery_person_id>/orders/<int:order_id>/accept', methods=['POST'])
def accept_delivery(delivery_person_id, order_id):
    if session.get('user_id') != delivery_person_id or session.get('role') != 'delivery_person':
        flash('無權執行此操作', 'danger')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE Orders 
            SET delivery_person_id = %s, status = %s 
            WHERE order_id = %s AND delivery_person_id IS NULL
        """, (delivery_person_id, 'get_completed', order_id))

        if cursor.rowcount > 0:
            connection.commit()
            flash('成功接單！', 'success')
        else:
            connection.rollback()
            flash('接單失敗，訂單可能已被接單或不存在', 'danger')

    except Exception as e:
        connection.rollback()
        app.logger.error(f"Error during order acceptance: {e}")
        flash(f'發生錯誤: {str(e)}', 'danger')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('view_delivery_orders', delivery_person_id=delivery_person_id))



#送達
@app.route('/delivery/<int:delivery_person_id>/orders/<int:order_id>/complete', methods=['POST'])
def complete_delivery(delivery_person_id, order_id):
    if session.get('user_id') != delivery_person_id or session.get('role') != 'delivery_person':
        flash('無權執行此操作', 'danger')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT status, delivery_person_id 
            FROM Orders 
            WHERE order_id = %s
        """, (order_id,))
        order = cursor.fetchone()


        cursor.execute("""
            UPDATE Orders 
            SET status = %s 
            WHERE order_id = %s AND delivery_person_id = %s AND status = %s
        """, ('delivery_completed', order_id, delivery_person_id, 'get_completed'))
        
        if cursor.rowcount > 0:
            connection.commit()
            flash('訂單已標記為送達！', 'success')
        else:
            connection.rollback()
            flash('更新失敗，可能訂單不存在或狀態不正確', 'danger')

    except Exception as e:
        connection.rollback()
        app.logger.error(f"Error during order completion: {e}")
        flash(f'發生錯誤: {str(e)}', 'danger')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('view_delivery_orders', delivery_person_id=delivery_person_id))





# 已完成订单
@app.route('/delivery/<int:delivery_person_id>/orders/completed', methods=['GET'])
def completed_orders(delivery_person_id):
    if session.get('user_id') != delivery_person_id or session.get('role') != 'delivery_person':
        flash('無權訪問此頁面', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.order_id, o.customer_id, o.total_price, r.name as restaurant_name
        FROM Orders o
        JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
        WHERE o.delivery_person_id = %s AND o.status = 'delivery_completed'
    """, (delivery_person_id,))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('delivery/completed_orders.html', orders=orders)

#個人簡介
@app.route('/delivery/<int:delivery_person_id>/profile', methods=['GET'])
def delivery_profile(delivery_person_id):
    if session.get('user_id') != delivery_person_id or session.get('role') != 'delivery_person':
        flash('無權訪問此頁面', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE user_id = %s", (delivery_person_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('delivery/delivery_profile.html', user=user)



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
        SELECT r.*, u.name AS owner_name 
        FROM restaurants r 
        INNER JOIN users u ON r.owner_id = u.user_id
    """)
    restaurants = cursor.fetchall()
    
    # 獲取所有外送員資訊
    cursor.execute("""
    SELECT *
    FROM users
    WHERE role ="delivery_person"
    """)
    delivery_persons = cursor.fetchall()
    
    # 獲取所有訂單資訊
    cursor.execute("""
        SELECT *
        FROM orders
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
        SELECT r.*, u.name AS owner_name, u.email AS owner_email
        FROM restaurants r
        INNER JOIN users u ON r.owner_id = u.user_id
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
    
    # 獲取所有 role 為 delivery_person 的使用者
    cursor.execute("""
        SELECT *
        FROM users 
        WHERE role = 'delivery_person'
    """)
    
    delivery_persons = cursor.fetchall()
    
    # 獲取每個外送員的訂單統計
    for person in delivery_persons:
        # 獲取已完成訂單數
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM orders
            WHERE delivery_person_id = %s AND status = 'all_completed'
        """, (person['user_id'],))
        completed = cursor.fetchone()
        person['completed_deliveries'] = completed['count'] if completed else 0
        
    
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
        SELECT *

        FROM orders 

    """)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('platform/orders.html', 
                         platform_id=platform_id,
                         orders=orders)

@app.route('/platform/<int:platform_id>/restaurant_detail/<int:restaurant_id>')
def restaurant_detail(platform_id, restaurant_id):
    if 'user_id' not in session or session['role'] != 'platform':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 獲取餐廳基本資訊
    cursor.execute("""
        SELECT r.*, u.name AS owner_name, u.email AS owner_email
        FROM restaurants r
        INNER JOIN users u ON r.owner_id = u.user_id
        WHERE r.restaurant_id = %s
    """, (restaurant_id,))
    restaurant = cursor.fetchone()
    
    # 獲取所有訂單
    cursor.execute("""
        SELECT o.*, u.name as customer_name
        FROM orders o
        INNER JOIN users u ON o.customer_id = u.user_id
        WHERE o.restaurant_id = %s
        AND o.status = 'all_completed'
        ORDER BY o.order_date DESC
    """, (restaurant_id,))
    all_orders = cursor.fetchall()
    
    # 獲取今日訂單
    cursor.execute("""
        SELECT o.*, u.name as customer_name
        FROM orders o
        INNER JOIN users u ON o.customer_id = u.user_id
        WHERE o.restaurant_id = %s
        AND o.status = 'all_completed'
        AND DATE(o.order_date) = CURDATE()
    """, (restaurant_id,))
    today_orders = cursor.fetchall()
    
    # 計算今日總金額
    today_total = sum(order['total_price'] for order in today_orders)
    
    cursor.close()
    conn.close()
    
    return render_template('platform/restaurant_detail.html',
                         platform_id=platform_id,
                         restaurant=restaurant,
                         all_orders=all_orders,
                         today_orders=today_orders,
                         today_total=today_total)

@app.route('/platform/<int:platform_id>/delivery_detail/<int:delivery_id>')
def delivery_detail(platform_id, delivery_id):
    if 'user_id' not in session or session['role'] != 'platform':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 獲取外送員基本資訊
    cursor.execute("""
        SELECT u.*
        FROM users u
        WHERE u.user_id = %s AND u.role = 'delivery_person'
    """, (delivery_id,))
    delivery_person = cursor.fetchone()
    print(delivery_person)
    
    # 獲取所有已完成訂單
    cursor.execute("""
        SELECT o.*, u.name as customer_name, r.name as restaurant_name
        FROM orders o
        INNER JOIN users u ON o.customer_id = u.user_id
        INNER JOIN restaurants r ON o.restaurant_id = r.restaurant_id
        WHERE o.delivery_person_id = %s
        AND o.status = 'all_completed'
        ORDER BY o.order_date DESC
    """, (delivery_id,))
    all_orders = cursor.fetchall()
    
    # 獲取今日已完成訂單
    cursor.execute("""
        SELECT o.*, u.name as customer_name, r.name as restaurant_name
        FROM orders o
        INNER JOIN users u ON o.customer_id = u.user_id
        INNER JOIN restaurants r ON o.restaurant_id = r.restaurant_id
        WHERE o.delivery_person_id = %s
        AND o.status = 'all_completed'
        AND DATE(o.order_date) = CURDATE()
    """, (delivery_id,))
    today_orders = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('platform/delivery_detail.html',
                         platform_id=platform_id,
                         delivery_person=delivery_person,
                         all_orders=all_orders,
                         today_orders=today_orders,
                         today_delivery_fee=len(today_orders) * 100)  # 每單100元
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
        "INSERT INTO Orders (customer_id, restaurant_id, status, total_price,delivery_person_id) VALUES (%s, %s, %s, %s, NUll)",
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