#!/bin/bash

output_file="respaldo_codigo_completo.txt"
echo "# Respaldo completo del proyecto - $(date)" > "$output_file"
echo "" >> "$output_file"

# Extensiones comunes que quieras incluir, ajusta si necesitás otras
extensiones="py txt md json"

# Recorremos archivos ordenados y concatenamos con encabezados y separadores
find . -type f \( $(printf -- "-iname '*.%s' -o " $extensiones | sed 's/ -o $//') \) | sort | while read -r file; do
    echo "" >> "$output_file"
    echo "# ====================== INICIO: $file ======================" >> "$output_file"
    echo "" >> "$output_file"
    cat "$file" >> "$output_file"
    echo "" >> "$output_file"
    echo "# ====================== FIN: $file =========================" >> "$output_file"
    echo -e "\n\n" >> "$output_file"
done

echo "Respaldo completado en $output_file"
