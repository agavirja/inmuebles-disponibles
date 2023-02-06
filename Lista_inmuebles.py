import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import pandas as pd
import mysql.connector as sql
from bs4 import BeautifulSoup
from shapely.geometry import Polygon,Point
from price_parser import Price

# C:\Users\LENOVO T14\Documents\GitHub\BUYDEPA\inmuebles-disponibles
# streamlit run D:\Dropbox\Empresa\Buydepa\COLOMBIA\DESARROLLO\app_inmuebles_oferta_buydepa\online\Lista_inmuebles.py
# https://streamlit.io/
# pipreqs --encoding utf-8 "D:\Dropbox\Empresa\Buydepa\COLOMBIA\DESARROLLO\app_inmuebles_oferta_buydepa\online"

st.set_page_config(layout="wide",initial_sidebar_state="collapsed")

user     = st.secrets["user"]
password = st.secrets["password"]
host     = st.secrets["host"]
database = st.secrets["schema"]

def get_url(x):
    urllink = ''
    for i in ['url_domus','url_fr','url_m2','url_cc','url_meli']:
        if i in x and isinstance(x[i], str) and len(x[i])>20:
            urllink = x[i]
            break    
    return urllink

@st.experimental_memo
def data_gestion():
    db_connection = sql.connect(user=user, password=password, host=host, database=database)
    data          = pd.read_sql("SELECT * FROM colombia.data_stock_inmuebles_gestion" , con=db_connection)
    data['url']   = data.apply(lambda x: get_url(x), axis=1)
    return data

@st.experimental_memo
def data_img():
    db_connection = sql.connect(user=user, password=password, host=host, database=database)
    data          = pd.read_sql("SELECT * FROM colombia.data_stock_inmuebles_img" , con=db_connection)
    return data

@st.experimental_memo
def data_caracteristicas():
    db_connection = sql.connect(user=user, password=password, host=host, database=database)
    data          = pd.read_sql("SELECT * FROM colombia.data_stock_inmuebles_caracteristicas" , con=db_connection)
    return data

@st.experimental_memo
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

data                = data_gestion()
dataimg             = data_img()
datacaracteristicas = data_caracteristicas()
data                = data[data['estado_venta']=='ADMINISTRADO']

