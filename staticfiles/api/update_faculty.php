<?php
require_once 'config.php';

ob_start();
$data = json_decode(file_get_contents('php://input'), true);

if (empty($data['id']) || empty($data['name']) || empty($data['email'])) {
    ob_end_clean();
    http_response_code(400);
    echo json_encode(['error' => 'ID, Name, and Email are required']);
    exit;
}

try {
    $stmt = $pdo->prepare("UPDATE faculty SET name=?, designation=?, department=?, email=? WHERE id=?");
    $stmt->execute([
        $data['name'],
        $data['designation'],
        $data['department'],
        $data['email'],
        $data['id']
    ]);
    
    ob_end_clean();
    echo json_encode(['success' => 'Faculty updated successfully']);
} catch (PDOException $e) {
    ob_end_clean();
    http_response_code(500);
    echo json_encode(['error' => 'Database error: ' . $e->getMessage()]);
}
?>