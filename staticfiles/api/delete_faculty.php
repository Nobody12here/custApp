<?php
require_once 'config.php';

ob_start();
$data = json_decode(file_get_contents('php://input'), true);

if (empty($data['id'])) {
    ob_end_clean();
    http_response_code(400);
    echo json_encode(['error' => 'ID is required']);
    exit;
}

try {
    $stmt = $pdo->prepare("DELETE FROM faculty WHERE id=?");
    $stmt->execute([$data['id']]);
    
    ob_end_clean();
    echo json_encode(['success' => 'Faculty deleted successfully']);
} catch (PDOException $e) {
    ob_end_clean();
    http_response_code(500);
    echo json_encode(['error' => 'Database error: ' . $e->getMessage()]);
}
?>