if data.empty is False:
    dataimg             = dataimg[dataimg['id_inmueble'].isin(data['id_inmueble'])]
    datacaracteristicas = datacaracteristicas[datacaracteristicas['id_inmueble'].isin(data['id_inmueble'])]
    datacaracteristicas.drop(columns=['nombre_conjunto'],inplace=True)
    data                = data[['id_inmueble','nombre_conjunto','precio_lista_venta','porcentaje_comision','url_domus','url_fr', 'url_m2','url_cc', 'url_meli']]
    data.rename(columns={'precio_lista_venta':'precio_venta'},inplace=True)
    data                = data.merge(dataimg[['id_inmueble','url_img1']],on=['id_inmueble'],how='left',validate='1:1')
    data                = data.merge(datacaracteristicas,on=['id_inmueble'],how='left',validate='1:1')
    data.index = range(len(data))
    idd = data.index>=0
    
    
    #-------------------------------------------------------------------------#
    # Descargar data
    variables = ['id_inmueble','estado_venta','precio_venta','porcentaje_comision','tipoinmueble','localidad','upz','barriocatastral','barriocomun','ciudad','direccion','nombre_conjunto','valoradministracion','estrato','areaconstruida','areaprivada','habitaciones','banos','garajes','depositos','piso','antiguedad','ascensores','numerodeniveles','url','url_img1','url_img2','url_img3','url_img4','url_img5','url_img6','url_img7','url_img8','url_img9','url_img10','url_img11','url_img12','url_img13','url_img14','url_img15','url_img16','url_img17','url_img18','url_img19','url_img20','url_img21','url_img22','url_img23','url_img24','url_img25','latitud','longitud','ph','chip','matricula','cedula_catastral','porteria','circuito_cerrado','lobby','salon_comunal','parque_infantil','terraza','sauna','turco','jacuzzi','cancha_multiple','cancha_baloncesto','cancha_voleibol','cancha_futbol','cancha_tenis','cancha_squash','salon_juegos','gimnasio','zona_bbq','sala_cine','piscina']
    variables = [x for x in variables if x in data]
    datadownload = data[variables]
    reanmeformat = {'id_inmueble':'Codigo','estado_venta':'Estado','precio_venta':'Precio','porcentaje_comision':'Comision (%)','tipoinmueble':'Tipo inmueble','ciudad':'Ciudad','localidad':'Localidad','upz':'UPZ','barriocatastral':'Barrio','barriocomun':'Barrio comun','direccion':'Direccion','nombre_conjunto':'Nombre edificio','valoradministracion':'Administracion','estrato':'Estrato','areaconstruida':'Area construida','areaprivada':'Area privada','habitaciones':'Habitaciones','banos':'Banos','garajes':'Garajes','depositos':'Depositos','piso':'Piso','antiguedad':'Antiguedad','ascensores':'Ascensores','numerodeniveles':'Niveles','latitud':'Latitud','longitud':'Longitud','ph':'Propiedad Horizontal','chip':'Chip','matricula':'Matricula Inmobiliaria','cedula_catastral':'Cedula catastral','porteria':'Porteria','circuito_cerrado':'Circuito cerrado','lobby':'Lobby','salon_comunal':'Salon comunal','parque_infantil':'Parque infantil','terraza':'Terraza','sauna':'Sauna','turco':'Turco','jacuzzi':'Jacuzzi','cancha_multiple':'Cancha multiple','cancha_baloncesto':'Cancha de baloncesto','cancha_voleibol':'Cancha de voleibol','cancha_futbol':'Cancha de futbol','cancha_tenis':'Cancha de tenis','cancha_squash':'Cancha de squash','salon_juegos':'Salon de juegos','gimnasio':'GYM','zona_bbq':'Zona de BBQ','sala_cine':'Sala de cine','piscina':'Piscina'}
    datadownload.rename(columns=reanmeformat,inplace=True)
    
    #-------------------------------------------------------------------------#
    # Mapa
    col1, col2, col3 = st.columns([1,1,6])

    # Filtro por Precio
    preciominq = int(data['precio_venta'].min())
    preciomaxq = int(data['precio_venta'].max())
        
    with col1:
        preciomin = st.text_input('Precio mínimo',value=f'${preciominq:,.0f}')
        preciomin = Price.fromstring(preciomin).amount_float
        
    with col2:
        preciomax = st.text_input('Precio máximo',value=f'${preciomaxq:,.0f}')
        preciomax = Price.fromstring(preciomax).amount_float
    idd = (idd) & (data['precio_venta']>=preciomin) & (data['precio_venta']<=preciomax)
    
    # Filtro por area     
    areaminq        = int(data[idd]['areaconstruida'].min())
    areamaxq        = int(data[idd]['areaconstruida'].max())
    if areaminq>=areamaxq: areaminq = areamaxq-1
    
    with col1:
        areamin = st.number_input('Área construida mínima',value=areaminq)
    with col2:
        areamax = st.number_input('Área construida máxima',value=areamaxq)
    idd = (idd) & (data['areaconstruida']>=areamin) & (data['areaconstruida']<=areamax)
        
    with col1:
        csv = convert_df(datadownload)

        st.download_button(
           "Descargar disponibles",
           csv,
           "info_completa.csv",
           "text/csv",
           key='descarga-csv'
        )


    with col3:
        default_lat = 4.663344
        default_lng = -74.076695
    
        m    = folium.Map(location=[default_lat, default_lng], zoom_start=10,tiles="cartodbpositron")
        for i, inmueble in data.iterrows():
            folium.Marker(location=[inmueble["latitud"], inmueble["longitud"]]).add_to(m)
        draw = Draw(
                    draw_options={"polyline": False,"marker": False,"circlemarker":False},
                    edit_options={"poly": {"allowIntersection": False}}
                    )
        draw.add_to(m)
        st_map = st_folium(m,width=1200,height=350)
    
        polygon     = None
        polygonType = ''
        if 'all_drawings' in st_map and st_map['all_drawings'] is not None:
            if st_map['all_drawings']!=[]:
                if 'geometry' in st_map['all_drawings'][0] and 'type' in st_map['all_drawings'][0]['geometry']:
                    polygonType = st_map['all_drawings'][0]['geometry']['type']
            
        if 'point' in polygonType.lower():
            coordenadas = st_map['last_circle_polygon']['coordinates']
            polygon     = Polygon(coordenadas[0])
    
        if 'polygon' in polygonType.lower():
            coordenadas = st_map['all_drawings'][0]['geometry']['coordinates']
            polygon     = Polygon(coordenadas[0])
    
        if polygon is not None:
            data['geometry'] = data.apply(lambda x: Point(x['longitud'],x['latitud']),axis=1)
            idd  = (idd) & (data['geometry'].apply(lambda x: polygon.contains(x)))
    
    #-------------------------------------------------------------------------#
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Filtro por estrato
        st.text('Estrato')
        idj = data.index<0
        for i in range(2,7):
            checkitem = st.checkbox(f'Estrato {i}',value=True) 
            if checkitem:
                idj = (idj) | (data['estrato']==i)
        idd = (idd) & (idj)

    with col2:
        # Filtro por habitaciones
        st.text('Habitaciones')
        idj = data.index<0
        for i in range(1,5):
            name = 'habitaciones'
            if i==1: name = 'habitación'
            checkitem = st.checkbox(f'{i} {name}',value=True) 
            if checkitem:
                idj = (idj) | (data['habitaciones']==i)
        idd = (idd) & (idj) 

    with col3:
        # Filtro por banos
        st.text('Baños')
        idj = data.index<0
        for i in range(1,5):
            name = 'baños'
            if i==1: name = 'baño'
            checkitem = st.checkbox(f'{i} {name}',value=True) 
            if checkitem:
                idj = (idj) | (data['banos']==i)
        idd = (idd) & (idj) 

    with col4:
        # Filtro por banos
        st.text('Garajes')
        idj = data.index<0
        for i in range(0,4):
            name = 'garajes'
            if i==1: name = 'garaje'
            checkitem = st.checkbox(f'{i} {name}',value=True) 
            if checkitem:
                idj = (idj) | (data['garajes']==i)
        idd = (idd) & (idj) 
            
    data = data[idd]
    #-------------------------------------------------------------------------#
    # Inmuebles
    st.write('---')
    css_format = """
        <style>
          .property-card-left {
            width: 100%;
            height: 800px; /* or max-height: 300px; */
            overflow-y: scroll; /* enable vertical scrolling for the images */
            text-align: center;
            display: inline-block;
            margin: 0px auto;
          }
    
          .property-block {
            width:32%;
            background-color: white;
            border: 1px solid gray;
            box-shadow: 2px 2px 2px gray;
            padding: 3px;
            margin-bottom: 10px; 
      	    display: inline-block;
      	    float: left;
            margin-right: 10px; 
          }

          .property {
            border: 1px solid gray;
            box-shadow: 2px 2px 2px gray;
            padding: 10px;
            margin-bottom: 10px;
          }
          
          .property-image{
            flex: 1;
          }
          .property-info{
            flex: 1;
          }
          
          .price-info {
            font-family: 'Comic Sans MS', cursive;
            font-size: 24px;
            margin-bottom: 1px;
          }
     
          .admon-info {
            font-family: 'Comic Sans MS', cursive;
            font-size: 12px;
            margin-bottom: 5px;
          }
          
          .caracteristicas-info {
            font-size: 16px;
            margin-bottom: 2px;
          }
          img{
            max-width: 50%;
            width: 100%;
            object-fit: cover;
            margin-bottom: 10px; 
          }
        </style>
    """

    imagenes = ''
    for i, inmueble in data.iterrows():

        if isinstance(inmueble['url_img1'], str) and len(inmueble['url_img1'])>20: imagen_principal =  inmueble['url_img1']
        else: imagen_principal = "https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png"
        codigo = (inmueble['id_inmueble']*5 + 2)**2
        caracteristicas = f'<strong>{inmueble["areaconstruida"]}</strong> mt<sup>2</sup> | <strong>{int(inmueble["habitaciones"])}</strong> hab | <strong>{int(inmueble["banos"])}</strong> baños | <strong>{int(inmueble["garajes"])}</strong> pq'
        url_export      = f'''https://inmuebles-disponibles.streamlit.app/Ficha?idcodigo={codigo}'''
        imagenes += f'''
              <div class="property-block">
                <a href="{url_export}" target="_blank">
                <div class="property-image">
                  <img src="{imagen_principal}" alt="property image" onerror="this.src='https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png';">
                </div>
                </a>
                <p class="price-info">${inmueble['precio_venta']:,.0f}</h3>
                <p class="caracteristicas-info">Dirección: {inmueble['direccion']}</p>
                <p class="caracteristicas-info">Dirección: {inmueble['nombre_conjunto']}</p>
                <p class="caracteristicas-info">{caracteristicas}</p>
              </div>
              '''
    texto = f"""
        <!DOCTYPE html>
        <html>
          <head>
          {css_format}
          </head>
          <body>
        <div class="property-card-left">
        {imagenes}
        </div>
          </body>
        </html>
        """
    texto = BeautifulSoup(texto, 'html.parser')
    st.markdown(texto, unsafe_allow_html=True)