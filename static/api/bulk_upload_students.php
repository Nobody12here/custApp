<?php
// Include the database configuration
require_once 'config.php'; // Adjust the path if config.php is in a different directory

ob_start(); // Start output buffering

// Get POST data
$data = json_decode(file_get_contents('php://input'), true);
if (json_last_error() !== JSON_ERROR_NONE) {
    ob_end_clean();
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON data received']);
    exit;
}

$students = $data['students'] ?? [];
if (empty($students)) {
    ob_end_clean();
    http_response_code(400);
    echo json_encode(['error' => 'No student data provided']);
    exit;
}

try {
    $successCount = 0;
    // Use correct column names: regNo and fatherName
    $stmt = $pdo->prepare("INSERT INTO students (id, name, regNo, fatherName, cgpa) VALUES (?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE name=?, fatherName=?, cgpa=?");

    foreach ($students as $student) {
        // Validate required fields
        if (empty($student['id']) || empty($student['name']) || empty($student['regNo'])) {
            continue; // Skip invalid records
        }

        // Execute with correct parameter order matching the query
        $stmt->execute([
            $student['id'],
            $student['name'],
            $student['regNo'],
            $student['fatherName'],
            $student['cgpa'],
            $student['name'],
            $student['fatherName'],
            $student['cgpa']
        ]);
        
        $successCount++;
    }

    // Clean buffer and send success response
    ob_end_clean();
    echo json_encode([
        'success' => true,
        'count' => $successCount,
        'message' => "$successCount students uploaded successfully"
    ]);

} catch (PDOException $e) {
    ob_end_clean();
    http_response_code(500);
    echo json_encode(['error' => 'Database error: ' . $e->getMessage()]);
    exit;
}
?>