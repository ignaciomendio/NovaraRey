from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import pdfplumber
import pandas as pd

def scrape_first_row(url):
    # 1. Abrir la URL
    with urlopen(url) as resp:
        html = resp.read()

    # 2. Parsear el HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 3. Encontrar la segunda tabla
    table = soup.find_all('table')[1]

    # 4. Obtener filas y extraer la primera de datos
    first_data_row = table.find_all('tr')[1]

    # 5. Leer cada celda
    cells = first_data_row.find_all('td')
    fecha = cells[2].get_text(strip=True)[0:10]  # Fecha en formato 'dd/mm/yyyy'
    link = urljoin(url,cells[3].find('a')['href'])  # Enlace al PDF
    return {'fecha': fecha, 'link': link}


def update_last_update(data):
    script_dir = Path(__file__).resolve().parent
    file_path = script_dir / 'lastupdate.txt'
    new_fecha = data.get('fecha')
    new_link = data.get('link')
    if file_path.exists():
        with open(file_path, 'r') as f:
            last_data = f.read().strip().splitlines()
        last_fecha = last_data[0]
        print(f'Fecha guardada: {last_fecha}')
    else:
        last_fecha = None
    if last_fecha != new_fecha:
        with open(file_path, 'w') as f:
            f.write(f"{new_fecha}\n{new_link}")
        dest_path = script_dir / "lastupdate.pdf"
        with urlopen(new_link) as resp:
            with open(dest_path, 'wb') as pdf_file:
                pdf_file.write(resp.read())
        return True
    return False


def extract_table_all_pages(pdf_path, table_index=0):
    """
    Extrae la tabla 'table_index' de cada página del PDF y la concatena en un DataFrame.
    Asume que cada tabla tiene el mismo encabezado en la primera página.
    """
    all_rows = []
    headers = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if len(tables) > table_index:
                table = tables[table_index]
                # La primera fila se considera encabezado
                if headers is None:
                    headers = table[0]
                # Filas de datos sin encabezado repetido
                data_rows = table[1:]
                all_rows.extend(data_rows)

    # Crear DataFrame final
    df = pd.DataFrame(all_rows, columns=headers)
    return df

if __name__ == '__main__':
    URL = 'https://www.dnrpa.gov.ar/valuacion/valuaciones.php'
    try:
        if update_last_update(scrape_first_row(URL)):
            print("Datos actualizados correctamente.")
        else:
            print("No hay cambios en los datos.")
    except Exception as e:
        print("Error al scrapear:", e)
    pdf = Path(__file__).resolve().parent / "lastupdate.pdf"
    df = extract_table_all_pages(pdf, table_index=0)


