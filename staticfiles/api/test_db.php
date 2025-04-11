<?php
require_once 'config.php'; // Adjust the path if config.php is in a different directory (e.g., 'api/config.php')

try {
    $stmt = $pdo->query("SELECT 1");
    if ($stmt) {
        echo "Database connection successful!";
    }
} catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}
?>