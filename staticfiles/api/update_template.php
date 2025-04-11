<?php
require_once 'config.php';

header('Content-Type: application/json');

$input = json_decode(file_get_contents('php://input'), true);

if (!isset($input['id']) || !isset($input['name']) || !isset($input['content'])) {
    http_response_code(400);
    echo json_encode(['error' => 'ID, name, and content are required']);
    exit;
}

$id = $input['id'];
$applicationName = $input['name'];
$applicationDesc = $input['content'];
$updatedAt = date('Y-m-d H:i:s'); // Current timestamp
$shortName = substr($applicationName, 0, 10); // Update short_name based on new name

try {
    $stmt = $pdo->prepare("
        UPDATE applications 
        SET application_name = ?, application_desc = ?, short_name = ?, updated_at = ?
        WHERE id = ?
    ");
    $stmt->execute([$applicationName, $applicationDesc, $shortName, $updatedAt, $id]);
    
    if ($stmt->rowCount() > 0) {
        echo json_encode(['success' => 'Application updated successfully']);
    } else {
        echo json_encode(['error' => 'No application found with the given ID']);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to update application: ' . $e->getMessage()]);
}
?>