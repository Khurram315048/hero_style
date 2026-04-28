-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: hero_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admins` (
  `admin_id` int(11) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) DEFAULT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `is_deleted` int(11) DEFAULT 0,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `admins_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (1,1,'Muhammad','Khurram','khurram','saleemkhurram420@gmail.com','scrypt:32768:8:1$5gXs6V5LkbPSIrBq$7a6f64ab24e2665e22bf5b73805a14ec38eb4e377b5e1092eb9cc6f351e7400fe8fd0997b9b49f011a89665cd35a6b0c9e3d96acdac9c18afaf782e83dfe03db',0),(2,1,'Adil','Bashir','adilasim','adilcentral123@gmail.com','scrypt:32768:8:1$652ie3QOzPn2L3dT$da58b4e25ccefb0db3016a758fc42954397880ded71c5f34ec8b68cb7d20b0f1f9',0);
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cart_items` (
  `item_id` int(11) NOT NULL AUTO_INCREMENT,
  `cart_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `price_at_add` decimal(10,2) NOT NULL,
  `added_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`item_id`),
  UNIQUE KEY `cart_id` (`cart_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`cart_id`) REFERENCES `carts` (`cart_id`) ON DELETE CASCADE,
  CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
INSERT INTO `cart_items` VALUES (1,1,14,1,1099.00,'2026-04-17 15:17:05'),(3,3,13,1,11999.00,'2026-04-18 03:57:06');
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carts`
--

DROP TABLE IF EXISTS `carts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `carts` (
  `cart_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `session_id` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`cart_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `carts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts`
--

LOCK TABLES `carts` WRITE;
/*!40000 ALTER TABLE `carts` DISABLE KEYS */;
INSERT INTO `carts` VALUES (1,NULL,'95992d67-40c8-433f-a1fa-87e1e42aed7c','2026-04-17 15:17:04','2026-04-17 15:17:04'),(3,NULL,'249c8293-3b47-4179-9dfb-340a1aec0dfd','2026-04-18 03:57:06','2026-04-18 03:57:06'),(7,NULL,'dcc87f27-e703-404a-b4fb-22272dc7ea9b','2026-04-25 06:17:47','2026-04-25 06:17:47');
/*!40000 ALTER TABLE `carts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categories` (
  `category_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'smart watches','watches that give digital vision to you and your life.',1,'2026-03-27 08:01:36'),(2,'metal watches','watches that give bold and uniqueness to the life.',1,'2026-03-27 08:02:48'),(3,'leather watches','watches that are vintage and heritage for the life.',1,'2026-03-27 08:03:34'),(4,'EarBuds','Ear Buds that give the hearing of deep listening.',1,'2026-04-06 15:47:07');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forms`
--

DROP TABLE IF EXISTS `forms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forms` (
  `form_id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) DEFAULT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `form_path` varchar(255) DEFAULT NULL,
  `overall_rating` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`form_id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `forms_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forms`
--

LOCK TABLES `forms` WRITE;
/*!40000 ALTER TABLE `forms` DISABLE KEYS */;
/*!40000 ALTER TABLE `forms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_details`
--

DROP TABLE IF EXISTS `order_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `order_details` (
  `order_detail_id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `product_amount` decimal(10,2) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `discount_per_item` decimal(10,2) DEFAULT 0.00,
  `subtotal` decimal(10,2) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`order_detail_id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `order_details_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT `order_details_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_details`
--

LOCK TABLES `order_details` WRITE;
/*!40000 ALTER TABLE `order_details` DISABLE KEYS */;
INSERT INTO `order_details` VALUES (1,1,2,1199.00,1,50.00,1199.00,'2026-04-17 15:24:29'),(2,2,17,5999.00,1,50.00,5999.00,'2026-04-18 04:25:20'),(3,3,1,11999.00,1,50.00,11999.00,'2026-04-18 04:45:31'),(4,4,3,1299.00,1,0.00,1299.00,'2026-04-18 07:44:08'),(5,4,20,2999.00,1,0.00,2999.00,'2026-04-18 07:44:08'),(6,4,15,53999.00,1,0.00,53999.00,'2026-04-18 07:44:08');
/*!40000 ALTER TABLE `order_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_item_returns`
--

DROP TABLE IF EXISTS `order_item_returns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `order_item_returns` (
  `return_id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `order_detail_id` int(11) NOT NULL,
  `reason` varchar(500) DEFAULT NULL,
  `status` enum('requested','approved','rejected') DEFAULT 'requested',
  `requested_at` datetime DEFAULT current_timestamp(),
  `resolved_at` datetime DEFAULT NULL,
  PRIMARY KEY (`return_id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `order_item_returns_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_item_returns`
--

LOCK TABLES `order_item_returns` WRITE;
/*!40000 ALTER TABLE `order_item_returns` DISABLE KEYS */;
INSERT INTO `order_item_returns` VALUES (1,4,4,'this item is not good.','requested','2026-04-20 19:02:57','2026-04-20 19:02:57'),(3,4,6,'bad quality','rejected','2026-04-20 19:32:31','2026-04-20 19:32:31');
/*!40000 ALTER TABLE `order_item_returns` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_payments`
--

DROP TABLE IF EXISTS `order_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `order_payments` (
  `payment_id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `payment_method` enum('COD','card','bank_transfer','JazzCash','EasyPaisa') NOT NULL,
  `transaction_id` varchar(255) DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` enum('pending','paid','failed','refunded') DEFAULT 'pending',
  `paid_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`payment_id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `order_payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_payments`
--

LOCK TABLES `order_payments` WRITE;
/*!40000 ALTER TABLE `order_payments` DISABLE KEYS */;
INSERT INTO `order_payments` VALUES (1,1,'JazzCash',NULL,1449.00,'pending',NULL,'2026-04-17 15:24:29'),(2,2,'JazzCash',NULL,6249.00,'pending',NULL,'2026-04-18 04:25:20'),(3,3,'JazzCash',NULL,10799.00,'pending',NULL,'2026-04-18 04:45:31'),(4,4,'bank_transfer',NULL,58297.00,'pending',NULL,'2026-04-18 07:44:08');
/*!40000 ALTER TABLE `order_payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_returns`
--

DROP TABLE IF EXISTS `order_returns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `order_returns` (
  `return_id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `reason` text NOT NULL,
  `status` enum('requested','approved','rejected','received','refunded') DEFAULT 'requested',
  `requested_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `resolved_at` timestamp NULL DEFAULT NULL,
  `is_cancelled` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`return_id`),
  KEY `return_order_fk` (`order_id`),
  CONSTRAINT `return_order_fk` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_returns`
--

LOCK TABLES `order_returns` WRITE;
/*!40000 ALTER TABLE `order_returns` DISABLE KEYS */;
INSERT INTO `order_returns` VALUES (1,3,'i am testing the return cancel method.','requested','2026-04-23 14:02:01','2026-04-20 13:28:24',1);
/*!40000 ALTER TABLE `order_returns` ENABLE KEYS */;
UNLOCK TABLES;
