<?php
require_once 'config.php';

header('Content-Type: application/json');

$input = json_decode(file_get_contents('php://input'), true);

if (!isset($input['users']) || !is_array($input['users']) || empty($input['users'])) {
    http_response_code(400);
    echo json_encode(['error' => 'No users data provided']);
    exit;
}

$users = $input['users'];
$successCount = 0;
$errorMessages = [];

try {
    $pdo->beginTransaction();

    $stmt = $pdo->prepare("
        INSERT INTO users (
            uu_id, name, father_name, address, program_name, dept_name, gender, status, email,
            created_at, updated_at, user_type, role, designation, otp, remark, phone_number,
            picture, cgpa, term, DoB, CNIC
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ");

    foreach ($users as $index => $user) {
        try {
            $createdAt = date('Y-m-d H:i:s');
            $updatedAt = $createdAt;

            $stmt->execute([
                $user['uu_id'],
                $user['name'],
                $user['father_name'] ?? null,
                $user['address'],
                $user['program_name'] ?? 'N/A',
                $user['dept_name'] ?? 'N/A',
                $user['gender'],
                $user['status'],
                $user['email'],
                $createdAt,
                $updatedAt,
                $user['user_type'],
                $user['role'],
                $user['designation'] ?? 'N/A',
                $user['otp'] ?? null,
                $user['remark'] ?? null,
                $user['phone_number'],
                $user['picture'] ?? null,
                $user['cgpa'] ?? null,
                $user['term'] ?? null,
                $user['DoB'] ?? null,
                $user['CNIC'] ?? null
            ]);
            $successCount++;
        } catch (Exception $e) {
            $errorMessages[] = "Row " . ($index + 2) . ": " . $e->getMessage();
        }
    }

    if (!empty($errorMessages)) {
        $pdo->rollBack();
        echo json_encode([
            'error' => 'Some users could not be uploaded',
            'details' => $errorMessages,
            'successful' => $successCount
        ]);
        exit;
    }

    $pdo->commit();
    echo json_encode(['success' => "$successCount users uploaded successfully"]);
} catch (Exception $e) {
    $pdo->rollBack();
    http_response_code(500);
    echo json_encode(['error' => 'Failed to upload users: ' . $e->getMessage()]);
}
?>