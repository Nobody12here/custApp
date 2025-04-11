<?php
require_once 'config.php'; // Adjust path if needed

ob_start();

$data = json_decode(file_get_contents('php://input'), true);
if (json_last_error() !== JSON_ERROR_NONE) {
    ob_end_clean();
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON data received']);
    exit;
}

$faculty = $data['faculty'] ?? [];
if (empty($faculty)) {
    ob_end_clean();
    http_response_code(400);
    echo json_encode(['error' => 'No faculty data provided']);
    exit;
}

try {
    $successCount = 0;
    $stmt = $pdo->prepare("INSERT INTO faculty (id, name, designation, department, email) VALUES (?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE name=?, designation=?, department=?, email=?");

    foreach ($faculty as $member) {
        if (empty($member['id']) || empty($member['name']) || empty($member['email'])) {
            continue;
        }

        $stmt->execute([
            $member['id'],
            $member['name'],
            $member['designation'],
            $member['department'],
            $member['email'],
            $member['name'],
            $member['designation'],
            $member['department'],
            $member['email']
        ]);
        
        $successCount++;
    }

    ob_end_clean();
    echo json_encode([
        'success' => true,
        'count' => $successCount,
        'message' => "$successCount faculty uploaded successfully"
    ]);

} catch (PDOException $e) {
    ob_end_clean();
    http_response_code(500);
    echo json_encode(['error' => 'Database error: ' . $e->getMessage()]);
    exit;
}
?>