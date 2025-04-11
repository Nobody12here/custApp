<?php
require_once 'config.php';
require_once './vendor/autoload.php';

use Dompdf\Dompdf;

header('Content-Type: application/pdf');
header('Content-Disposition: attachment; filename="generated.pdf"');

if (!isset($_POST['name']) || !isset($_POST['content'])) {
    http_response_code(400);
    echo "Error: Name and content are required";
    exit;
}

$name = $_POST['name'];
$content = $_POST['content'];

try {
    $dompdf = new Dompdf();
    $html = "<!DOCTYPE html>
             <html>
             <head>
                 <title>$name</title>
                 <style>
                     body { font-family: Arial, sans-serif; }
                     h1 { color: #333; }
                 </style>
             </head>
             <body>
                 <h1>$name</h1>
                 $content
             </body>
             </html>";

    $dompdf->loadHtml($html);
    $dompdf->setPaper('A4', 'portrait');
    $dompdf->render();
    $dompdf->stream("{$name}.pdf", ['Attachment' => false]);
} catch (Exception $e) {
    http_response_code(500);
    echo "Error generating PDF: " . $e->getMessage();
    exit;
}

exit;
?>