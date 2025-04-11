<?php
require_once 'config.php';

try {
    $stmt = $pdo->query("SELECT * FROM faculty");
    $faculty = $stmt->fetchAll(PDO::FETCH_ASSOC);
    echo json_encode($faculty);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Database error: ' . $e->getMessage()]);
}
?>