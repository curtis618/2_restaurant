-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2024-12-20 18:09:50
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `fooddelivery`
--

-- --------------------------------------------------------

--
-- 資料表結構 `deliveries`
--

CREATE TABLE `deliveries` (
  `delivery_id` int(11) NOT NULL,
  `order_id` int(11) DEFAULT NULL,
  `delivery_person_id` int(11) NOT NULL,
  `pickup_time` datetime DEFAULT NULL,
  `delivery_time` datetime DEFAULT NULL,
  `delivery_status` enum('pending','in_progress','completed') DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `deliverymanagementlogs`
--

CREATE TABLE `deliverymanagementlogs` (
  `log_id` int(11) NOT NULL,
  `platform_id` int(11) NOT NULL,
  `delivery_person_id` int(11) NOT NULL,
  `action` enum('add','update','delete') NOT NULL,
  `action_time` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `menus`
--

CREATE TABLE `menus` (
  `menu_id` int(11) NOT NULL,
  `restaurant_id` int(11) NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `stock_quantity` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `menus`
--

INSERT INTO `menus` (`menu_id`, `restaurant_id`, `item_name`, `description`, `price`, `stock_quantity`) VALUES
(1, 1, '豬血湯', '豬血根湯', 0.01, 110);

-- --------------------------------------------------------

--
-- 資料表結構 `orderchecklogs`
--

CREATE TABLE `orderchecklogs` (
  `log_id` int(11) NOT NULL,
  `platform_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `check_time` datetime DEFAULT current_timestamp(),
  `status_before` enum('pending','accepted','delivered') DEFAULT NULL,
  `status_after` enum('pending','accepted','delivered') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `orderitems`
--

CREATE TABLE `orderitems` (
  `order_item_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `menu_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `restaurant_id` int(11) NOT NULL,
  `status` enum('pending','accepted','delivered') DEFAULT 'pending',
  `order_date` datetime DEFAULT current_timestamp(),
  `total_price` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `payments`
--

CREATE TABLE `payments` (
  `payment_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_date` datetime DEFAULT current_timestamp(),
  `payment_method` enum('credit_card','cash') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `platformadmins`
--

CREATE TABLE `platformadmins` (
  `platform_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `restaurantmanagementlogs`
--

CREATE TABLE `restaurantmanagementlogs` (
  `log_id` int(11) NOT NULL,
  `platform_id` int(11) NOT NULL,
  `restaurant_id` int(11) NOT NULL,
  `action` enum('add','update','delete') NOT NULL,
  `action_time` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `restaurants`
--

CREATE TABLE `restaurants` (
  `restaurant_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `address` text NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `owner_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `restaurants`
--

INSERT INTO `restaurants` (`restaurant_id`, `name`, `address`, `phone`, `owner_id`) VALUES
(1, '麥噹噹', '我家吧八八八八八八八', '0902209875', 1);

-- --------------------------------------------------------

--
-- 資料表結構 `reviews`
--

CREATE TABLE `reviews` (
  `review_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `restaurant_id` int(11) NOT NULL,
  `rating` int(11) DEFAULT NULL CHECK (`rating` between 1 and 5),
  `comment` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('customer','vendor','delivery_person','platform') NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `restaurant_id` int(11) DEFAULT NULL,
  `delivery_person_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `users`
--

INSERT INTO `users` (`user_id`, `name`, `email`, `password`, `role`, `phone`, `restaurant_id`, `delivery_person_id`) VALUES
(1, 'user1', '1@1', '0', 'vendor', '0902209875', NULL, NULL),
(2, 'user2', '2@2', '0', 'vendor', NULL, NULL, NULL),
(3, 'user3', '3@3', '0', 'customer', NULL, NULL, NULL),
(4, 'user4', '4@4', '0', 'customer', NULL, NULL, NULL),
(6, 'user6', '6@6', '0', 'platform', NULL, NULL, NULL),
(13, 'user11', '11@11', '0', 'platform', NULL, NULL, NULL),
(15, 'user15', '15@15', '0', 'delivery_person', NULL, NULL, NULL);

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `deliveries`
--
ALTER TABLE `deliveries`
  ADD PRIMARY KEY (`delivery_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `delivery_person_id` (`delivery_person_id`);

--
-- 資料表索引 `deliverymanagementlogs`
--
ALTER TABLE `deliverymanagementlogs`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `platform_id` (`platform_id`),
  ADD KEY `delivery_person_id` (`delivery_person_id`);

--
-- 資料表索引 `menus`
--
ALTER TABLE `menus`
  ADD PRIMARY KEY (`menu_id`),
  ADD KEY `restaurant_id` (`restaurant_id`);

--
-- 資料表索引 `orderchecklogs`
--
ALTER TABLE `orderchecklogs`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `platform_id` (`platform_id`),
  ADD KEY `order_id` (`order_id`);

--
-- 資料表索引 `orderitems`
--
ALTER TABLE `orderitems`
  ADD PRIMARY KEY (`order_item_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `menu_id` (`menu_id`);

--
-- 資料表索引 `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `restaurant_id` (`restaurant_id`);

--
-- 資料表索引 `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`payment_id`),
  ADD KEY `order_id` (`order_id`);

--
-- 資料表索引 `platformadmins`
--
ALTER TABLE `platformadmins`
  ADD PRIMARY KEY (`platform_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- 資料表索引 `restaurantmanagementlogs`
--
ALTER TABLE `restaurantmanagementlogs`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `platform_id` (`platform_id`),
  ADD KEY `restaurant_id` (`restaurant_id`);

--
-- 資料表索引 `restaurants`
--
ALTER TABLE `restaurants`
  ADD PRIMARY KEY (`restaurant_id`),
  ADD KEY `owner_id` (`owner_id`);

--
-- 資料表索引 `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`review_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `restaurant_id` (`restaurant_id`);

--
-- 資料表索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `fk_restaurant_id` (`restaurant_id`),
  ADD KEY `fk_delivery_person_id` (`delivery_person_id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `deliveries`
--
ALTER TABLE `deliveries`
  MODIFY `delivery_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `deliverymanagementlogs`
--
ALTER TABLE `deliverymanagementlogs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `menus`
--
ALTER TABLE `menus`
  MODIFY `menu_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `orderchecklogs`
--
ALTER TABLE `orderchecklogs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `orderitems`
--
ALTER TABLE `orderitems`
  MODIFY `order_item_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `payments`
--
ALTER TABLE `payments`
  MODIFY `payment_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `platformadmins`
--
ALTER TABLE `platformadmins`
  MODIFY `platform_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `restaurantmanagementlogs`
--
ALTER TABLE `restaurantmanagementlogs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `restaurants`
--
ALTER TABLE `restaurants`
  MODIFY `restaurant_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `reviews`
--
ALTER TABLE `reviews`
  MODIFY `review_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `deliveries`
--
ALTER TABLE `deliveries`
  ADD CONSTRAINT `deliveries_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `deliveries_ibfk_2` FOREIGN KEY (`delivery_person_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `deliverymanagementlogs`
--
ALTER TABLE `deliverymanagementlogs`
  ADD CONSTRAINT `deliverymanagementlogs_ibfk_1` FOREIGN KEY (`platform_id`) REFERENCES `platformadmins` (`platform_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `deliverymanagementlogs_ibfk_2` FOREIGN KEY (`delivery_person_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `menus`
--
ALTER TABLE `menus`
  ADD CONSTRAINT `menus_ibfk_1` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `orderchecklogs`
--
ALTER TABLE `orderchecklogs`
  ADD CONSTRAINT `orderchecklogs_ibfk_1` FOREIGN KEY (`platform_id`) REFERENCES `platformadmins` (`platform_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `orderchecklogs_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `orderitems`
--
ALTER TABLE `orderitems`
  ADD CONSTRAINT `orderitems_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `orderitems_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `menus` (`menu_id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `restaurantmanagementlogs`
--
ALTER TABLE `restaurantmanagementlogs`
  ADD CONSTRAINT `restaurantmanagementlogs_ibfk_1` FOREIGN KEY (`platform_id`) REFERENCES `platformadmins` (`platform_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `restaurantmanagementlogs_ibfk_2` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `restaurants`
--
ALTER TABLE `restaurants`
  ADD CONSTRAINT `restaurants_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `reviews_ibfk_3` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `fk_delivery_person_id` FOREIGN KEY (`delivery_person_id`) REFERENCES `deliveries` (`delivery_person_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`restaurant_id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
