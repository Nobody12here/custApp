<?php
require_once '../vendor/autoload.php';
require_once 'config.php';

use Spatie\PdfToHtml\Pdf;

header('Content-Type: application/json');

if (!isset($_FILES['pdf']) || $_FILES['pdf']['error'] !== UPLOAD_ERR_OK) {
    echo json_encode(['error' => 'No valid PDF file uploaded']);
    exit;
}

$uploadedFile = $_FILES['pdf']['tmp_name'];
$outputDir = sys_get_temp_dir();

try {
    $pdf = new Pdf($uploadedFile);
    $html = $pdf->setOutputDirectory($outputDir)->getHtml();

    if ($html) {
        echo json_encode(['success' => true, 'html' => $html]);
    } else {
        echo json_encode(['error' => 'Failed to convert PDF to HTML']);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Conversion error: ' . $e->getMessage()]);
}
?>