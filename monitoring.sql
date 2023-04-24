CREATE TABLE monitor (
        monitor_id smallint UNSIGNED NOT NULL AUTO_INCREMENT,
        monitor_name varchar(255) NOT NULL COMMENT 'Display Name',
        monitor_type varchar(255) NOT NULL COMMENT 'Monitor Type',
        monitor_ip varchar(80) DEFAULT NULL COMMENT 'Ip or FQDN of server',
        monitor_url varchar(255) DEFAULT NULL COMMENT 'Website Url',
        monitor_state varchar(12) DEFAULT NULL COMMENT 'Monitor Status: Active/Suspended',
        board_id smallint UNSIGNED NOT NULL COMMENT 'Foreign Key, points to Board monitor is on',
        monitor_site24_id bigint UNSIGNED DEFAULT NULL COMMENT 'Monitor ID for Site24 monitors',
        created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (monitor_id),
        FOREIGN KEY (board_id) REFERENCES board(board_id)
);

CREATE TABLE board (
        board_id smallint UNSIGNED NOT NULL AUTO_INCREMENT,
        board_name varchar(255) NOT NULL COMMENT 'Board or BU Name',
        board_type varchar(12) NOT NULL COMMENT 'Board Type, Nagios, Site24 etc.',
        board_bu_id int UNSIGNED DEFAULT NULL COMMENT 'If Site24, BUID',
        created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (board_id)
);

CREATE TABLE contact ( 
        contact_id smallint UNSIGNED NOT NULL AUTO_INCREMENT,
        contact_name varchar(255) NOT NULL COMMENT 'Contact Name',
        contact_type varchar(255) NOT NULL COMMENT 'Individual or Team Type',
        contact_email varchar(255) NOT NULL COMMENT 'Email Address',
        contact_phone varchar(20) DEFAULT NULL COMMENT 'Phone Number',
        contact_site24_id bigint UNSIGNED DEFAULT NULL COMMENT 'User_id for Site24 contact group',
        created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (contact_id)
);

CREATE TABLE contact_group (
        contact_group_id smallint UNSIGNED NOT NULL AUTO_INCREMENT,
        contact_group_name varchar(255) NOT NULL COMMENT 'contact group name',
        contact_group_site24_id bigint UNSIGNED DEFAULT NULL COMMENT 'User_group_id'
        created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (contact_group_id)
);

-- multiple records with same contact_id... one for each contact_group
-- multiple records with same contact_group_id... one for each contact
CREATE TABLE contact_link_group (
        contact_link_group_id smallint UNSIGNED NOT NULL AUTO_INCREMENT,
        contact_group_id smallint UNSIGNED NOT NULL,
        contact_id smallint UNSIGNED NOT NULL,
        PRIMARY KEY (contact_link_group_id),
        FOREIGN KEY (contact_group_id) REFERENCES contact_group(contact_group_id),
        FOREIGN KEY (contact_id) REFERENCES contact(contact_id)
);

-- multiple records with same monitor_id... one for each contact_group
-- multiple records with same contact_group_id... one for each monitor
CREATE TABLE monitor_link_group (
        monitor_link_group_id smallint UNSIGNED NOT NULL AUTO_INCREMENT,
        contact_group_id smallint UNSIGNED NOT NULL,
        monitor_id smallint UNSIGNED NOT NULL,
        PRIMARY KEY (monitor_link_group_id),
        FOREIGN KEY (contact_group_id) REFERENCES contact_group(contact_group_id),
        FOREIGN KEY (monitor_id) REFERENCES monitor(monitor_id)
);



CREATE TABLE credentials (
        credential_id smallint UNSIGNED NOT NULL AUTO_INCREMENT,
        credential_user varchar(255) NOT NULL,
        credential_pwd varchar(255) NOT NULL COMMENT 'hashed password',
        credential_email varchar(255) NOT NULL,
        PRIMARY KEY (credential_id)
)