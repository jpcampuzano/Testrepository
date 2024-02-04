## Dashboard creado por Juan Pablo Cmapuznao para AFi escuela

#########Preprocesamiento de datos################

import pandas as pd

## Cargamos el fichero Fruto del scrapping

file_path = 'extracted_datafinal.jsonl'

#### Funciones utiles
def preprocess_price(df):
    price_map = {
        "€": "Bajo",
        "€€ - €€€": "Medio",
        "€€€€": "Alto"
    }
    df['Price'] = df['Price'].map(price_map)
    return df

# Definimos las ciudades que analizaremos

city_list = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza", "Málaga", "Murcia", "Palma de Mallorca", "Las Palmas de Gran Canaria", "Bilbao", "Alicante", "Córdoba", "Valladolid", "Vigo", "Gijón", "L'Hospitalet de Llobregat", "Vitoria-Gasteiz", "La Coruña", "Granada", "Elche"]

# Leemos el archivo de json lines
restaurants = pd.read_json(file_path, lines=True)

## Eliminamos los duplicados de los restaurantes, esto sucede por mla insercion promocional de un restaurante varias veces en una misma pagina
restaurants_unique = restaurants.drop_duplicates(subset='Name', keep='first')

# Limpiamos la columna de numero de reseñas
Number_reviews_clean =[int((r.split(' '))[0].replace('.','')) for r in list(restaurants_unique['Reviews_N'])]


restaurants_unique.loc[:,'Reviews_N']=Number_reviews_clean

restaurants_unique = restaurants_unique.drop(restaurants_unique[restaurants_unique['Reviews_N'] < 30].index).reindex()
# Limpiamos la columna del score
restaurants_unique['Score'] = restaurants_unique['Score'].str.replace(',', '.').astype(float)

# Aplicamos el parseo del precio y usamos df para acortar las expresiones en la fase de visualización
df = preprocess_price(restaurants_unique)


##### Visualizacón de datos en streamlit ######

## A continuacón s epresneta la estructura del dashboard de streamlit.
## las funciones para realizar los graficos estan en el archivo plots_dinamic.py

import streamlit as st
import pandas as pd
from plots_dinamic import plot_histogram_category
from plots_dinamic import plot_histogram_price
from plots_dinamic import plot_map
from plots_dinamic import plot_categories_by_city
from plots_dinamic import plot_restaurants_by_price_city

st.set_page_config(layout="wide") # Configuramos como wide para tener más area a disposición

st.title('Explorador de datos the TripAdvisor')

st.sidebar.image("Tripadvisor.png", use_column_width=True) # Creamos un sidebar para navegar por el dashboard

page = st.sidebar.radio(
    "Menú",
    ("Bienvenida", "Datos", "Análisis exploratorio", "Mapa"),
)

if page == "Bienvenida":  ## Creamos la pagina de bienvenida, y usamos markdown para formatear el texto
    st.header("Bienvenido al Explorador de datos de restaurantes De Tripadvisor👋")
    st.subheader('Creado por Juan Pablo Campuzano para AFI Escuela ')
    st.markdown(
    """
    En este Dashboard podrás encontrar la información obtenida de 'scraprear' 
    la sección de restaurantes de [Tripadvisor España](https://www.tripadvisor.es/Restaurants)
    
    **👈 Para continuar selecciona una de las paginas en el menú a tu izquierda** 
    ### En ellas podras encontrar:
    - **Datos:**  Breve explicación del contenido de los datos
    - **Análisis exploratorio:**  Visualizaciónes con precios, tipos de comida y puntuaciones 
    - **Mapa:**  Ubicación geografica de los restaurantes analizados
    """)
    
