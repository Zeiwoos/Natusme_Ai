CREATE DATABASE  IF NOT EXISTS `natusme` ;
USE `natusme`;

DROP TABLE IF EXISTS `users`;
CREATE TABLE users (
                        id                   INT AUTO_INCREMENT PRIMARY KEY,
                        username             VARCHAR(50) UNIQUE NOT NULL,
                        password             VARCHAR(255) NOT NULL,
                        level                INT DEFAULT 1,
                        exp                  INT DEFAULT 0,

#                         email                VARCHAR(100) UNIQUE NOT NULL,
                        avatar               TEXT,
                        create_time          DATETIME ,
                        last_login_time      DATETIME DEFAULT NULL,
                        bio                  TEXT,
                        update_time          DATETIME ,
                        wechat_account       VARCHAR(100) UNIQUE,
                        qq_account           VARCHAR(100) UNIQUE,
                        is_logged_out        INT DEFAULT 0 CHECK (is_logged_out IN (0, 1)),
                        permission_level     ENUM('BANNED','USER','ADMIN','SUPER_ADMIN') default 'USER'


);
