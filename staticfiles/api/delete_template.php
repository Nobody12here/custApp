<?php
require_once 'config.php';

header('Content-Type: application/json');

$input = json_decode(file_get_contents('php://input'), true);

if (!isset($input['id'])) {
    http_response_code(400);
    echo json_encode(['error' => 'ID is required']);
    exit;
}

$id = $input['id'];

try {
    $stmt = $pdo->prepare("DELETE FROM applications WHERE id = ?");
    $stmt->execute([$id]);
    
    if ($stmt->rowCount() > 0) {
        echo json_encode(['success' => 'Application deleted successfully']);
    } else {
        echo json_encode(['error' => 'No application found with the given ID']);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to delete application: ' . $e->getMessage()]);
}
?>