<?php
require_once 'config.php';

header('Content-Type: application/json');

$input = json_decode(file_get_contents('php://input'), true);

if (!isset($input['name']) || !isset($input['content'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Template name and content are required']);
    exit;
}

$applicationName = $input['name'];
$applicationDesc = $input['content'];

// Set default values for new required fields
$responsibleDeptId = 1; // Default department ID (you may need to adjust this)
$shortName = substr($applicationName, 0, 10); // Use first 10 characters of the name
$amount = 0.00; // Default amount
$defaultResponsibleEmployeeId = 1; // Default employee ID (as per table default)
$status = 1; // Default status (active)
$createdAt = date('Y-m-d H:i:s'); // Current timestamp
$updatedAt = $createdAt; // Same as created_at for new records

try {
    $stmt = $pdo->prepare("
        INSERT INTO applications (
            application_name, application_desc, responsible_dept_id, short_name, 
            amount, default_responsible_employee_id, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ");
    $stmt->execute([
        $applicationName, $applicationDesc, $responsibleDeptId, $shortName, 
        $amount, $defaultResponsibleEmployeeId, $status, $createdAt, $updatedAt
    ]);
    echo json_encode(['success' => 'Application saved successfully']);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to save application: ' . $e->getMessage()]);
}
?>