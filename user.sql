CREATE TABLE user (
        user_id smallint UNSIGNED NOT NULL AUTO_INCREMENT,
        user_name varchar(255) NOT NULL COMMENT 'Username for Login, use standard Epicor email without @',
        user_pwd varchar(255) NOT NULL COMMENT 'Hashed Password for user',
        created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id)
);