if page == "Datos":
    st.header("Set de Datos:")
    st.markdown(
    """
    ### El siguente dataframe esta conformado por la siguiente estructura:
    
    - **Name:**  Nombre del Restaurante
    - **Reviews_N:**  Numero de reseñas 
    - **Rank:**  Rango en su ciudad
    - **Price:**  Precio
    - **Categories:**  Tipos de cocina ofertada
    - **Adress:**  Dirección del restaurante
    - **Score:**  Puntuación del restaurante
    - **Latitude:**  Latitud de la ubicación
    - **Longitude:**  longitud de la 
    - **City:**  Ciudad donde esta ubicado
    
    Las ciudades analizadas fueron las 20 más pobladas: 
        Madrid, Barcelona, Valencia, Sevilla, Zaragoza, Málaga
        Murcia, Palma de Mallorca, Las Palmas de Gran Canaria, Bilbao,
        Alicante, Córdoba, Valladolid, Vigo, Gijón, L'Hospitalet de Llobregat,
        Vitoria-Gasteiz, La Coruña , Granada, Elche
        
    El dataset está compuesto por los 30 restaurantes mejor puntuados de cada ciudad    
    """)
    
    options_city1 = st.multiselect( ## Creamos los filtros
    'Acá Puedes filtrar por ciudad',
    city_list,
    ["Madrid", "Barcelona", "Valencia",])
    
    options_price1 = st.multiselect(
    'Acá Puedes filtrar por Precio',
    ["Bajo", "Medio", "Alto",],
    ["Bajo", "Medio", "Alto",])
    


    st.dataframe(df[df["city"].isin(options_city1) & # aplicamos los filtros
                    df["Price"].isin(options_price1)],
                 column_config ={"Score": st.column_config.NumberColumn(
        "Score",
        help="Number of stars on GitHub",
        format="%d ⭐",
        )})

    
if page == "Análisis exploratorio":
    st.header("Análisis exploratorio")
    st.markdown(
    """
    ## ¿Qué tipos de comida se ofrecen con mayor frecuencia en los restaurantes de las diferentes ciudades (acumulado)?
    """)
    with st.expander("Abrir para visualizar"): ## Para dividir una misma página en varias secciones, usamos las secciones explandibles
        
        col1, col2 = st.columns([1, 3]) # dividimos por columnas para dar orden a la página
        options_city2 = col1.multiselect(
        'Acá Puedes filtrar por ciudad',
        city_list,
        ["Madrid", "Barcelona", "Valencia",])
        
        categories_expanded = df.explode('categories') ## Usamos explode para obrtener un registro por cada categoria
        
        
        options_categories2 = col2.multiselect(
        'Acá Puedes filtrar por tipo de cocina',
        set(categories_expanded['categories'].tolist()),
        (['Japonesa', 'Americana', 'Mediterránea']))
        
        filtered_df = categories_expanded[categories_expanded['categories'].isin(options_categories2) &
                                          categories_expanded["city"].isin(options_city2)]
    
        fig = plot_histogram_category(filtered_df) ## Lllamamos a la función para graficar
        col2.pyplot(fig)
        st.write('Insight: La comida más popular de los mejores restaurantes de todas las ciudades es la mediterranea, seguida por la española.')
        st.write('Insight: En las ciudades más grandes el numero de restaurantes que ofrecen sabores de otros continentes es mucho mayor que en las ciudades pequeñas siendo los sabores extranjeros más populares el Americano y Japones ')        
        
        
    st.markdown(  
    """
    ## ¿Qué tipos de comida se ofrecen con mayor frecuencia en los restaurantes agrupando por ciudades?
    """)
    with st.expander("Abrir para visualizar"):
        
        colA, colB = st.columns([1, 3])
        
        options_city2 = colA.multiselect(
        'Acá Puedes filtrar por ciudad',
        city_list,
        ["Madrid", "Barcelona", "Valencia",], key = "<AC>",)
        
        categories_expanded = df.explode('categories')
        categories_expanded = categories_expanded[['categories', 'city']]
        
        
        
        options_categories2 = colB.multiselect(
        'Acá Puedes filtrar por tipo de cocina',
        set(categories_expanded['categories'].tolist()),
        (['Japonesa', 'Americana', 'Mediterránea']), key = "<AN>",)
        
        filtered_df = categories_expanded[categories_expanded['categories'].isin(options_categories2) &
                                          categories_expanded["city"].isin(options_city2)]
    
        fig = plot_categories_by_city(filtered_df)
        colB.pyplot(fig)
        st.write('Insight: Las ciudades Costeras ofrecen menos opciones de comidas, destacando la mediterranea y marisquerias, con poca prevalencia de cocinas popúlares como la americana ')
        
        
    st.markdown(
    """
    ## ¿Cuales son los precios de los restaurantes mejor valorados de las diferentes ciudades (acumulado)?
    """)
    with st.expander("Abrir para visualizar"):
        
        col3, col4 = st.columns([1, 3])
        options_city3 = col3.multiselect(
        'Acá Puedes filtrar por ciudad',
        city_list,
        ["Madrid", "Barcelona", "Valencia",], key = "<AA>",)
        
        options_price3 = col3.multiselect(
        'Acá Puedes filtrar por precio',
        set(df['Price'].tolist()),
         set(df['Price'].tolist()))
        
        filtered_df = df[df["city"].isin(options_city3) &
                         df["Price"].isin(options_price3)]
    
        fig = plot_histogram_price(filtered_df)
        col4.pyplot(fig)
        st.write('Insight: La gran mayoria de los mejores restaurantes ofrecen sus productos precio medio, es decir, no hay que gastar mucho para comer bien ')
        
        
    st.markdown(
    """
    ## ¿Cuales son los precios de los restaurantes mejor valorados agrupados por ciudad?
    """)
    with st.expander("Abrir para visualizar"):
        
        colN, colM = st.columns([1, 3])
        options_city3 = colN.multiselect(
        'Acá Puedes filtrar por ciudad',
        city_list,
        ["Madrid", "Barcelona", "Valencia",], key = "<BB>",)
        
        options_price3 = colM.multiselect(
        'Acá Puedes filtrar por precio',
        set(df['Price'].tolist()),
         set(df['Price'].tolist()), key = "<AF>",)
        
        filtered_df = df[df["city"].isin(options_city3) &
                         df["Price"].isin(options_price3)]
    
        fig = plot_restaurants_by_price_city(filtered_df)
        colM.pyplot(fig)        
        st.write('Insight: En las ciudades pequeñas el numero de restaurantes con precios altos es mayor que aquellos con precios bajos, en las ciudades grandes se encuentran por menos dinero mas opciones de calidad ')
        
        
 

