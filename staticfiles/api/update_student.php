<?php
require_once 'config.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    $id = isset($data['id']) ? (int)$data['id'] : null;
    $name = $data['name'] ?? '';
    $regNo = $data['regNo'] ?? '';
    $fatherName = $data['fatherName'] ?? null; // Nullable
    $cgpa = isset($data['cgpa']) ? (float)$data['cgpa'] : null; // Nullable, cast to float

    if (empty($id) || empty($name) || empty($regNo)) {
        echo json_encode(['error' => 'ID, name, and regNo are required']);
        exit;
    }

    try {
        $stmt = $pdo->prepare("UPDATE students SET name = ?, regNo = ?, fatherName = ?, cgpa = ? WHERE id = ?");
        $stmt->execute([$name, $regNo, $fatherName, $cgpa, $id]);
        $rowCount = $stmt->rowCount();

        if ($rowCount > 0) {
            echo json_encode(['success' => 'Student updated successfully']);
        } else {
            echo json_encode(['error' => 'No student found with ID: ' . $id]);
        }
    } catch (PDOException $e) {
        echo json_encode(['error' => 'Failed to update student: ' . $e->getMessage()]);
    }
} else {
    echo json_encode(['error' => 'Invalid request method']);
}
?>