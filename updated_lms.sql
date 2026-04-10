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
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
INSERT INTO `cart_items` VALUES (1,1,12,1,1699.00,'2026-03-30 10:12:09'),(2,2,13,1,11999.00,'2026-03-30 10:12:17'),(3,3,3,1,1299.00,'2026-03-30 11:08:27'),(4,4,1,1,11999.00,'2026-03-30 11:14:26'),(5,5,5,1,1099.00,'2026-04-09 13:13:03'),(6,5,9,1,22999.00,'2026-04-09 13:13:09'),(7,5,18,1,3999.00,'2026-04-09 13:13:16'),(8,6,8,1,33999.00,'2026-04-09 13:15:48'),(9,7,13,1,11999.00,'2026-04-09 13:17:42'),(12,9,17,1,5999.00,'2026-04-09 13:44:27'),(13,10,6,1,32999.00,'2026-04-09 13:48:52'),(14,11,19,1,8499.00,'2026-04-10 05:40:23'),(15,11,9,1,22999.00,'2026-04-10 05:41:07'),(16,12,5,2,1099.00,'2026-04-10 05:41:35'),(17,13,12,1,1699.00,'2026-04-10 06:01:14'),(26,16,19,1,8499.00,'2026-04-10 06:34:19');
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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts`
--

LOCK TABLES `carts` WRITE;
/*!40000 ALTER TABLE `carts` DISABLE KEYS */;
INSERT INTO `carts` VALUES (1,NULL,'8d36d5f6-6c65-4306-aee6-5a99f7293817','2026-03-30 10:12:09','2026-03-30 10:12:09'),(2,NULL,'641d2a65-5929-4df4-b7b0-0025c70244cd','2026-03-30 10:12:17','2026-03-30 10:12:17'),(3,NULL,NULL,'2026-03-30 11:08:27','2026-03-30 11:08:27'),(4,NULL,NULL,'2026-03-30 11:14:26','2026-03-30 11:14:26'),(5,NULL,'4f47e5cc-7bee-4af1-b4ca-9c6f266b46c7','2026-04-09 13:13:03','2026-04-09 13:13:03'),(6,NULL,'f3985dfc-a9b7-40cd-a98a-cc0d721913c3','2026-04-09 13:15:48','2026-04-09 13:15:48'),(7,NULL,'52545bd2-0194-455e-8206-a792f5d79307','2026-04-09 13:17:42','2026-04-09 13:17:42'),(9,NULL,'1e1bb28b-ad21-4e02-8d70-b26b323023f1','2026-04-09 13:44:26','2026-04-09 13:44:26'),(10,NULL,'3837face-e072-4e63-8184-99d7709f9f4d','2026-04-09 13:48:51','2026-04-09 13:48:51'),(11,NULL,'ce726656-7315-49e3-be90-ab4c6ee8e936','2026-04-10 05:40:23','2026-04-10 05:40:23'),(12,NULL,'5d27489b-d1b9-4b3b-adc2-4480ea728a95','2026-04-10 05:41:35','2026-04-10 05:41:35'),(13,NULL,'566abe56-20b7-452e-a94c-3015e6f1446f','2026-04-10 06:01:14','2026-04-10 06:01:14'),(14,NULL,'910c527b-d62b-4d24-a61d-6499b81da392','2026-04-10 06:03:49','2026-04-10 06:03:49'),(16,NULL,'2f8f7bf6-b388-496b-ab47-d4b7a205e76b','2026-04-10 06:34:19','2026-04-10 06:34:19');
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forms`
--

