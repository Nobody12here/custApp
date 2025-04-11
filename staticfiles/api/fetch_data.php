<?php
require_once 'config.php';

try {
    $tables = ['students', 'faculty', 'department', 'programs'];
    $data = [];

    foreach ($tables as $table) {
        $stmt = $pdo->query("SELECT * FROM $table LIMIT 1"); // Fetch first record
        $data[$table] = $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    echo json_encode($data);
} catch (PDOException $e) {
    echo json_encode(['error' => 'Failed to fetch data: ' . $e->getMessage()]);
}
?>