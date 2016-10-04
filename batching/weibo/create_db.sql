CREATE DATABASE weibo
  DEFAULT CHARACTER SET utf8
  COLLATE utf8_general_ci;

USE weibo;

CREATE TABLE batching_comment (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  userID     VARCHAR(50),
  userName   VARCHAR(50),
  userType   VARCHAR(50), # 没有爬到,在userName里
  time       VARCHAR(50),
  forwardNum INT,
  commentNum INT,
  likeNum    INT,
  content    VARCHAR(500)
)
  ENGINE = MyISAM
  DEFAULT CHARSET = utf8;

CREATE TABLE SyntacticResults (
  id                INT PRIMARY KEY,
  preprocessSen     VARCHAR(500),
  posTagging        VARCHAR(750),
  syntacticAnalysis TEXT,
  pvWord            VARCHAR(200),
  pvModifierWord    VARCHAR(200),
  keyWords          VARCHAR(200),
  tagResult         INT
)
  ENGINE = MyISAM
  DEFAULT CHAR SET = utf8;


CREATE TABLE UpdateResults (
  id            INT PRIMARY KEY,
  realTagResult INT
)
  ENGINE = MyISAM
  DEFAULT CHAR SET = utf8;


CREATE TABLE BatchAnalyzeResults (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  topicName         VARCHAR(50),
  startID           INT,
  endID             INT,
  yiwenFeatureSet   TEXT,
  foudingFeatureSet TEXT,
  chenshuFeatureSet TEXT,
  featuresAnalysis  TEXT,
  timelineAnalysis  TEXT
)
  ENGINE = MyISAM
  DEFAULT CHAR SET = utf8;

  CREATE TABLE `batching_keyword` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword_text` varchar(20) NOT NULL,
  `create_date` datetime(6) NOT NULL,
  `diagram_data` longtext,
  `request_count` int(10) unsigned NOT NULL,
  `request_date` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 ;

  CREATE TABLE `batching_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userID` varchar(100) NOT NULL,
  `userName` varchar(100) NOT NULL,
  `userType` varchar(100) NOT NULL,
  `time` varchar(100) NOT NULL,
  `forwardNum` int(11) NOT NULL,
  `commentNum` int(11) NOT NULL,
  `likeNum` int(11) NOT NULL,
  `content` varchar(800) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8;

CREATE TABLE `simple_simple` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sentence_text` varchar(200) NOT NULL,
  `request_date` datetime(6) NOT NULL,
  `request_count` int(10) unsigned NOT NULL,
  `seg_json` varchar(200) DEFAULT NULL,
  `washed_text` varchar(200) DEFAULT NULL,
  `lexical_tree` longtext,
  `emotion` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sentence_text` (`sentence_text`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8;



# INSERT INTO comment (userID, userName, userType, time, forwardNum, commentNum, likeNum, content, title, usercard)
# VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);