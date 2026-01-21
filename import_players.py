"""
Integración con Google Sheets - Base de Datos de Jugadores
GARGUEL v1.1

Base de datos oficial:
https://docs.google.com/spreadsheets/d/1HW-weeq79GRnoZNcfbj7bINVaDv55WVl/edit

Créditos: Creador de la base de datos de jugadores de IEVR
Copyright GARGUEL: (c) 2026 kazah-png
GitHub: https://github.com/kazah-png/GARGUEL
"""

import pandas as pd
import sqlite3

SHEET_URL = "https://docs.google.com/spreadsheets/d/1HW-weeq79GRnoZNcfbj7bINVaDv55WVl/export?format=csv&gid=1403097221"

def import_players_from_google_sheets():
    try:
        print("📥 Descargando base de datos de jugadores...")
        print("🔗 Fuente: Google Sheets IEVR")
        
        df = pd.read_csv(SHEET_URL)
        print(f"✅ {len(df)} jugadores encontrados")
        
        conn = sqlite3.connect('garguel.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                position TEXT,
                element TEXT,
                rarity TEXT,
                overall INTEGER
            )
        """)
        
        imported = 0
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO players (name, position, element, rarity, overall)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    str(row.get('name', row.get('Name', ''))),
                    str(row.get('position', row.get('Position', ''))),
                    str(row.get('element', row.get('Element', ''))),
                    str(row.get('rarity', row.get('Rarity', ''))),
                    int(row.get('overall', row.get('Overall', 0)))
                ))
                imported += 1
            except:
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✅ {imported} jugadores importados a garguel.db")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GARGUEL v1.1 - Importador de Jugadores")
    print("Copyright (c) 2026 kazah-png")
    print("GitHub: https://github.com/kazah-png/GARGUEL")
    print("="*60 + "\n")
    
    import_players_from_google_sheets()
    
    print("\n✅ Importación completada")
    input("\nPresiona Enter para salir...")
