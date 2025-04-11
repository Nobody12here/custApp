<?php
require_once 'config.php';

header('Content-Type: application/json');

try {
    $stmt = $pdo->query("SELECT id, application_name AS name, application_desc AS content, created_at FROM applications");
    $applications = $stmt->fetchAll(PDO::FETCH_ASSOC);
    echo json_encode($applications);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to fetch applications: ' . $e->getMessage()]);
}
?>