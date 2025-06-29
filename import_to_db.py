import os
import csv
import sqlite3

DATA_FOLDER = "data/raw"
DB_NAME = "mlb_almanac.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

def create_table(table_name):
    sql = f'''
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        year INTEGER,
        statistic TEXT,
        name TEXT,
        team TEXT,
        value TEXT,
        top_25 TEXT
    )
    '''
    cursor.execute(sql)
    conn.commit()

def import_file(year):
    filename = f"mlb_almanac_{year}.csv"
    filepath = os.path.join(DATA_FOLDER, filename)
    table_name = f"mlb_almanac_{year}"

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    create_table(table_name)

    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Table {table_name} already contains data, skipping import.")
        return

    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row or all(cell.strip() == "" for cell in row):
                continue
            
            if row[0].strip().lower() == "statistic":
                continue
            
            first_cell = row[0].strip()
            if first_cell and first_cell[0].isdigit() and "history" in first_cell.lower():
                continue

            if len(row) < 5:
                print(f"Warning: skipping malformed row in {filename}: {row}")
                continue
            
            try:
                cursor.execute(f'''
                    INSERT INTO "{table_name}" (year, statistic, name, team, value, top_25)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (year, row[0], row[1], row[2], row[3], row[4]))
            except Exception as e:
                print(f"Failed to insert row {row} in {filename}: {e}")

    conn.commit()
    print(f"Imported {filename} into table {table_name} successfully.")

def main():
    for year in range(1876, 2026):
        import_file(year)
    conn.close()

if __name__ == "__main__":
    main()





