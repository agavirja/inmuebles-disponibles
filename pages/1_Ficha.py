import streamlit as st
import folium
import re
import json
import math
import pandas as pd
import mysql.connector as sql
import pdfcrowd
import tempfile
from streamlit_folium import st_folium
from bs4 import BeautifulSoup

# C:\Users\LENOVO T14\Documents\GitHub\BUYDEPA\inmuebles-disponibles
#st.set_page_config(layout="wide",initial_sidebar_state="collapsed")
st.set_page_config(layout="wide")

API_KEY      = st.secrets["API_KEY"]
pdfcrowduser = st.secrets["pdfcrowduser"]
pdfcrowdpass = st.secrets["pdfcrowdpass"]

user     = st.secrets["user"]
password = st.secrets["password"]
host     = st.secrets["host"]
database = st.secrets["schema"]

#-------------------------------------------------------------------------#
# Datos de contacto
datos_contacto = [{'nombre':'Karen Cano','tel':'(57) 3107270212'},
                  {'nombre':'Viviana Diaz','tel':'(57) 3108691308'}]
                  
# https://pdfcrowd.com/pricing/api/?api=v2
# https://pdfcrowd.com/user/account/stats/

@st.cache_data
def data_gestion(id_inmueble):
    db_connection = sql.connect(user=user, password=password, host=host, database=database)
    data          = pd.read_sql(f"SELECT * FROM colombia.data_stock_inmuebles_gestion WHERE id_inmueble={id_inmueble}" , con=db_connection)
    return data

@st.cache_data
def data_img(id_inmueble):
    db_connection = sql.connect(user=user, password=password, host=host, database=database)
    data          = pd.read_sql(f"SELECT * FROM colombia.data_stock_inmuebles_img WHERE id_inmueble={id_inmueble}" , con=db_connection)
    return data

@st.cache_data
def data_caracteristicas(id_inmueble):
    db_connection = sql.connect(user=user, password=password, host=host, database=database)
    data          = pd.read_sql(f"SELECT * FROM colombia.data_stock_inmuebles_caracteristicas WHERE id_inmueble={id_inmueble}" , con=db_connection)
    return data

@st.cache_data
def data_documents(id_inmueble):
    db_connection = sql.connect(user=user, password=password, host=host, database=database)
    data          = pd.read_sql(f"SELECT id_inmueble,venta_relevantfiles FROM colombia.data_stock_inmuebles_documents WHERE id_inmueble={id_inmueble}" , con=db_connection)
    return data

@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

# obtener los argumentos de la url
args = st.experimental_get_query_params()
if 'idcodigo' in args: 
    try:    idcodigo = args['idcodigo'][0]
    except: idcodigo = ''
else: idcodigo = ''
with st.sidebar:
    try:    
        idcodigo = int((math.sqrt(int(idcodigo))-2)/5)
        idcodigo = str(idcodigo)
    except: pass
    idcodigo = st.text_input('Id del inmueble',value=idcodigo)
    if idcodigo=='': idcodigo = 0 
    idcodigo = (int(idcodigo)*5 + 2)**2

data = pd.DataFrame()
try: 
    id_inmueble         = int((math.sqrt(int(idcodigo))-2)/5) 
    data                = data_gestion(id_inmueble)
    dataimg             = data_img(id_inmueble)
    datacaracteristicas = data_caracteristicas(id_inmueble)
    datadocumentos      = data_documents(id_inmueble)
    if data.empty is False:
        data = data[['id_inmueble','estado_venta','nombre_conjunto','precio_lista_venta','porcentaje_comision','url_domus','url_fr', 'url_m2','url_cc', 'url_meli']]
    if dataimg.empty is False:
        data = data.merge(dataimg,on=['id_inmueble'],how='left',validate='1:1')
    if datacaracteristicas.empty is False:
        if 'nombre_conjunto' in  datacaracteristicas: del datacaracteristicas['nombre_conjunto']
        data = data.merge(datacaracteristicas,on=['id_inmueble'],how='left',validate='1:1')
    if datadocumentos.empty is False:
        data = data.merge(datadocumentos,on=['id_inmueble'],how='left',validate='1:1')
except: pass

