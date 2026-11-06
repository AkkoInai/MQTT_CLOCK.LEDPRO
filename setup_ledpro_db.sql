-- setup_ledpro_db.sql
-- 実行方法: sudo mariadb -u root < setup_ledpro_db.sql
-- (または `sudo mariadb -u root` でログインしてから1行ずつ流してもOK)
--
-- ※ '<ここにパスワードを設定>' の部分は、必ずご自身で決めたパスワードに
--    書き換えてから実行してください。このファイルにパスワードを書いたまま
--    残す場合は、他人が読めない場所に保管してください。

CREATE DATABASE IF NOT EXISTS ledpro CHARACTER SET utf8mb4;

-- DBユーザー(Linuxユーザーとは別、ご希望通り)
CREATE USER IF NOT EXISTS 'ledpro_writer'@'localhost' IDENTIFIED BY 'ledpro_writer';

-- このユーザーには「ledproデータベースへの読み書き」だけを許可する
-- (DROP/ALTER等の管理権限は与えない。将来テーブル構造を変える時だけrootで作業する)
GRANT INSERT, SELECT ON ledpro.* TO 'ledpro_writer'@'localhost';
FLUSH PRIVILEGES;

USE ledpro;

-- 温湿度ログ(定期記録)
CREATE TABLE IF NOT EXISTS climate_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  temperature FLOAT NOT NULL,
  humidity FLOAT NOT NULL
);

-- 振動/地震イベントログ(閾値を超えた時だけ記録)
CREATE TABLE IF NOT EXISTS quake_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  magnitude FLOAT NOT NULL,
  accel_x FLOAT NOT NULL,
  accel_y FLOAT NOT NULL,
  accel_z FLOAT NOT NULL
);
