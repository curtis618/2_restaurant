-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： localhost
-- 產生時間： 2024 年 12 月 09 日 17:07
-- 伺服器版本： 9.0.1
-- PHP 版本： 8.4.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `FoodDelivery`
--

-- --------------------------------------------------------

--
-- 資料表結構 `Menus`
--

CREATE TABLE `Menus` (
  `menu_id` int NOT NULL,
  `restaurant_id` int NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `description` text,
  `price` decimal(10,2) NOT NULL,
  `stock_quantity` int DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 傾印資料表的資料 `Menus`
--

INSERT INTO `Menus` (`menu_id`, `restaurant_id`, `item_name`, `description`, `price`, `stock_quantity`) VALUES
(1, 1, 'dog', '11', 11.00, 11),
(4, 1, 'cat', 'salty', 150.00, 250);

-- --------------------------------------------------------

--
-- 資料表結構 `OrderItems`
--

CREATE TABLE `OrderItems` (
  `order_item_id` int NOT NULL,
  `order_id` int NOT NULL,
  `menu_id` int NOT NULL,
  `quantity` int NOT NULL,
  `price` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 傾印資料表的資料 `OrderItems`
--

INSERT INTO `OrderItems` (`order_item_id`, `order_id`, `menu_id`, `quantity`, `price`) VALUES
(3, 1, 1, 2, 22.00),
(5, 1, 4, 2, 200.00),
(6, 2, 1, 2, 22.00),
(7, 3, 4, 2, 200.00),
(8, 4, 1, 10, 220.00),
(9, 4, 4, 10, 2000.00);

-- --------------------------------------------------------

--
-- 資料表結構 `Orders`
--

CREATE TABLE `Orders` (
  `order_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `restaurant_id` int NOT NULL,
  `status` enum('pending','accepted','delivered') DEFAULT 'pending',
  `order_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `total_price` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 傾印資料表的資料 `Orders`
--

INSERT INTO `Orders` (`order_id`, `customer_id`, `restaurant_id`, `status`, `order_date`, `total_price`) VALUES
(1, 1, 1, 'delivered', '2024-12-08 00:12:49', 100.00),
(2, 1, 1, 'delivered', '2024-12-08 00:12:52', 100.00),
(3, 1, 1, 'accepted', '2024-12-09 22:31:02', 200.00),
(4, 1, 1, 'accepted', '2024-12-09 22:31:06', 200.00);

-- --------------------------------------------------------

--
-- 資料表結構 `Restaurants`
--

CREATE TABLE `Restaurants` (
  `restaurant_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `address` text NOT NULL,
  `phone` varchar(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- 傾印資料表的資料 `Restaurants`
--

INSERT INTO `Restaurants` (`restaurant_id`, `name`, `address`, `phone`) VALUES
(1, '黎田鹽酥雞', '大學路ㄧ號', '09000000');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `Menus`
--
ALTER TABLE `Menus`
  ADD PRIMARY KEY (`menu_id`);

--
-- 資料表索引 `OrderItems`
--
ALTER TABLE `OrderItems`
  ADD PRIMARY KEY (`order_item_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `menu_id` (`menu_id`);

--
-- 資料表索引 `Orders`
--
ALTER TABLE `Orders`
  ADD PRIMARY KEY (`order_id`);

--
-- 資料表索引 `Restaurants`
--
ALTER TABLE `Restaurants`
  ADD PRIMARY KEY (`restaurant_id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `Menus`
--
ALTER TABLE `Menus`
  MODIFY `menu_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `OrderItems`
--
ALTER TABLE `OrderItems`
  MODIFY `order_item_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `Orders`
--
ALTER TABLE `Orders`
  MODIFY `order_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `Restaurants`
--
ALTER TABLE `Restaurants`
  MODIFY `restaurant_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `OrderItems`
--
ALTER TABLE `OrderItems`
  ADD CONSTRAINT `orderitems_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `Orders` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `orderitems_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `Menus` (`menu_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