LOCK TABLES `forms` WRITE;
/*!40000 ALTER TABLE `forms` DISABLE KEYS */;
INSERT INTO `forms` VALUES (2,NULL,'adfs','aa@gmail.com','9315042401','return','dfhhd','adfgbbhhbbbbbapr','static/uploads/support_forms\\sample.PNG',2);
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_details`
--

LOCK TABLES `order_details` WRITE;
/*!40000 ALTER TABLE `order_details` DISABLE KEYS */;
INSERT INTO `order_details` VALUES (1,1,4,1149.00,1,0.00,1149.00,'2026-03-31 06:38:36'),(2,2,4,1149.00,1,0.00,1149.00,'2026-03-31 06:53:16'),(3,3,14,1099.00,1,0.00,1099.00,'2026-03-31 06:54:35'),(4,3,11,2599.00,1,0.00,2599.00,'2026-03-31 06:54:35'),(5,4,11,2599.00,2,0.00,5198.00,'2026-03-31 12:01:26'),(6,4,7,31999.00,1,0.00,31999.00,'2026-03-31 12:01:26'),(7,5,2,1199.00,1,0.00,1199.00,'2026-04-02 13:01:25'),(8,6,10,33999.00,1,0.00,33999.00,'2026-04-02 14:08:12'),(9,7,1,11999.00,2,0.00,23998.00,'2026-04-09 13:24:06'),(10,7,7,31999.00,1,0.00,31999.00,'2026-04-09 13:24:06'),(11,8,10,33999.00,1,50.00,33999.00,'2026-04-10 06:17:51');
/*!40000 ALTER TABLE `order_details` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_payments`
--

