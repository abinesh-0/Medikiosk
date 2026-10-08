USE medikiosk;
CREATE TABLE IF NOT EXISTS otp_tokens (
 id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 email VARCHAR(191) NOT NULL,
 purpose ENUM('register','reset') NOT NULL,
 otp_hash VARCHAR(255) NOT NULL,
 expires_at DATETIME NOT NULL,
 attempts INT NOT NULL DEFAULT 0,
 consumed_at DATETIME NULL,
 created_at DATETIME NOT NULL,
 INDEX idx_otp_email_purpose (email,purpose)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
