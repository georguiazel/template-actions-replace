#!/usr/bin/env python3
import argparse
import json
import os
import sys
import io


try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

def parse_replacements(raw: str):
    """
    Convierte 'A.B=1|C=2' en dict {'A.B': 1, 'C': 2} con cast automático:
      - 5, 3.14 → número
      - true/false/null → bool/None
      - resto → string (sin necesidad de comillas)
    """
    replacements = []
    for pair in raw.split("|"):
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        key = key.strip()

        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value.strip().strip('"').strip("'")
        replacements.append((key, parsed_value))
    return replacements

def set_by_path(obj, path_parts, value):
    """Crea dicts intermedios si no existen y asigna el valor al final de la ruta."""
    current = obj
    for k in path_parts[:-1]:
        if k not in current or not isinstance(current[k], dict):
            current[k] = {}
        current = current[k]
    current[path_parts[-1]] = value

def set_value(obj, key, value):
    """
    Reglas:
      - 'nested:K1.K2'  -> trata puntos como ruta anidada
      - 'literal:K1.K2' -> trata la clave literalmente (con puntos)
      - por defecto: si existe clave literal -> reemplaza; si no, usa ruta anidada
    """
    if key.startswith("nested:"):
        dotted = key[len("nested:"):]
        set_by_path(obj, dotted.split("."), value)
        return

    if key.startswith("literal:"):
        literal = key[len("literal:"):]
        obj[literal] = value
        return

    if key in obj:
        obj[key] = value
    else:
        set_by_path(obj, key.split("."), value)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", required=True, help="Archivos separados por |")
    parser.add_argument("--replacements", required=True, help="Reemplazos clave=valor separados por |")
    args = parser.parse_args()

    files = [f for f in args.files.split("|") if f.strip()]
    replacements = parse_replacements(args.replacements)

    if not files:
        print("[X] No se recibieron archivos en --files", file=sys.stderr)
        sys.exit(1)
    if not replacements:
        print("[X] No se recibieron reemplazos en --replacements", file=sys.stderr)
        sys.exit(1)

    for file in files:
        if not os.path.exists(file):
            print(f"[X] Archivo no encontrado: {file}", file=sys.stderr)
            sys.exit(1)

        print(f"Procesando archivo: {file}")
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"[X] El archivo no es JSON válido: {file}", file=sys.stderr)
            sys.exit(1)

        
        for key, val in replacements:
            set_value(data, key, val)

        
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Archivo actualizado: {file}")

        
        try:
            with open(file, "r", encoding="utf-8") as f:
                print("------ contenido actualizado ------")
                print(f.read())
                print("------ fin de archivo ------")
        except Exception:
            
            pass

if __name__ == "__main__":
    main()
