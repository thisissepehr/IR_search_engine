CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`Author`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Author` (
  `idAuthor` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(45) NULL,
  `LastName` VARCHAR(45) NULL,
  `Institution` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  PRIMARY KEY (`idAuthor`));

CREATE UNIQUE INDEX `email_UNIQUE` ON `mydb`.`Author` (`email` ASC);

-- -----------------------------------------------------
-- Table `mydb`.`Paper`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Paper` (
  `idPaper` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(45) NULL,
  `abstract` VARCHAR(45) NULL,
  `body` VARCHAR(45) NULL,
  `year` DATETIME NULL,
  `doi` VARCHAR(45) NULL,
  `word_count` INT NULL,
  PRIMARY KEY (`idPaper`));


-- -----------------------------------------------------
-- Table `mydb`.`paper_to_author`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`paper_to_author` (
  `fk_paper_id` INT NOT NULL,
  `fk_author_id` INT NOT NULL,
  PRIMARY KEY (`fk_paper_id`, `fk_author_id`),
  CONSTRAINT `fk_author_paper_to_author`
    FOREIGN KEY (`fk_author_id`)
    REFERENCES `mydb`.`Author` (`idAuthor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_paper_paper_to_author`
    FOREIGN KEY (`fk_paper_id`)
    REFERENCES `mydb`.`Paper` (`idPaper`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE INDEX `fk_author_paper_to_author_idx` ON `mydb`.`paper_to_author` (`fk_author_id` ASC);


-- -----------------------------------------------------
-- Table `mydb`.`Word`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`Word` (
  `idWord` INT NOT NULL AUTO_INCREMENT,
  `word` VARCHAR(45) NULL,
  PRIMARY KEY (`idWord`));

CREATE UNIQUE INDEX `word_UNIQUE` ON `mydb`.`Word` (`word` ASC);


-- -----------------------------------------------------
-- Table `mydb`.`word_to_paper`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`word_to_paper` (
  `fk_word_id` INT NOT NULL,
  `fk_paper_id` INT NOT NULL,
  `counter` INT NULL,
  PRIMARY KEY (`fk_word_id`, `fk_paper_id`),
  CONSTRAINT `fk_word_word_to_paper`
    FOREIGN KEY (`fk_word_id`)
    REFERENCES `mydb`.`Word` (`idWord`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_paper_word_to_paper`
    FOREIGN KEY (`fk_paper_id`)
    REFERENCES `mydb`.`Paper` (`idPaper`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE INDEX `fk_paper_word_to_paper_idx` ON `mydb`.`word_to_paper` (`fk_paper_id` ASC);