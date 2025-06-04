# Crear carpetas
$folders = @(
    "app\api\v1\marketplaces",
    "app\api\v1\erp",
    "app\core",
    "app\db\models",
    "app\db\crud",
    "app\db\migrations",
    "app\services\marketplaces",
    "app\services\erps",
    "app\tests\api",
    "app\tests\db",
    "app\tests\services"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}

# Crear archivos
$files = @(
    "app\api\v1\marketplaces\mercadolibre.py",
    "app\api\v1\marketplaces\otro_marketplace.py",
    "app\api\v1\erp\siigo.py",
    "app\api\v1\erp\otro_erp.py",
    "app\api\v1\users.py",
    "app\api\v1\api_router.py",
    "app\core\config.py",
    "app\core\security.py",
    "app\db\base.py",
    "app\db\session.py",
    "app\db\models\user.py",
    "app\db\models\marketplace.py",
    "app\db\models\erp.py",
    "app\db\models\venta.py",
    "app\db\crud\user.py",
    "app\db\crud\marketplace.py",
    "app\db\crud\erp.py",
    "app\db\crud\venta.py",
    "app\services\marketplaces\mercadolibre.py",
    "app\services\marketplaces\otro_marketplace.py",
    "app\services\erps\siigo.py",
    "app\services\erps\otro_erp.py",
    "app\services\cost_calculator.py",
    "app\main.py",
    "requirements.txt",
    "README.md"
)

foreach ($file in $files) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

Write-Host "✅ Estructura de proyecto creada con éxito."