elif page == "Mapa": #
    st.header("Mapa interactivo")
    st.markdown(
    """
    ## Acá puedes filrar los difirentes restaurantes en base a tus preferencias y encontrar su ubicación y dirección 
    
    Pasa el ratón por los restaurantes para desplegar la información
    """)
    col5, col6 = st.columns([1, 3])
    options_city4 = col6.multiselect(
    'Acá Puedes filtrar por ciudad',
    city_list,
    ["Madrid", "Barcelona", "Valencia",], key = "<AB>",)
    
    categories_expanded = df.explode('categories')
    category_counts = categories_expanded['categories'].value_counts()
    
    options_categories4 = col5.multiselect(
    'Acá Puedes filtrar por tipo de cocina',
    set(categories_expanded['categories'].tolist()),
    (['Japonesa', 'Americana', 'Mediterránea']))
    
    options_price4 = col5.multiselect(
    'Acá Puedes filtrar por precio',
    set(df['Price'].tolist()),
    set(df['Price'].tolist()))
    
    score_silder = col5.slider(
    "Selecciona las estrellas del Restaurante ⭐",
    value=(1, 5),min_value =1,max_value=5)
    
    
    
    
    
    filtered_df = df[df["city"].isin(options_city4) &
                     df["Price"].isin(options_price4) &
                     df['categories'].apply(lambda x: any(category in x for category in options_categories4)) & 
                     (df["Score"]>=score_silder[0]) & (df["Score"]<=score_silder[1])]
    
    fig = plot_map(filtered_df)
    col6.plotly_chart(fig)
    