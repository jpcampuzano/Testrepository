import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def plot_histogram_category(data):
    
    df = pd.DataFrame(data)

    
    categories_expanded = df.explode('categories')

   
    category_counts = categories_expanded['categories'].value_counts()

    # Plotting
    plt.figure(figsize=(10, 6))
    category_counts.plot(kind='bar')
    plt.title('Número de Restaurantes por Categoría')
    plt.xlabel('Categoría')
    plt.ylabel('Número de Restaurantes')
    plt.xticks(rotation=90)
    plt.tight_layout()

    return plt


def plot_categories_by_city(data):

    
    df = pd.DataFrame(data)

    
    categories_expanded = df.explode('categories')
    categories_expanded = categories_expanded[['categories', 'city']]
    
    category_city_counts = categories_expanded.groupby(['categories', 'city']).size().unstack(fill_value=0)


    cities = category_city_counts.columns
    colors = plt.cm.get_cmap('tab10', len(cities))

    
    category_city_counts.plot(kind='bar', figsize=(10, 6), color=[colors(i) for i in range(len(cities))])

    
    plt.title('Número de Restaurantes por Categoría y ciudad')
    plt.xlabel('Categoría')
    plt.ylabel('Número de Restaurantes')
    plt.xticks(rotation=90)
    plt.legend(title='Ciudad')
    plt.tight_layout()

    return plt



def plot_histogram_price(data):
    
    df = pd.DataFrame(data)

    df = data
 
    price_counts = df['Price'].value_counts()

    plt.figure(figsize=(10, 6))
    price_counts.plot(kind='bar')
    plt.title('Número de Restaurantes por rango de precio')
    plt.xlabel('Precio')
    plt.ylabel('Número de Restaurantes')
    plt.xticks(rotation=90)
    plt.tight_layout()

    return plt

def plot_restaurants_by_price_city(data):
   
    
    df = pd.DataFrame(data)

    
    price_city_counts = df.groupby(['Price', 'city']).size().unstack(fill_value=0)

    
    cities = price_city_counts.columns
    colors = plt.cm.get_cmap('tab10', len(cities))

    # Plotting
    price_city_counts.plot(kind='bar', figsize=(10, 6), color=[colors(i) for i in range(len(cities))])
    plt.title('Número de Restaurantes por rango de precio')
    plt.xlabel('Precii')
    plt.ylabel('Número de Restaurantes')
    plt.xticks(rotation=45)
    plt.legend(title='City')
    plt.tight_layout()

    return plt


def plot_map(data):

    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(data)
    
    # Create the map using Plotly Express
    fig = px.scatter_mapbox(df, 
                            lat="Latitude", 
                            lon="Longitude", 
                            hover_name="Name", 
                            hover_data=["Address","Price","Score"],
                            color_discrete_sequence=["red"], 
                            zoom=4, 
                            height=500, width=770)
    
    # Set the mapbox style to "open-street-map", which does not require a Mapbox token
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(mapbox_center={"lat": 40.416775, "lon": -3.703790})
    
    # Remove the margin to make the map fit better in the output cell or window
    fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
    
    return fig