if data.empty is False:
    
    urllink = ''
    for i in ['url_domus','url_fr','url_m2','url_cc','url_meli']:
        if i in data and isinstance(data[i].iloc[0], str) and len(data[i].iloc[0])>20:
            urllink = data[i].iloc[0]
            break

    variables = ['id_inmueble','estado_venta','precio_lista_venta','porcentaje_comision','tipoinmueble','localidad','upz','barriocatastral','barriocomun','ciudad','direccion','nombre_conjunto','valoradministracion','estrato','areaconstruida','areaprivada','habitaciones','banos','garajes','depositos','piso','antiguedad','ascensores','numerodeniveles','url_img1','url_img2','url_img3','url_img4','url_img5','url_img6','url_img7','url_img8','url_img9','url_img10','url_img11','url_img12','url_img13','url_img14','url_img15','url_img16','url_img17','url_img18','url_img19','url_img20','url_img21','url_img22','url_img23','url_img24','url_img25','latitud','longitud','ph','chip','matricula','cedula_catastral','porteria','circuito_cerrado','lobby','salon_comunal','parque_infantil','terraza','sauna','turco','jacuzzi','cancha_multiple','cancha_baloncesto','cancha_voleibol','cancha_futbol','cancha_tenis','cancha_squash','salon_juegos','gimnasio','zona_bbq','sala_cine','piscina']
    variables = [x for x in variables if x in data]
    datadownload = data[variables]
    datadownload['url'] = urllink
    reanmeformat = {'id_inmueble':'Codigo','estado_venta':'Estado','precio_lista_venta':'Precio','porcentaje_comision':'Comision (%)','tipoinmueble':'Tipo inmueble','ciudad':'Ciudad','localidad':'Localidad','upz':'UPZ','barriocatastral':'Barrio','barriocomun':'Barrio comun','direccion':'Direccion','nombre_conjunto':'Nombre edificio','valoradministracion':'Administracion','estrato':'Estrato','areaconstruida':'Area construida','areaprivada':'Area privada','habitaciones':'Habitaciones','banos':'Banos','garajes':'Garajes','depositos':'Depositos','piso':'Piso','antiguedad':'Antiguedad','ascensores':'Ascensores','numerodeniveles':'Niveles','latitud':'Latitud','longitud':'Longitud','ph':'Propiedad Horizontal','chip':'Chip','matricula':'Matricula Inmobiliaria','cedula_catastral':'Cedula catastral','porteria':'Porteria','circuito_cerrado':'Circuito cerrado','lobby':'Lobby','salon_comunal':'Salon comunal','parque_infantil':'Parque infantil','terraza':'Terraza','sauna':'Sauna','turco':'Turco','jacuzzi':'Jacuzzi','cancha_multiple':'Cancha multiple','cancha_baloncesto':'Cancha de baloncesto','cancha_voleibol':'Cancha de voleibol','cancha_futbol':'Cancha de futbol','cancha_tenis':'Cancha de tenis','cancha_squash':'Cancha de squash','salon_juegos':'Salon de juegos','gimnasio':'GYM','zona_bbq':'Zona de BBQ','sala_cine':'Sala de cine','piscina':'Piscina'}
    datadownload.rename(columns=reanmeformat,inplace=True)

    #-------------------------------------------------------------------------#
    fontsize        = 13
    fontfamily      = 'sans-serif'
    backgroundcolor = '#FAFAFA'
    
    css_format = """
      <style>
        .property-card-left {
          width: 100%;
          height: 800px; /* or max-height: 300px; */
          overflow-y: scroll; /* enable vertical scrolling for the images */
        }
        .property-card-right {
          width: 100%;
          margin-left: 10px;
        }
    
        .text-justify {
          text-align: justify;
        }
        
        .no-margin {
          margin-bottom: 1px;
        }
        .margin-text-top {
          margin-top: 20px;
        }        
        .price-part1 {
          font-family: 'Comic Sans MS', cursive;
          font-size: 24px;
          margin-bottom: 1px;
        }
        
        .price-part2 {
          font-size: 14px;
          font-family: 'Comic Sans MS';
          margin-bottom: 1px;
        }
    
        .nota {
          font-size: 12px;
          margin-top: 20px;
        }
        .row {
          display: flex;
          flex-wrap: nowrap;
        }
        .col-25 {
          flex: 1;
          text-align: justify;
          font-size: 12px;
        }
        
        i.fas {
          font-size: 12px;
        }
        .property-status-red {
          text-align: center;
          width:40%;
          padding: 8px;
          background-color: #FFCDD2;
          color: #B71C1C;
          margin-bottom: 10px;
        }    
        .property-status-green {
          text-align: center;
          width:40%;
          padding: 8px;
          background-color: #C8E6C9;
          color: #1B5E20;
          margin-bottom: 10px;
        }    
        img{
            width:47%;
            height:320px;
            margin-bottom: 10px; 
        }
      </style>
    """
    
    col1, col2 = st.columns([3,2])
    with col1:
        imagenes    = '<div class="property-card-images">\n'
        variables   = [x for x in list(data) if 'url_img' in x]
        conteo      = 0
        maximgcount = 0
        for i in variables:
            maximgcount += 1
            if isinstance(data[i].iloc[0], str) and len(data[i].iloc[0])>=7:
                imagenes += f'''<img src="{data[i].iloc[0]}" alt="property image" onerror="this.src='https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/sin_imagen.png';">\n'''
                conteo += 1
            if conteo==2:
                imagenes += '</div>\n'
                imagenes += '<div class="property-card-images">\n'
                conteo   = 0
            if maximgcount>=24: 
                break
            
        imagenes = BeautifulSoup(imagenes, 'html.parser')
        
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
        
    with col2:
        
        #{"catname":"Precios","categoria":"precios","variable":"precio_lista_venta","varname":"Precio:","tipo":"float","keepif":"notempty"},
        #{"catname":"Precios","categoria":"precios","variable":"valoradministracion","varname":"Administración:","tipo":"float","keepif":"notempty"},
        #{"catname":"Información general","categoria":"general","variable":"areaconstruida","varname":"Área construida:","tipo":"float","keepif":"notempty"},
        #{"catname":"Información general","categoria":"general","variable":"habitaciones","varname":"Habitaciones:","tipo":"int","keepif":"notempty"},
        #{"catname":"Información general","categoria":"general","variable":"banos","varname":"Baños:","tipo":"int","keepif":"notempty"},
        #{"catname":"Información general","categoria":"general","variable":"garajes","varname":"Garajes:","tipo":"int","keepif":"notempty"},

        precio              = f'${data["precio_lista_venta"].iloc[0]:,.0f}' 
        tiponegocio         = "Venta"
        latitud             = data["latitud"].iloc[0] 
        longitud            = data["longitud"].iloc[0]
        caracteristicas = f'<strong>{data["areaconstruida"].iloc[0]}</strong> mt<sup>2</sup> | <strong>{data["habitaciones"].iloc[0]}</strong> habitaciones | <strong>{data["banos"].iloc[0]}</strong> baños | <strong>{data["garajes"].iloc[0]}</strong> garajes'
        try:    valoradministracion = f'<p>Administración: ${data["valoradministracion"].iloc[0]:,.0f}</p>'
        except: valoradministracion = ''
        try:    tipoinmueble = data['tipoinmueble'].iloc[0].title().strip()
        except: tipoinmueble = 'Apartamento'
        
        estado_inmueble = '''
                          <div>
                            <p class="property-status-green">Disponible</p>
                          </div>            
                        '''
        if 'estado_venta' in data and (data['estado_venta'].iloc[0].lower()=='vendido' or data['estado_venta'].iloc[0].lower()=='remodelando'):
            estado_inmueble = f'''
                                <div>
                                  <p class="property-status-red">{data['estado_venta'].iloc[0].title().strip()}</p>
                                </div>            
                              '''
        try:
            porcentaje_comision = data["porcentaje_comision"].iloc[0]
            if str(porcentaje_comision).split('.')[-1][0]=='0':
                porcentaje_comision = "{:.0%}".format(porcentaje_comision/100)
            else:
                porcentaje_comision = "{:.1%}".format(porcentaje_comision/100)
            porcentaje_comision = f'<p>Comisión: <strong>{porcentaje_comision}</strong></p>'
        except: porcentaje_comision = ''

        formato = [{"catname":"Información general","categoria":"general","variable":"ciudad","varname":"Ciudad:","tipo":"str","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"localidad","varname":"Localidad:","tipo":"str","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"barriocatastral","varname":"Barrio:","tipo":"str","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"nombre_conjunto","varname":"Edificio:","tipo":"str","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"direccion","varname":"Dirección:","tipo":"str","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"tipoinmueble","varname":"Tipo inmueble:","tipo":"str","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"estrato","varname":"Estrato:","tipo":"int","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"depositos","varname":"Depósitos:","tipo":"int","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"piso","varname":"Piso:","tipo":"int","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"antiguedad_min","varname":"Antigüedad:","tipo":"int","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"ascensores","varname":"Ascensores:","tipo":"int","keepif":"notempty"},
        {"catname":"Información general","categoria":"general","variable":"numerodeniveles","varname":"Niveles:","tipo":"int","keepif":"notempty"},
        {"catname":"Información catastral","categoria":"catastral","variable":"chip","varname":"Chip:","tipo":"str","keepif":"notempty"},
        {"catname":"Información catastral","categoria":"catastral","variable":"matricula","varname":"Matricula inmobiliaria:","tipo":"str","keepif":"notempty"},
        {"catname":"Información catastral","categoria":"catastral","variable":"cedula_catastral","varname":"Cédula catastral:","tipo":"str","keepif":"notempty"},
        {"catname":"Información catastral","categoria":"catastral","variable":"conjunto_unidades","varname":"# Unidades en el conjunto:","tipo":"int","keepif":"notempty"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"ph","varname":"Propiedad horizontal:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"porteria","varname":"Portería:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"circuito_cerrado","varname":"Circuito cerrado:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"lobby","varname":"Lobby:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"salon_comunal","varname":"Salón comunal:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"parque_infantil","varname":"Parque infantil:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"terraza","varname":"Terraza:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"sauna","varname":"Sauna:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"turco","varname":"Turco:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"jacuzzi","varname":"Jacuzzi:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"cancha_multiple","varname":"Cancha múltiple:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"cancha_baloncesto","varname":"Cancha baloncesto:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"cancha_voleibol","varname":"Cancha de voleibol:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"cancha_futbol","varname":"Cancha de futbol:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"cancha_tenis","varname":"Cancha de tenis:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"cancha_squash","varname":"Cancha de squash:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"salon_juegos","varname":"Salón de juegos:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"gimnasio","varname":"GYM:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"zona_bbq","varname":"Zona de BBQ:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"sala_cine","varname":"Sala de cine:","tipo":"str","keepif":"si"},
        {"catname":"Amenities del edificio","categoria":"amenities","variable":"piscina","varname":"Piscina:","tipo":"str","keepif":"si"}]        
    
        formato     = pd.DataFrame(formato)
        tablavector = []
        tablaname   = []
        for j in formato['categoria'].unique():
            df    = formato[formato['categoria']==j]
            tabla = ""
            for i,items in df.iterrows():
                variable = items['variable']
                if variable in data and data[variable].iloc[0] is not None:
                    tipovariable = items['tipo']
                    if 'str' in tipovariable:
                        if isinstance(data[variable].iloc[0], str):
                            tabla += f'''
                              <tr style="border-style: none;">
                                <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">{items['varname']}</td>
                                <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">{data[variable].iloc[0]}</td>
                              </tr>
                            '''                            
                    elif 'int' in tipovariable:
                        try:
                            int(data[variable].iloc[0])
                            tabla += f'''
                              <tr style="border-style: none;">
                                <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">{items['varname']}</td>
                                <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">{data[variable].iloc[0]}</td>
                              </tr>
                            '''    
                        except: pass

                    elif 'float' in tipovariable:
                        try:
                            float(data[variable].iloc[0])
                            tabla += f'''
                              <tr style="border-style: none;">
                                <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">{items['varname']}</td>
                                <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">{data[variable].iloc[0]}</td>
                              </tr>
                            '''  
                        except: pass
                    
            if tabla!="":
                tabla = f'''
                <ul>
                    <table style="width:100%;">
                    {tabla}
                    </table>
                </ul>\n
                '''
                tablavector.append(tabla)
                tablaname.append(j)
        
        tablamerge = ''
        for i in range(len(tablaname)):
            if tablaname[i]!="amenities":
                catname = formato[formato['categoria']==tablaname[i]]['catname'].iloc[0]
                tablamerge += f'''
                                <p><strong>{catname}:</strong></p>
                                    {tablavector[i]}\n
                            '''
            
        tablamerge = BeautifulSoup(tablamerge, 'html.parser')
        
        texto_property = f"""
        <!DOCTYPE html>
        <html>
        <head>
        {css_format}
        </head>
        <body>
        <div class="property-card-right">
                {estado_inmueble}
                <p class="no-margin">
                  <span class="price-part1">{precio}</span> 
                  <span class="price-part2">({tiponegocio})</span>
                </p>
                {valoradministracion}
                {porcentaje_comision}
                <p>{caracteristicas}</p>
                <p>Código: <strong>{id_inmueble}</strong></p>
                {tablamerge}                
        </div>
        </body>
        </html>
        """
        texto_property = BeautifulSoup(texto_property, 'html.parser')
        st.markdown(texto_property, unsafe_allow_html=True)
        
        csv = convert_df(datadownload)

        st.download_button(
           "Descargar info completa",
           csv,
           "info_completa.csv",
           "text/csv",
           key='descarga-csv'
        )

    st.write('---')
    col1, col2 = st.columns([3,2])
    with col1:
        map = folium.Map(location=[latitud, longitud],zoom_start=17,tiles="cartodbpositron")
        folium.Marker(location=[latitud, longitud]).add_to(map)
        st_map = st_folium(map, width=600, height=350)
        
    with col2:
        tabla_contacto = ""
        for j in datos_contacto:
            key   = j['nombre']
            value = j['tel']
            tabla_contacto += f'''
              <tr style="border-style: none;">
                <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">{key}</td>
                <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">{value}</td>
              </tr>
            '''
        for i in ['url_domus','url_fr','url_m2','url_cc','url_meli']:
            if isinstance(data[i].iloc[0], str) and len(data[i].iloc[0])>20: 
                link = f'''[Link]({data[i].iloc[0]})'''
                tabla_contacto += f'''
                  <tr style="border-style: none;">
                    <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">Ver inmueble</td>
                    <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">
                        <a href="{data[i].iloc[0]}">Link</a>
                    </td>
                  </tr>
                '''
                break
        try:
            lista_documents = pd.DataFrame(json.loads(data['venta_relevantfiles'].iloc[0]))
            idd = lista_documents['filename'].apply(lambda x: 'ctl' in x.lower() and '.pdf' in x.lower())
            if sum(idd)>0:
                lista_documents = lista_documents[idd]
                lista_documents['filedate'] = pd.to_datetime(lista_documents['filedate'],errors='coerce')
                lista_documents = lista_documents.sort_values(by='filedate',ascending=False)
                url_document    = lista_documents['urldocument'].iloc[0]
                link = f'''[Link]({url_document})'''
                tabla_contacto += f'''
                  <tr style="border-style: none;">
                    <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">CTL</td>
                    <td style="border-style: none;font-family:{fontfamily};font-size:{fontsize}px;">
                        <a href="{url_document}">Link</a>
                    </td>
                  </tr>
                '''
        except: pass
        
        # Tabla de amenities
        df     = formato[formato['categoria']=='amenities']
        conteo = 0
        tabla  = ''
        tabla_amenities = ''
        for i,items in df.iterrows():
            variable = items['variable']
            varname  = items['varname'].split(':')[0].strip()
            if variable in data and data[variable].iloc[0] is not None:
                tipovariable = items['tipo']
                keepif       = items['keepif']
                if 'str' in tipovariable:
                    if isinstance(data[variable].iloc[0], str) and data[variable].iloc[0].lower()==keepif.lower():
                        tabla += f'''
                          <div class="col-25">{varname}</div>
                          <div class="col-25"><i class="fas fa-check"></i></div>\n
                        '''
                        conteo += 1
                if 'int' in tipovariable:
                    try:
                        int(data[variable].iloc[0])
                        tabla += f'''
                          <div class="col-25">{varname}</div>
                          <div class="col-25">{data[variable].iloc[0]}</div>\n
                        '''
                        conteo += 1
                    except: pass
            if conteo>0 and conteo % 2 == 0:
                tabla_amenities += f'''
                <div class="row">
                {tabla}
                </div>
                '''
                tabla = ''
                
        if conteo % 2 == 1 and tabla!='':
            tabla_amenities += f'''
            <div class="row">
            {tabla}
            <div class="col-25"></div>
            <div class="col-25"></div>\n
            </div>
            '''    
    
        tabla_contacto = f'''

        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.14.0/css/all.css" integrity="sha384-HzLeBuhoNPvSl5KYnjx0BT+WB0QEEqLprO+NBkkk5gbc67FTaL7XIGa2w1L0Xbgc" crossorigin="anonymous">
        <p><strong>Amenities del edificio</strong></p>
        {tabla_amenities}
        <p  class="margin-text-top"><strong>Datos de contacto de esta propiedad</strong></p>
        <table style="width:100%;">
        {tabla_contacto}
        </table>
        '''
        tabla_contacto = BeautifulSoup(tabla_contacto, 'html.parser')
        st.markdown(tabla_contacto, unsafe_allow_html=True)

        nota = f"""
        <!DOCTYPE html>
        <html>
        <head>
        {css_format}
        </head>
        <body>
            <p class="nota"> <strong>Nota</strong>: La información de contacto de la propiedad <strong>NO</strong> sale en la ficha que se descarga en pdf</p>
        </body>
        </html>
        """
        nota = BeautifulSoup(nota, 'html.parser')
        st.markdown(nota, unsafe_allow_html=True)
    
        #---------------------------------------------------------------------#
        if st.button('Generar PDF'):
            with st.spinner("Generando PDF"):
                css_format_export = """
                        <style>
                          .property-card {
                            display: flex;
                          }
                          .property-card-left {
                            width: 60%;
                            float: left;
                          }
                          .property-card-right {
                            width: 40%;
                            float: right;
                            margin-left: 20px;
                          }
                          .price-part1 {
                            font-family: 'Comic Sans MS', cursive;
                            font-size: 24px;
                            margin-bottom: 1px;
                          }
                          
                          .price-part2 {
                            font-size: 14px;
                            font-family: 'Comic Sans MS';
                            margin-bottom: 1px;
                          }
                          .text-justify {
                            text-align: justify;
                          }
                          .no-margin {
                            margin-bottom: 1px;
                          }
                          .property-map {
                              width: 400px;
                              height: 200px;
                          }
                          .row {
                            display: flex;
                            flex-wrap: nowrap;
                          }
                          .col-25 {
                            flex: 1;
                            text-align: justify;
                            font-size: 12px;
                          }
                          i.fas {
                            font-size: 12px;
                          }
                          img{
                              width:45%;
                              height:180px;
                              margin-bottom: 10px; 
                          }
                        </style>
                """
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="UTF-8">
                    {css_format_export}
                </head>
                <body>
                    <main>
                      <div class="property-card">
                        <div class="property-card-left">
                             {imagenes}
                        </div>
                      <div class="property-card-right">
                        <p class="no-margin">
                          <span class="price-part1">{precio}</span> 
                          <span class="price-part2">  ({tiponegocio})</span>
                        </p>
                        {valoradministracion}
                        <p>{caracteristicas}</p>
                        <p>Código: <strong>{id_inmueble}</strong></p>
                        {tablamerge}
                        <img src="https://maps.googleapis.com/maps/api/staticmap?center={latitud},{longitud}&zoom=16&size=400x200&markers=color:blue|{latitud},{longitud}&key={API_KEY}" alt="Google Map" class="property-map">
                        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.14.0/css/all.css" integrity="sha384-HzLeBuhoNPvSl5KYnjx0BT+WB0QEEqLprO+NBkkk5gbc67FTaL7XIGa2w1L0Xbgc" crossorigin="anonymous">
                        <p><strong>Amenities del edificio</strong></p>
                        {tabla_amenities}
                      </div>
                    </main>
                </body>
                </html>
                """
    
                caracteres_especiales = {
                    "á": "&aacute;",
                    "é": "&eacute;",
                    "í": "&iacute;",
                    "ó": "&oacute;",
                    "ú": "&uacute;",
                    "ñ": "&ntilde;",
                    "Á": "&Aacute;",
                    "É": "&Eacute;",
                    "Í": "&Iacute;",
                    "Ó": "&Oacute;",
                    "Ú": "&Uacute;",
                    "Ñ": "&Ntilde;",
                }
                for caracter, codigo in caracteres_especiales.items():
                    html = re.sub(caracter, codigo, html)

                html              = BeautifulSoup(html, 'html.parser')
                fd, temp_path     = tempfile.mkstemp(suffix=".html")
                wd, pdf_temp_path = tempfile.mkstemp(suffix=".pdf")       
                
                client = pdfcrowd.HtmlToPdfClient(pdfcrowduser,pdfcrowdpass)
                client.convertStringToFile(html, pdf_temp_path)

                with open(pdf_temp_path, "rb") as pdf_file:
                    PDFbyte = pdf_file.read()
                
                st.download_button(label="Descargar Ficha",
                                    data=PDFbyte,
                                    file_name=f"ficha-codigo-{idcodigo}.pdf",
                                    mime='application/octet-stream')
else: 
    st.error("Codigo del inmueble no encontrado")