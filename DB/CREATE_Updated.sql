CREATE SCHEMA IF NOT EXISTS `BASP` DEFAULT CHARACTER SET utf8 ;
USE `BASP` ;

-- -----------------------------------------------------
-- Table `BASP`.`Author`
-- -----------------------------------------------------
--OLD
CREATE TABLE IF NOT EXISTS `BASP`.`Author` (
  `idAuthor` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(45) NULL,
  `LastName` VARCHAR(45) NULL,
  `Institution` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  PRIMARY KEY (`idAuthor`));

CREATE UNIQUE INDEX `email_UNIQUE` ON `BASP`.`Author` (`email` ASC);

-- NEW
CREATE TABLE `Author` (
  `idAuthor` int NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(45) DEFAULT NULL,
  `LastName` varchar(45) DEFAULT NULL,
  `Institution` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idAuthor`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=492 DEFAULT CHARSET=utf8mb3;

-- -----------------------------------------------------
-- Table `BASP`.`Paper`
-- -----------------------------------------------------
-- OLD
CREATE TABLE IF NOT EXISTS `BASP`.`Author` (
  `idAuthor` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(45) NULL,
  `LastName` VARCHAR(45) NULL,
  `Institution` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  PRIMARY KEY (`idAuthor`));

CREATE UNIQUE INDEX `email_UNIQUE` ON `BASP`.`Author` (`email` ASC);

-- NEW
CREATE TABLE `Paper` (
  `idPaper` varchar(200) NOT NULL,
  `title` text,
  `abstract` text,
  `body` text,
  `year` datetime DEFAULT NULL,
  `doi` varchar(45) DEFAULT NULL,
  `word_count` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- -----------------------------------------------------
-- Table `BASP`.`paper_to_author`
-- -----------------------------------------------------
-- OLD
CREATE TABLE IF NOT EXISTS `BASP`.`paper_to_author` (
  `fk_paper_id` INT NOT NULL,
  `fk_author_id` INT NOT NULL,
  PRIMARY KEY (`fk_paper_id`, `fk_author_id`),
  CONSTRAINT `fk_author_paper_to_author`
    FOREIGN KEY (`fk_author_id`)
    REFERENCES `BASP`.`Author` (`idAuthor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_paper_paper_to_author`
    FOREIGN KEY (`fk_paper_id`)
    REFERENCES `BASP`.`Paper` (`idPaper`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE INDEX `fk_author_paper_to_author_idx` ON `BASP`.`paper_to_author` (`fk_author_id` ASC);

-- NEW
CREATE TABLE `paper_to_author` (
  `fk_paper_id` varchar(200) NOT NULL,
  `fk_author_id` int NOT NULL,
  PRIMARY KEY (`fk_paper_id`,`fk_author_id`),
  KEY `fk_author_paper_to_author_idx` (`fk_author_id`),
  CONSTRAINT `fk_author_paper_to_author` FOREIGN KEY (`fk_author_id`) REFERENCES `Author` (`idAuthor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- -----------------------------------------------------
-- Table `BASP`.`Word`
-- -----------------------------------------------------
-- OLD
CREATE TABLE IF NOT EXISTS `BASP`.`Word` (
  `idWord` INT NOT NULL AUTO_INCREMENT,
  `word` VARCHAR(45) NULL,
  PRIMARY KEY (`idWord`));

CREATE UNIQUE INDEX `word_UNIQUE` ON `BASP`.`Word` (`word` ASC);

-- NEW
CREATE TABLE `Word` (
  `idWord` int NOT NULL AUTO_INCREMENT,
  `word` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idWord`),
  UNIQUE KEY `word_UNIQUE` (`word`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- -----------------------------------------------------
-- Table `BASP`.`word_to_paper`
-- -----------------------------------------------------
-- OLD
CREATE TABLE IF NOT EXISTS `BASP`.`word_to_paper` (
  `fk_word_id` INT NOT NULL,
  `fk_paper_id` INT NOT NULL,
  `counter` INT NULL,
  PRIMARY KEY (`fk_word_id`, `fk_paper_id`),
  CONSTRAINT `fk_word_word_to_paper`
    FOREIGN KEY (`fk_word_id`)
    REFERENCES `BASP`.`Word` (`idWord`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_paper_word_to_paper`
    FOREIGN KEY (`fk_paper_id`)
    REFERENCES `BASP`.`Paper` (`idPaper`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE INDEX `fk_paper_word_to_paper_idx` ON `BASP`.`word_to_paper` (`fk_paper_id` ASC);

-- NEW
CREATE TABLE `word_to_paper` (
  `fk_word_id` int NOT NULL,
  `fk_paper_id` int NOT NULL,
  `counter` int DEFAULT NULL,
  PRIMARY KEY (`fk_word_id`,`fk_paper_id`),
  KEY `fk_paper_word_to_paper_idx` (`fk_paper_id`),
  CONSTRAINT `fk_word_word_to_paper` FOREIGN KEY (`fk_word_id`) REFERENCES `Word` (`idWord`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- -----------------------------------------------------

CREATE USER 'populator' IDENTIFIED BY 'd9pifetoyesad2cekipoyolis';
GRANT INSERT ON BASP.* TO 'populator';
GRANT SELECT ON Author TO 'populator';
GRANT SELECT ON Word TO 'populator';

CREATE USER 'retriver' IDENTIFIED BY '5t7zuvtoyesad2vguhbpoyoli';
GRANT SELECT ON BASP.* TO 'retriver';

-- -----------------------------------------------------
-- UPDATES
ALTER TABLE Author
MODIFY title, abstract, body
text;

ALTER TABLE Paper
MODIFY idPaper
VARCHAR(200);

ALTER TABLE paper_to_author
MODIFY fk_paper_id
VARCHAR(200);

ALTER TABLE child DROP FOREIGN KEY `child_ibfk_1`;

ALTER TABLE Paper MODIFY idPaper VARCHAR(200) NOT NULL;
ALTER TABLE Paper DROP PRIMARY KEY;
