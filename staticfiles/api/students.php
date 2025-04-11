<?php
require_once 'config.php';

header('Content-Type: application/json');

try {
    $stmt = $pdo->query("SELECT id, name, regNo, fatherName, cgpa FROM students");
    $students = $stmt->fetchAll(PDO::FETCH_ASSOC);
    echo json_encode($students);
} catch (PDOException $e) {
    echo json_encode(['error' => 'Failed to fetch students: ' . $e->getMessage()]);
}
?>