LOCK TABLES `order_payments` WRITE;
/*!40000 ALTER TABLE `order_payments` DISABLE KEYS */;
INSERT INTO `order_payments` VALUES (1,1,'JazzCash',NULL,1399.00,'pending',NULL,'2026-03-31 06:38:36'),(2,2,'JazzCash',NULL,1399.00,'pending',NULL,'2026-03-31 06:53:16'),(3,3,'EasyPaisa',NULL,3948.00,'pending',NULL,'2026-03-31 06:54:35'),(4,4,'COD',NULL,37197.00,'pending',NULL,'2026-03-31 12:01:26'),(5,5,'bank_transfer',NULL,1449.00,'pending',NULL,'2026-04-02 13:01:26'),(6,6,'JazzCash',NULL,33999.00,'pending',NULL,'2026-04-02 14:08:12'),(7,7,'EasyPaisa',NULL,55997.00,'pending',NULL,'2026-04-09 13:24:06'),(8,8,'EasyPaisa',NULL,33999.00,'pending',NULL,'2026-04-10 06:17:51');
/*!40000 ALTER TABLE `order_payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `order_number` varchar(50) NOT NULL,
  `status` enum('pending','confirmed','shipped','delivered','cancelled','returned') DEFAULT 'pending',
  `subtotal` decimal(10,2) NOT NULL,
  `discount_amount` decimal(10,2) DEFAULT 0.00,
  `promo_code` varchar(100) DEFAULT NULL,
  `shipping_charges` decimal(10,2) DEFAULT 0.00,
  `total_amount` decimal(10,2) NOT NULL,
  `shipping_address` text NOT NULL,
  `billing_address` text DEFAULT NULL,
  `ordered_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `is_deleted` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`order_id`),
  UNIQUE KEY `order_number` (`order_number`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,NULL,'HW-A3B93B94','pending',1149.00,0.00,NULL,250.00,1399.00,'Muhammad Khurram, 03150484043, Gulshan Iqbal Colony Qasim Bela Multan, Multan 6500',NULL,'2026-03-31 06:38:36','2026-03-31 06:38:36',0),(2,1,'HW-A07AC338','pending',1149.00,0.00,NULL,250.00,1399.00,'Muhammad Khurram, 03150484043, Gulshan Iqbal Colony Qasim Bela Multan, Multan 6500',NULL,'2026-03-31 06:53:16','2026-03-31 06:53:16',0),(3,3,'HW-09026DC9','pending',3698.00,0.00,NULL,250.00,3948.00,'khurram saleem, 03150484041, Main Street Dhamaka Chowk Near Army Wall Qasim Bela Multan Cantt, Multan 6500',NULL,'2026-03-31 06:54:35','2026-03-31 06:54:35',0),(4,4,'HW-86FB80AB','pending',37197.00,0.00,NULL,0.00,37197.00,'Umair Khurram,03150494042,Fiasal Park Multan,Multan 6500',NULL,'2026-03-31 12:01:26','2026-03-31 12:01:26',0),(5,5,'HW-BADAFC21','pending',1199.00,0.00,NULL,250.00,0.00,'1449','Gulshan Iqbal Colony Qasim Bela Multan,Multan 6500','2026-04-02 13:01:25','2026-04-02 13:01:25',0),(6,6,'HW-5084486C','pending',33999.00,0.00,NULL,0.00,33999.00,'Gulshan Iqbal Colony Qasim Bela Multan,Multan 6500','Gulshan Iqbal Colony Qasim Bela Multan,Multan 6500','2026-04-02 14:08:12','2026-04-02 14:08:12',0),(7,7,'HW-F5C3CA74','pending',55997.00,0.00,NULL,0.00,55997.00,'Gulshan Iqbal Colony Qasim Bela Multan, Multan 6500','Gulshan Iqbal Colony Qasim Bela Multan, Multan 6500','2026-04-09 13:24:06','2026-04-09 13:24:06',0),(8,8,'HW-2DE892E8','pending',33999.00,0.00,NULL,0.00,33999.00,'Western Fort Colony, Near Army wall Dhmaka Chowk Qasim Bela Multan,Multan 6500','Western Fort Colony, Near Army wall Dhmaka Chowk Qasim Bela Multan,Multan 6500','2026-04-10 06:17:51','2026-04-10 06:17:51',0);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_details`
--

DROP TABLE IF EXISTS `product_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `product_details` (
  `detail_id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `short_description` varchar(500) DEFAULT NULL,
  `long_description` text DEFAULT NULL,
  `display_type` varchar(100) DEFAULT NULL,
  `display_size` varchar(50) DEFAULT NULL,
  `brightness_nits` int(11) DEFAULT NULL,
  `battery_life` varchar(100) DEFAULT NULL,
  `connectivity` text DEFAULT NULL,
  `strap_material` varchar(100) DEFAULT NULL,
  `case_material` varchar(100) DEFAULT NULL,
  `water_resistance` varchar(100) DEFAULT NULL,
  `weight` varchar(50) DEFAULT NULL,
  `warranty_months` int(11) DEFAULT 12,
  `is_always_on_display` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`detail_id`),
  UNIQUE KEY `product_id` (`product_id`),
  CONSTRAINT `product_details_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_details`
--

LOCK TABLES `product_details` WRITE;
/*!40000 ALTER TABLE `product_details` DISABLE KEYS */;
INSERT INTO `product_details` VALUES (1,1,'Feature-packed smartwatch with vibrant display and smart health suite','SKIM is a powerful smartwatch designed for the modern lifestyle. Packed with health tracking, smart notifications and a vivid display, it keeps you connected and active throughout the day.','AMOLED','1.43 inch',600,'7 days','Calls, texts, social media alerts','Silicone','Zinc Alloy','Splash Proof','45g',12,1,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(2,2,'Slim smartwatch with elegant design and essential smart features','SNIX combines a sleek slim profile with smart functionality. Ideal for daily use with fitness tracking, notifications and a long lasting battery that keeps up with your pace.','TFT LCD','1.39 inch',500,'5 days','Calls, texts, social media alerts','Silicone','Aluminum Alloy','Splash Proof','40g',12,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(3,3,'Smart health companion with advanced fitness tracking features','SNIQ is built for the health conscious user offering real time heart rate monitoring, sleep analysis, step tracking and multiple sport modes all wrapped in a comfortable lightweight build.','IPS LCD','1.4 inch',450,'6 days','Calls, texts, health alerts','Silicone','Plastic Frame','Splash Proof','38g',12,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(4,4,'Bold smartwatch with large display and extended battery life','SNIM features a large bold display with crisp visuals, extended battery performance and a comprehensive smart suite making it the perfect all day companion for busy individuals.','AMOLED','1.5 inch',550,'8 days','Calls, texts, social media, stock alerts','Vegan Leather','Chrome Plated','Splash Proof','47g',12,1,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(5,5,'Affordable smartwatch with essential features for everyday use','SNIN delivers the essential smartwatch experience at an accessible price point. Stay connected with notifications, track your daily activity and monitor your health without breaking the bank.','TFT LCD','1.3 inch',380,'4 days','Calls, texts alerts','Silicone','ABS Plastic','Splash Proof','35g',6,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(6,6,'Premium mechanical watch with refined craftsmanship and timeless design','MURREN is a statement of sophistication. Crafted with precision mechanics and a refined aesthetic, this timepiece is built for those who appreciate the art of traditional watchmaking.','Analog','40mm',NULL,'Mechanical — no battery','None','Genuine Leather','Stainless Steel','3 ATM Water Resistant','95g',24,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(7,7,'Classic mechanical watch with stainless steel bracelet and bold dial','MURRAM brings bold presence to your wrist with a striking dial design and durable stainless steel construction. A classic timepiece that transitions effortlessly from office to evening.','Analog','42mm',NULL,'Mechanical — no battery','None','Stainless Steel Bracelet','Stainless Steel','5 ATM Water Resistant','110g',24,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(8,8,'Luxury mechanical watch with sapphire glass and premium finish','MULEN is engineered for the discerning wearer. Featuring scratch resistant sapphire crystal glass, a premium dial finish and precise mechanical movement that reflects true horological excellence.','Analog','41mm',NULL,'Mechanical — no battery','None','Crocodile Textured Leather','Titanium','10 ATM Water Resistant','100g',36,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(9,9,'Elegant dress watch with slim profile and minimal dial design','MUAREN is the perfect dress watch for formal occasions. Its ultra slim profile, clean minimal dial and fine leather strap make it an understated yet powerful style statement.','Analog','38mm',NULL,'Quartz — SR626SW battery 2 years','None','Genuine Leather','Rose Gold Plated','3 ATM Water Resistant','70g',12,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(10,10,'Sports inspired mechanical watch with chronograph function','MURGEN combines sporty aesthetics with mechanical precision. The chronograph sub-dials, tachymeter bezel and robust build make it the ideal watch for those who live an active lifestyle.','Analog Chronograph','44mm',NULL,'Mechanical — no battery','None','Rubber','Brushed Stainless Steel','10 ATM Water Resistant','130g',24,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(11,11,'Casual leather strap watch with clean dial for everyday wear','LIXES is a relaxed everyday watch featuring a soft genuine leather strap and a clean uncluttered dial. Simple, comfortable and reliable for daily casual wear.','Analog','36mm',NULL,'Quartz — SR626SW battery 2 years','None','Genuine Leather','Zinc Alloy','3 ATM Water Resistant','60g',12,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(12,12,'Slim leather watch with vintage inspired design','LIUNEN draws inspiration from vintage watch design with a slim case, warm toned dial and supple leather strap that ages beautifully over time.','Analog','34mm',NULL,'Quartz — SR626SW battery 2 years','None','Vintage Leather','Brass','3 ATM Water Resistant','55g',12,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(13,13,'Premium leather strap watch with large bold dial and date function','LEAN is built for those who want presence. A large bold dial, date display and premium leather strap deliver a confident look suitable for both professional and casual settings.','Analog with Date','42mm',NULL,'Quartz — CR2032 battery 2 years','None','Full Grain Leather','Stainless Steel','5 ATM Water Resistant','85g',12,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(14,14,'Minimalist leather watch with two tone design and slim case','LEATH is for the minimalist. A clean two tone dial, ultra slim case and fine leather strap create a watch that is quietly confident and endlessly versatile.','Analog','35mm',NULL,'Quartz — SR626SW battery 2 years','None','Slim Leather','Alloy','3 ATM Water Resistant','50g',12,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(15,15,'High end leather watch with automatic movement and exhibition caseback','LEAD is a showcase of mechanical artistry. The exhibition caseback reveals the intricate automatic movement within, paired with a hand stitched leather strap for ultimate luxury.','Analog Automatic','40mm',NULL,'Automatic — self winding no battery','None','Hand Stitched Leather','Sapphire Crystal Case','5 ATM Water Resistant','105g',36,0,'2026-03-28 06:05:36','2026-03-28 06:05:36'),(16,16,'Premium wireless earbuds with active noise cancellation','Elite Pro earbuds with ANC, 6-mic array, Bluetooth 5.3, crystal clear sound',NULL,NULL,NULL,'8 hours (36 with case)','Bluetooth 5.3, AAC',NULL,NULL,'IPX4','4.2g',24,0,'2026-04-06 15:54:42','2026-04-06 15:54:42'),(17,17,'High-quality earbuds with enhanced bass','Sound Max delivers powerful bass and clear treble with 6-mic array for noise cancellation',NULL,NULL,NULL,'7 hours (28 with case)','Bluetooth 5.2, aptX',NULL,NULL,'IPX3','5g',12,0,'2026-04-06 15:54:42','2026-04-06 15:54:42'),(18,18,'Sports earbuds with secure fit ear hooks','Fit Sport designed for workouts with ear hooks, sweat resistant, perfect for running and gym',NULL,NULL,NULL,'6 hours (20 with case)','Bluetooth 5.0, AAC',NULL,NULL,'IPX5','5.5g',12,0,'2026-04-06 15:54:42','2026-04-06 15:54:42'),(19,19,'Studio-grade earbuds for professionals','Studio Pro with 360° audio, 24-bit LDAC, gaming mode, low latency, for creators and gamers',NULL,NULL,NULL,'9 hours (40 with case)','Bluetooth 5.3, LDAC, aptX HD',NULL,NULL,'IPX4','3.8g',24,0,'2026-04-06 15:54:42','2026-04-06 15:54:42'),(20,20,'Ultra-lightweight compact earbuds','Lite Compact ultra-lightweight design, quick charge, balanced sound for everyday use',NULL,NULL,NULL,'5 hours (18 with case)','Bluetooth 5.0, AAC',NULL,NULL,'IPX2','3.5g',12,0,'2026-04-06 15:54:42','2026-04-06 15:54:42');
/*!40000 ALTER TABLE `product_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_images`
--

DROP TABLE IF EXISTS `product_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `product_images` (
  `image_id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `alt_text` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `width` int(11) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`image_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_images_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_images`
--

LOCK TABLES `product_images` WRITE;
/*!40000 ALTER TABLE `product_images` DISABLE KEYS */;
INSERT INTO `product_images` VALUES (1,1,'/static/uploads/smart_watches/img1a.png','Smart Watch',1,800,800,'2026-03-28 06:14:48'),(2,2,'/static/uploads/smart_watches/img2a.png','smart black watch',1,800,700,'2026-03-28 06:18:49'),(3,3,'/static/uploads/smart_watches/img3a.png','smart blue watch',1,800,800,'2026-03-28 06:49:31'),(4,4,'/static/uploads/smart_watches/img4a.png','smart purple watch',1,800,800,'2026-03-28 06:50:35'),(5,5,'/static/uploads/smart_watches/img5a.png','smart silver watch',1,800,800,'2026-03-28 06:51:08'),(6,6,'/static/uploads/metal_watches/img1m.png','Silver Metal Watch',1,800,800,'2026-03-28 09:08:23'),(7,7,'/static/uploads/metal_watches/img2m.png','Silver Blue Metal Watch',1,800,800,'2026-03-28 09:15:55'),(8,8,'/static/uploads/metal_watches/img3m.png','Silver Black Metal Watch',1,800,800,'2026-03-28 09:15:55'),(9,9,'/static/uploads/metal_watches/img4m.png','Silver Vintage Metal Watch',1,800,800,'2026-03-28 09:15:55'),(10,10,'/static/uploads/metal_watches/img5m.png','Black Bold Metal Watch',1,700,700,'2026-03-28 09:19:37'),(11,11,'/static/uploads/leather_watches/img1l.png','Brown Leather Watch',1,800,800,'2026-03-28 09:15:55'),(12,12,'/static/uploads/leather_watches/img2l.png','Black Leather Watch',1,800,800,'2026-03-28 09:15:55'),(13,13,'/static/uploads/leather_watches/img3l.png','Gold Leather Watch',1,800,800,'2026-03-28 09:15:55'),(14,14,'/static/uploads/leather_watches/img4l.png','Brown Lean Watch',1,800,800,'2026-03-28 09:15:55'),(15,15,'/static/uploads/leather_watches/img5l.png','Bold Black Watch',1,800,800,'2026-03-28 09:15:55'),(16,16,'/static/uploads/ear_buds/img1.png','Hero Elite Pro Earbuds',1,800,800,'2026-04-06 15:58:00'),(17,17,'/static/uploads/ear_buds/img2.png','Hero Sound Max Earbuds',1,800,800,'2026-04-06 15:58:00'),(18,18,'/static/uploads/ear_buds/img3.png','Hero Fit Sport Earbuds',1,800,800,'2026-04-06 15:58:00'),(19,19,'/static/uploads/ear_buds/img4.png','Hero Studio Pro Earbuds',1,800,800,'2026-04-06 15:58:00'),(20,20,'/static/uploads/ear_buds/img5.png','Hero Lite Compact Earbuds',1,800,800,'2026-04-06 15:58:00');
/*!40000 ALTER TABLE `product_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `products` (
  `product_id` int(11) NOT NULL AUTO_INCREMENT,
  `product_no` varchar(50) NOT NULL,
  `category_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `base_price` decimal(10,2) NOT NULL,
  `sale_price` decimal(10,2) DEFAULT NULL,
  `stock_quantity` int(11) DEFAULT 0,
  `status` enum('active','draft','archived') DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`product_id`),
  UNIQUE KEY `product_no` (`product_no`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'SM-001',1,'SKIM',12999.00,11999.00,4,'active','2026-03-27 08:04:40','2026-03-27 08:04:40'),(2,'SW-002',1,'SNIX',12999.00,1199.00,5,'active','2026-03-28 05:23:29','2026-03-28 05:23:29'),(3,'SW-003',1,'SNIQ',14999.00,1299.00,5,'active','2026-03-28 05:24:52','2026-03-28 05:24:52'),(4,'SW-004',1,'SNIM',14999.00,1149.00,5,'active','2026-03-28 05:24:52','2026-03-28 05:24:52'),(5,'SW-005',1,'SNIN',11999.00,1099.00,5,'active','2026-03-28 05:24:52','2026-03-28 05:24:52'),(6,'MW-001',2,'MURREN',34000.00,32999.00,5,'active','2026-03-28 05:55:39','2026-03-28 05:55:39'),(7,'MW-002',2,'MURRAM',35000.00,31999.00,5,'active','2026-03-28 05:58:36','2026-03-28 05:58:36'),(8,'MW-003',2,'MULEN',36000.00,33999.00,5,'active','2026-03-28 05:58:36','2026-03-28 05:58:36'),(9,'MW-004',2,'MUAREN',24000.00,22999.00,5,'active','2026-03-28 05:58:36','2026-03-28 05:58:36'),(10,'MW-005',2,'MURGEN',34999.00,33999.00,5,'active','2026-03-28 05:58:36','2026-03-28 05:58:36'),(11,'LW-001',3,'LIXES',3000.00,2599.00,5,'active','2026-03-28 06:02:02','2026-03-28 06:02:02'),(12,'LW-002',3,'LIUNEN',2000.00,1699.00,5,'active','2026-03-28 06:02:02','2026-03-28 06:02:02'),(13,'LW-003',3,'LEAN',14000.00,11999.00,5,'active','2026-03-28 06:02:02','2026-03-28 06:02:02'),(14,'LW-004',3,'LEATH',1500.00,1099.00,5,'active','2026-03-28 06:02:02','2026-03-28 06:02:02'),(15,'LW-005',3,'LEAD',54000.00,53999.00,5,'active','2026-03-28 06:02:02','2026-03-28 06:02:02'),(16,'EB-001',4,'Hero Elite Pro',8999.00,7999.00,15,'active','2026-04-06 15:51:55','2026-04-06 15:51:55'),(17,'EB-002',4,'Hero Sound Max',6999.00,5999.00,20,'active','2026-04-06 15:51:55','2026-04-06 15:51:55'),(18,'EB-003',4,'Hero Fit Sport',4999.00,3999.00,25,'active','2026-04-06 15:51:55','2026-04-06 15:51:55'),(19,'EB-004',4,'Hero Studio Pro',9999.00,8499.00,12,'active','2026-04-06 15:51:55','2026-04-06 15:51:55'),(20,'EB-005',4,'Hero Lite Compact',3999.00,2999.00,30,'active','2026-04-06 15:51:55','2026-04-06 15:51:55');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `role_id` int(11) NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'admin',1,'2026-03-31 06:46:18'),(2,'user',2,'2026-03-31 06:46:40');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `address` text DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `last_login_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,2,'Muhammad','Khurram','saleemkhurram420@gmail.com','03150484043','guest','Gulshan Iqbal Colony Qasim Bela Multan','Multan','Pakistan',1,NULL,'2026-03-31 06:53:16','2026-03-31 06:53:16'),(3,2,'khurram','saleem','cashcentral123@gmail.com','03150484041','guest','Main Street Dhamaka Chowk Near Army Wall Qasim Bela Multan Cantt','Multan','Pakistan',1,NULL,'2026-03-31 06:54:35','2026-03-31 06:54:35'),(4,2,'Umair','Khurram','central123@gmail.com','03150494042','guest','Fiasal Park Multan','Multan','Pakistan',1,NULL,'2026-03-31 12:01:26','2026-03-31 12:01:26'),(5,2,'testing','buy now','testing123@gmail.com','03150484022','guest','Gulshan Iqbal Colony Qasim Bela Multan','Multan','Pakistan',1,NULL,'2026-04-02 13:01:25','2026-04-02 13:01:25'),(6,2,'testing','check','testcentral@gmail.com','03150484012','guest','Gulshan Iqbal Colony Qasim Bela Multan','Multan','Pakistan',1,NULL,'2026-04-02 14:08:11','2026-04-02 14:08:11'),(7,2,'testing','back cart','central@gmail.com','03150424041','guest','Gulshan Iqbal Colony Qasim Bela Multan','Multan','Pakistan',1,NULL,'2026-04-09 13:24:05','2026-04-09 13:24:05'),(8,2,'test','buy now backend','cent123@gmail.com','03140503432','guest','Western Fort Colony, Near Army wall Dhmaka Chowk Qasim Bela Multan','Multan','Pakistan',1,NULL,'2026-04-10 06:17:51','2026-04-10 06:17:51');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `visitors`
--

DROP TABLE IF EXISTS `visitors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors` (
  `visitor_id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` varchar(255) NOT NULL,
  `ip_address` varchar(50) DEFAULT NULL,
  `pages_viewed` int(11) DEFAULT 1,
  `total_visits` int(11) DEFAULT 1,
  `first_visit_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `last_visit_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`visitor_id`),
  UNIQUE KEY `session_id` (`session_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `visitors_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `visitors`
--

LOCK TABLES `visitors` WRITE;
/*!40000 ALTER TABLE `visitors` DISABLE KEYS */;
/*!40000 ALTER TABLE `visitors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'hero_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-10 11:37:51
