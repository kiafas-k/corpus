/*
 Navicat MySQL Data Transfer

 Source Server         : server
 Source Server Type    : MySQL
 Source Server Version : 50722
 Source Host           : 10.0.0.108:3306
 Source Schema         : articles

 Target Server Type    : MySQL
 Target Server Version : 50722
 File Encoding         : 65001

 Date: 03/06/2018 14:16:12
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tbl_articles
-- ----------------------------
DROP TABLE IF EXISTS `tbl_articles`;
CREATE TABLE `tbl_articles`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `url` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `timestamp` bigint(20) NULL DEFAULT NULL,
  `source` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `keywords` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `text` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `named_entities` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `topic` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `sentiment` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4103 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tbl_sources
-- ----------------------------
DROP TABLE IF EXISTS `tbl_sources`;
CREATE TABLE `tbl_sources`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source` longtext CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `topic` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `active` int(1) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 26 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
