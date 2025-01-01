# 軟體工程期末作業
* [git repo](https://github.com/curtis618/2_restaurant)
## 資料庫
![Untitled](https://hackmd.io/_uploads/Sk0Zq1XUkl.png)
:::spoiler SQL程式碼
```MySQL=
CREATE DATABASE FoodDelivery;

USE FoodDelivery;

-- 使用者表：包括商家、顧客、送貨小哥
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'vendor', 'platform', 'delivery_person') NOT NULL,
    phone VARCHAR(15),
    restaurant_id INT DEFAULT NULL,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id) ON DELETE SET NULL
);

-- 餐廳表：存儲餐廳資訊
CREATE TABLE Restaurants (
    restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(15),
    owner_id INT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 菜單表：存儲餐廳的菜單資訊
CREATE TABLE Menus (
    menu_id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id) ON DELETE CASCADE
);

-- 訂單表：存儲顧客的訂單資訊
CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    delivery_person_id INT NOT NULL,
    status ENUM('accepted', 'pending', 'notify', 'get_completed', 'delivery_completed', 'all_completed') DEFAULT 'accepted',
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id) ON DELETE CASCADE
);

-- 訂單詳情表：存儲訂單的每個項目
CREATE TABLE OrderItems (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES Menus(menu_id) ON DELETE CASCADE
);

-- 評價表：存儲顧客對餐廳的評價
CREATE TABLE Reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    customer_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id) ON DELETE CASCADE
);
```
:::
### 餐廳：楊期閎
:::info
* 菜單上架
* 確認收單
* 通知取餐
:::
### 外送員：李晉瑋
:::info
* 查看待送訂單
* 接單
* 取貨
* 送達簽收
:::
### 平台：孫翊軒
:::info
* 結算商家、客戶、小哥的款項出帳
:::
### 客戶：廖志賢
:::info
* 查看菜單
* 下單
* 收貨
* 給評

:::

```mysql=
CREATE DATABASE FoodDelivery;

USE FoodDelivery;

-- 使用者表：包括商家、顧客、送貨小哥
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'vendor','platform', 'delivery_person') NOT NULL,
    phone VARCHAR(15)
);

-- 餐廳表：存儲餐廳資訊
CREATE TABLE Restaurants (
    restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(15),
    owner_id INT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 菜單表：存儲餐廳的菜單資訊
CREATE TABLE Menus (
    menu_id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id) ON DELETE CASCADE
);

-- 訂單表：存儲顧客的訂單資訊
CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    delivery_person_id INT NOT NULL,
    status ENUM('accepted','pending','notify','get_completed','delivery_completed','all_completed'
) DEFAULT 'accepted',
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id) ON DELETE CASCADE
);

-- 訂單詳情表：存儲訂單的每個項目
CREATE TABLE OrderItems (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES Menus(menu_id) ON DELETE CASCADE
);


-- 評價表：存儲顧客對餐廳的評價
CREATE TABLE Reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    customer_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id) ON DELETE CASCADE
);

```

選取fooddelivery資料庫後，在SQL中執行:
```mysql=
-- 在users中加入restaurant_id的外鍵
ALTER TABLE USERS
ADD COLUMN restaurant_id INT DEFAULT NULL,
ADD CONSTRAINT fk_restaurant_id
FOREIGN KEY (restaurant_id) REFERENCES RESTAURANTS(restaurant_id)
ON DELETE SET NULL;
```

