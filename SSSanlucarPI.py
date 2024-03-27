import folium
from folium.plugins import AntPath
import csv
import subprocess
from datetime import datetime
from time import sleep

mapa = None

co_paz =    [
    [36.775430045,-6.352014287],
    [36.77514294,-6.352474633],
    [36.774970275,-6.352758988],
    [36.77486534,-6.352924378],
    [36.775503403,-6.353238416],
    [36.775833181,-6.353389544],
    [36.77587188,-6.353210675],
    [36.775913106,-6.353229844],
    [36.775885159,-6.353346188],
    [36.776175999,-6.353466586],
    [36.776149699,-6.353544139],
    [36.775853945,-6.3534058],
    [36.775749242,-6.353902114]
]

co_ancha =  [
    [36.778150939,-6.355029923],
    [36.778698496,-6.353783418],
    [36.779432716,-6.352181243]
]

ruta1 = []
ruta2 = []
ruta3 = []

hdad1 = ["Estudiantes", "blue"]
hdad2 = ["Dolores", "red"]
hdad3 = ["", ""]

class Hermandad:

    def __init__(self, nombre, logo, fecha_inicio, fecha_fin, hora_pos):
        self.nombre = nombre
        self.logo = logo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.hora_pos = hora_pos

def main():

    global mapa

    hermandades = []

    #GENERACIÓN DE MAPA BASE
    mapa = generar_mapa("")
    actualizar_mapa()

    #CARGA DE DATOS
    print("***** CARGA DE DATOS  *****")

    with open('/home/ing/sssanlucar.github.io/SSSanlucar2024.csv', encoding="utf8") as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=';')
        cabecera = None
        for row in csv_reader:
            if cabecera == None:
                cabecera = row
            else:
                hora_pos = {}
                for i in range(4, 292):
                    if row[i] != "": hora_pos[cabecera[i]] = row[i]
                hermandades.append(Hermandad(row[0],row[1],row[2],row[3],hora_pos))

    for hermandad in hermandades:
        print(hermandad.nombre , " " , hermandad.fecha_inicio, " " , hermandad.fecha_fin, " " , hermandad.hora_pos)
    
    print("***** CARGA DE DATOS FINALIZADA *****")

    leer_rutas(10,11,-1) #Lee las rutas de las hermandades, el 0 es la Bondad, el 1 es Tercera Caida, etc. Si se pone -1, se omite la lectura.

    #BUCLE EN TIEMPO REAL
    while True:

        now = datetime.now()
        #now = datetime(2024,3,24,20,40,00,00)
        if((now.minute%5==0) and (now.second==0)):
            fecha_actual = now.strftime('%d/%m/%Y-%H:%M')
            print("ACTUALIZACIÓN: ", fecha_actual)
            mapa = generar_mapa(fecha_actual)
            añadir_carrera_oficial()
            añadir_itinerario(ruta1, hdad1[1], hdad1[0])
            añadir_itinerario(ruta2, hdad2[1], hdad2[0])
            añadir_itinerario(ruta3, hdad3[1], hdad3[0])
            for hermandad in hermandades:
                if((fecha_actual >= hermandad.fecha_inicio) and (fecha_actual <= hermandad.fecha_fin)):
                    print(hermandad.nombre)
                    pos = hermandad.hora_pos.get(fecha_actual.split("-")[1])
                    añadir_marcador(hermandad.nombre, hermandad.logo, pos)
            actualizar_mapa()
            subprocess.call(["/home/ing/sssanlucar.github.io/git.sh"])
            sleep(1)

def generar_mapa(fecha_actual):
    return folium.Map(location = [36.775871284198246, -6.353200236926841], tiles="Cartodb VoyagerLabelsUnder", zoom_start = 16, attr = ("@pablo_ng98 @isidrong_ | " + fecha_actual))

def actualizar_mapa():
    global mapa, hdad1, hdad2

    mapa = add_categorical_legend(mapa, 'Leyenda',
                                  colors=[hdad1[1], hdad2[1]],
                                  labels=[hdad1[0], hdad2[0]])

    mapa.get_root().html.add_child(folium.Element("""
    <div style="position: fixed; top: 20px; left: 70px; width: auto; height: auto; background-color:white;border:2px solid grey; z-index: 900;">
        <h5>  Pendiente de partes meteorológicos </h5>
    </div>
    <meta http-equiv="refresh" content="300">
    """))

    #<br> -Borriquita no hace estación de penitencia  <br> -Sagrada Cena no hace estación de penitencia  <br> -Oración en el Huerto no hace estación de penitencia <br> -Pusillus Grex no hace estación de penitencia

    mapa.save(outfile="/home/ing/sssanlucar.github.io/index.html")

