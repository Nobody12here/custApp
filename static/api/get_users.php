<?php
require_once 'config.php';

header('Content-Type: application/json');

$userType = isset($_GET['user_type']) ? $_GET['user_type'] : '';

if (!$userType) {
    echo json_encode(['error' => 'User type parameter is required']);
    exit;
}

try {
    $stmt = $pdo->prepare("SELECT * FROM users WHERE user_type = ?");
    $stmt->execute([$userType]);
    $users = $stmt->fetchAll(PDO::FETCH_ASSOC);
    echo json_encode($users);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to fetch users: ' . $e->getMessage()]);
}
?>