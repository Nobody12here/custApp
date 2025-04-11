
<?php
$host = 'localhost'; // Replace with the remote database host (e.g., 'yourdomain.com' or '192.168.1.1')
$dbname = 'custappp'; // Replace with your remote database name
$username = 'root'; // Replace with your remote database username
$password = ''; // Replace with your remote database password
$port = 3306; // Default MySQL port; update if your host uses a different port

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;port=$port", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    die("Connection failed: " . $e->getMessage());
}
?>