def añadir_carrera_oficial():
    global mapa

    folium.PolyLine(locations = co_paz, color = " #2874A6", weight = 5, tooltip = "Carrera Oficial - Plaza de la Paz").add_to(mapa)
    folium.PolyLine(locations = co_ancha, color = " #2874A6", weight = 5, tooltip = "Carrera Oficial - Calle Ancha").add_to(mapa)

def añadir_marcador(nombre, logo, pos):
        global mapa

        nombre_tramo = nombre.split(": ")
        pos_act = pos.split(";")

        html =  """
                <h6><p style = "text-align: center;"><b>{her}</b></h6>
                <p style = "text-align: center;">{tramo}</p>
                """.format(her = nombre_tramo[0], tramo = nombre_tramo[1])

        icono = folium.CustomIcon(
            logo,
            icon_size=(50, 50),
            popup_anchor=(0, -25)
        )

        folium.Marker(location=[float(pos_act[0]),float(pos_act[1])],
                      icon = icono,
                      popup = folium.Popup(html, max_width = 100, lazy = True)).add_to(mapa)

def leer_rutas(hdadID1, hdadID2, hdadID3):

    global ruta1
    global ruta2
    global ruta3

    if hdadID1 != -1:
        ruta1 = leer_ruta(hdadID1)
    if hdadID2 != -1:
        ruta2 = leer_ruta(hdadID2)
    if hdadID3 != -1:
        ruta3 = leer_ruta(hdadID3)

def leer_ruta(columna):
    coordenadas = []  # Lista para almacenar las tuplas de coordenadas

    with open('/home/ing/sssanlucar.github.io/SSSanlucar2024-Itinerarios.csv', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)
        for row in reader:
            # Asumiendo que las coordenadas están en la primera columna, ajusta según sea necesario
            try:
                partes = row[columna].split(',')  # Intenta dividir la cadena de coordenadas
                if len(partes) != 2:
                    raise ValueError(
                        f"Formato incorrecto, se esperaban 2 partes (latitud y longitud), pero se obtuvieron {len(partes)}")
                latitud, longitud = map(float, partes)  # Convierte las partes en floats
                coordenadas.append((latitud, longitud))
            except ValueError as e:
                print(f"Error procesando fila {reader.line_num}: {e}")
                print(f"Fila problemática: {row}")

    print(coordenadas)
    return coordenadas

def añadir_itinerario(coord, color, nombre):
    global mapa
    try:
        folium.plugins.AntPath(locations=coord, color=color, weight=3, tooltip=nombre, dash_array=[30, 50],
                               delay=5000).add_to(mapa)
        #folium.PolyLine(locations=coord, color=color, weight=1, tooltip=nombre).add_to(mapa)
    except:
        print("Ruta vacia")


def add_categorical_legend(folium_map, title, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))

    legend_categories = ""
    for label, color in color_by_label.items():
        legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"

    legend_html = f"""
    <div id='maplegend' class='maplegend'>
      <div class='legend-title'>{title}</div>
      <div class='legend-scale'>
        <ul class='legend-labels'>
        {legend_categories}
        </ul>
      </div>
    </div>
    """
    script = f"""
        <script type="text/javascript">
        var oneTimeExecution = (function() {{
                    var executed = false;
                    return function() {{
                        if (!executed) {{
                             var checkExist = setInterval(function() {{
                                       if ((document.getElementsByClassName('leaflet-top leaflet-right').length) || (!executed)) {{
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.display = "flex"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.flexDirection = "column"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].innerHTML += `{legend_html}`;
                                          clearInterval(checkExist);
                                          executed = true;
                                       }}
                                    }}, 100);
                        }}
                    }};
                }})();
        oneTimeExecution()
        </script>
      """

    css = """

    <style type='text/css'>
      .maplegend {
        z-index:9999;
        float:right;
        background-color: rgba(255, 255, 255, 1);
        border-radius: 5px;
        border: 2px solid #bbb;
        padding: 10px;
        font-size:12px;
        positon: relative;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    """

    folium_map.get_root().header.add_child(folium.Element(script + css))

    return folium_map

#LLAMADA A LA FUNCIÓN MAIN
if __name__ == "__main__":
    main()