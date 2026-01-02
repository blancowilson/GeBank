import pyodbc
from app.config import settings

def diagnose_raw():
    conn_str = settings.SQL_SERVER_URL.replace("mssql+aioodbc://", "DRIVER={ODBC Driver 17 for SQL Server};SERVER=").replace("?driver=ODBC+Driver+17+for+SQL+Server", "").replace("/", ";DATABASE=").replace("@", ";UID=").replace(":", ";PWD=")
    # Ajuste manual rápido de la cadena de conexión para pyodbc puro si el parseo falla, 
    # pero intentemos usar la libreria sqlalchemy para obtener la url cruda si es posible, 
    # o mejor aun, usemos la cadena directa que sabemos que funciona.
    
    # Asumiendo localhost y autenticación SQL
    # Reconstruyendo string desde settings para ser seguro
    import sqlalchemy.engine.url
    url = sqlalchemy.engine.url.make_url(settings.SQL_SERVER_URL)
    
    dsn = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={url.host},{url.port or 1433};DATABASE={url.database};UID={url.username};PWD={url.password}"
    
    print(f"Conectando con: SERVER={url.host};DATABASE={url.database}...")
    
    try:
        conn = pyodbc.connect(dsn)
        cursor = conn.cursor()
        
        print("\n--- Columnas en GePagos ---")
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'GePagos'")
        columns = [row[0] for row in cursor.fetchall()]
        print(columns)
        
        print("\n--- Datos (Primeros 5) ---")
        # Seleccionamos todas las columnas dinámicamente
        cursor.execute(f"SELECT TOP 5 * FROM GePagos")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_raw()
