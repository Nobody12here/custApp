<?php
require_once 'config.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    $id = isset($data['id']) ? (int)$data['id'] : null;

    if (empty($id)) {
        echo json_encode(['error' => 'ID is required']);
        exit;
    }

    try {
        $stmt = $pdo->prepare("DELETE FROM students WHERE id = ?");
        $stmt->execute([$id]);
        $rowCount = $stmt->rowCount();

        if ($rowCount > 0) {
            echo json_encode(['success' => 'Student deleted successfully']);
        } else {
            echo json_encode(['error' => 'No student found with ID: ' . $id]);
        }
    } catch (PDOException $e) {
        echo json_encode(['error' => 'Failed to delete student: ' . $e->getMessage()]);
    }
} else {
    echo json_encode(['error' => 'Invalid request method']);
}
?>