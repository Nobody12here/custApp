<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

require_once 'config.php';

header('Content-Type: application/json');

if (!isset($_GET['table'])) {
    echo json_encode(['error' => 'Table parameter is required']);
    exit;
}

$table = $_GET['table'];
$userType = isset($_GET['user_type']) ? strtolower($_GET['user_type']) : '';

// Whitelist allowed tables to prevent SQL injection
$allowedTables = ['users', 'department', 'programs'];
if (!in_array($table, $allowedTables)) {
    echo json_encode(['error' => 'Invalid table name']);
    exit;
}

try {
    if ($table === 'users') {
        // Define attributes based on user type
        $allAttributes = [
            'user_id', 'uu_id', 'name', 'father_name', 'address', 'program_name', 'dept_name',
            'gender', 'status', 'email', 'created_at', 'updated_at', 'user_type', 'role',
            'designation', 'otp', 'remark', 'phone_number', 'picture', 'cgpa', 'term', 'DoB', 'CNIC'
        ];

        $studentAttributes = [
            'user_id', 'uu_id', 'name', 'father_name', 'address', 'program_name', 'dept_name',
            'gender', 'status', 'email', 'created_at', 'updated_at', 'role', 'otp', 'remark',
            'phone_number', 'picture', 'cgpa', 'term', 'DoB', 'CNIC'
        ];

        $staffAttributes = [
            'user_id', 'uu_id', 'name', 'address', 'gender', 'status', 'email', 'created_at',
            'updated_at', 'role', 'designation', 'remark', 'phone_number', 'picture'
        ];

        if ($userType === 'student') {
            echo json_encode($studentAttributes);
        } elseif ($userType === 'staff') {
            echo json_encode($staffAttributes);
        } else {
            echo json_encode($allAttributes);
        }
    } else {
        // For other tables (department, programs), fetch columns dynamically
        $stmt = $pdo->query("SHOW COLUMNS FROM $table");
        $columns = $stmt->fetchAll(PDO::FETCH_COLUMN);
        echo json_encode($columns);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to fetch attributes: ' . $e->getMessage()]);
}
?>