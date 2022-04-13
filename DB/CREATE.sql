CREATE SCHEMA IF NOT EXISTS `BASP` DEFAULT CHARACTER SET utf8 ;
USE `BASP` ;

-- -----------------------------------------------------
-- Table `BASP`.`Author`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `BASP`.`Author` (
  `idAuthor` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(45) NULL,
  `LastName` VARCHAR(45) NULL,
  `Institution` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  PRIMARY KEY (`idAuthor`));

CREATE UNIQUE INDEX `email_UNIQUE` ON `BASP`.`Author` (`email` ASC);

-- -----------------------------------------------------
-- Table `BASP`.`Paper`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `BASP`.`Paper` (
  `idPaper` VARCHAR(200) NOT NULL,
  `title` text,
  `abstract` text,
  `body` text,
  `year` DATETIME NULL,
  `doi` VARCHAR(45) NULL,
  `word_count` INT NULL,
  PRIMARY KEY (`idPaper`));


-- -----------------------------------------------------
-- Table `BASP`.`paper_to_author`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `BASP`.`paper_to_author` (
  `fk_paper_id` VARCHAR(200) NOT NULL,
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


-- -----------------------------------------------------
-- Table `BASP`.`Word`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `BASP`.`Word` (
  `idWord` INT NOT NULL AUTO_INCREMENT,
  `word` VARCHAR(45) NULL,
  PRIMARY KEY (`idWord`));

CREATE UNIQUE INDEX `word_UNIQUE` ON `BASP`.`Word` (`word` ASC);


-- -----------------------------------------------------
-- Table `BASP`.`word_to_paper`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `BASP`.`word_to_paper` (
  `fk_word_id` INT NOT NULL,
  `fk_paper_id` VARCHAR(200) NOT NULL,
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

CREATE USER 'populator' IDENTIFIED BY 'd9pifetoyesad2cekipoyolis';
GRANT INSERT ON BASP.* TO 'populator';
GRANT SELECT ON Author TO 'populator';
GRANT SELECT ON Word TO 'populator';

CREATE USER 'retriver' IDENTIFIED BY '5t7zuvtoyesad2vguhbpoyoli';
GRANT SELECT ON BASP.* TO 'retriver';


