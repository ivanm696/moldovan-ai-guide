<?php
declare(strict_types=1);

require __DIR__ . '/MolTransliterator.php';

$validModes = ['auto', 'lat2cyr', 'cyr2lat'];

// ---- JSON API: index.php?api=1&mode=auto&text=... (GET or POST) ----
if (isset($_REQUEST['api'])) {
    header('Content-Type: application/json; charset=utf-8');
    header('Access-Control-Allow-Origin: *');

    $text = (string) ($_REQUEST['text'] ?? '');
    $mode = (string) ($_REQUEST['mode'] ?? 'auto');
    $mode = in_array($mode, $validModes, true) ? $mode : 'auto';

    echo json_encode([
        'lang'   => MolTransliterator::LANG,
        'mode'   => $mode,
        'script' => MolTransliterator::detectScript($text),
        'input'  => $text,
        'result' => MolTransliterator::convert($text, $mode),
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

// ---- HTML form ----
$text = (string) ($_POST['text'] ?? '');
$mode = (string) ($_POST['mode'] ?? 'auto');
$mode = in_array($mode, $validModes, true) ? $mode : 'auto';
$result = $text !== '' ? MolTransliterator::convert($text, $mode) : '';
$h = static fn (string $s): string => htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
?>
<!doctype html>
<html lang="mol">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>МолТранслатор (PHP)</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
    @media (max-width: 640px) { .grid { grid-template-columns: 1fr; } }
    textarea { width: 100%; height: 12rem; font-size: 1rem; padding: .6rem; box-sizing: border-box; }
    button, select { font-size: 1rem; padding: .5rem .9rem; margin-top: .6rem; }
  </style>
</head>
<body>
  <h1>МолТранслатор</h1>
  <p>Латиницэ ↔ Кириликэ · Стандарт Лумина · ISO 639-3: <code>mol</code></p>
  <form method="post">
    <div class="grid">
      <div>
        <label for="text"><b>Сурсэ</b></label>
        <textarea id="text" name="text"><?= $h($text) ?></textarea>
      </div>
      <div>
        <label for="out"><b>Резултат</b></label>
        <textarea id="out" readonly><?= $h($result) ?></textarea>
      </div>
    </div>
    <select name="mode">
      <option value="auto"    <?= $mode === 'auto' ? 'selected' : '' ?>>Аутомат</option>
      <option value="lat2cyr" <?= $mode === 'lat2cyr' ? 'selected' : '' ?>>Латиницэ → Кириликэ</option>
      <option value="cyr2lat" <?= $mode === 'cyr2lat' ? 'selected' : '' ?>>Кириликэ → Латиницэ</option>
    </select>
    <button type="submit">⚡ Конвертеште</button>
  </form>
  <p><small>API: <code>index.php?api=1&amp;mode=auto&amp;text=Chișinău</code></small></p>
</body>
</html>
