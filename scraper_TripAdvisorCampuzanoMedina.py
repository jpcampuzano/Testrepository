## Script de scrapping de Tripadvisor, creado por Juan Pablo Campuzano, Para AFI escuela, sin propositos comerciales
import re
import time
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.chrome.options import Options




############## Funciones útiles#############

def send_keys_character_by_character(element, text):
    ## utilizamos esta función para introducir las ciudades letra por letra, ya que si las introducimos de modo continuo no funciona siempre
    for char in text:
        element.send_keys(char)

chrome_options = Options()

num_pages_to_download = 1 ## Numero de paginas por ciudad, cada pagina contiene 30 restaurantes

# Lista de ciudades a scrapear
spain_cities = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza", "Málaga", "Murcia", "Palma de Mallorca", "Las Palmas de Gran Canaria", "Bilbao", "Alicante", "Córdoba", "Valladolid", "Vigo", "Gijón", "L'Hospitalet de Llobregat", "Vitoria-Gasteiz", "La Coruña (A Coruña)", "Granada", "Elche"]


for current_city in spain_cities: ## Loop principar para iterar entre ciudades
    
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options) # inizializar el driver de selenium
    
    start_url = 'https://www.tripadvisor.es/Restaurants/'
    
    
    browser.get(start_url)
    

    try: ## Si está presente el botón de cookies, lo encontramos y lo aceptamos
        cookies_button = (WebDriverWait(browser, 20)
                          .until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler'))))
        cookies_button.click()
    except Exception as e:
        print("Error:", str(e))
   
    
    
    search_text = (browser ## Buscamos la barra de busqueda
                   .find_element(By.CSS_SELECTOR, 'input[placeholder=\'Ciudad o nombre del restaurante\']'))
    
    search_text.click()
    search_text.clear() ## borramos el texto presente
    browser.implicitly_wait(10)
    
    
    send_keys_character_by_character(search_text,current_city) ## Enviamos la ciudad letra por letra
    time.sleep(5) # Esperamos 5 segundos para darle tiempo al driver de cargar las sugerencias
    
    ## Seleccionamos la primera sugerencia de ciudad
    first_selector = "a.GzJDZ.w.z._S._F.Wc.Wh.Q.B-._G[tabindex='-1']"  
    first_option_button = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, first_selector)))
    first_option_button.click()
    
    browser.refresh()
    
    for page in range(num_pages_to_download): ## loop de las páginas a cargar de cada ciudad
        print(page)
        
        # Definimos el área del HTML donde estan ubicados los articulos con los restaurantes
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Ikpld.f.e')))
        
        # Usamos beatifulSoup para extraer los elementos presentes y poder iterar posteriormente sobre ellos
        articles = browser.find_element(By.CSS_SELECTOR, 'div.Ikpld.f.e')
        articles = articles.get_attribute('outerHTML')
        articles = BeautifulSoup(articles, 'html.parser')
            
        # Loop para abrir cada uno de los articulos de los restaurantes
        for article in articles.find_all('div', {'class': 'vIjFZ Gi o VOEhq'}):
            href_value = article.select('div.biGQs a.BMQDV')[0].attrs['href']
            new_url = 'https://www.tripadvisor.es'+ href_value ## Concatenamos el url del restaurante
    
            
            
            # Abrimos una nueva pestaña
            browser.execute_script("window.open('', '_blank');")
            
            # Cambiamos a la nueva pestaña
            browser.switch_to.window(browser.window_handles[1])
            
            # indroducimos el URL del resturante
            browser.get(new_url)
            
            
            data = {} ##Inizializamos el diccionario donde se guardarán los datos
            
            try: ## Ponemos todas las extracciones de información dentro de un Try ya que en algunos restaurantes no estan presentes algunos
                ##  de los selectores, por ejemplo en los anuncios sin reseñas, o restaurantes donde no se declara el precio
                
                ## Extraemos el nombre del restaurante
                name = browser.find_element(By.CSS_SELECTOR,'h1[data-test-target="top-info-header"]')
                print(name.text.strip())
                data["Name"] = name.text.strip()
                
                
                span_element = browser.find_element(By.CLASS_NAME,"DsyBj")
            
                ## Extraemos el numero de reseñas
                reviews_link = browser.find_element(By.CSS_SELECTOR, 'a[href="#REVIEWS"]')
                data["Reviews_N"] = reviews_link.text
                
                ## Extraemos la clsificación dentro de la ciudad
                rank_link = browser.find_element(By.CSS_SELECTOR, 'a.AYHFM')
                data["Rank"] = rank_link.text
                
                ## Extraemos la lista donde se encuentra la información de precion y los tipos de cocina ofertados
                categories = browser.find_elements(By.CSS_SELECTOR, 'span.DsyBj.DxyfE a.dlMOJ')
                additional_info = [category.text for category in categories]
                
                data["Price"]= additional_info[0]
                data["categories"]= additional_info[1:-1]
                
                ## Extraemos la dirección del restaurante
                address_links = browser.find_elements(By.CSS_SELECTOR, 'a.AYHFM[href="#MAPVIEW"]')
                data["Address"] = address_links[0].text.strip()
                
                ## Extraemos la puntuación total
                score = browser.find_element(By.CLASS_NAME, "ZDEqb")
                data["Score"] = score.text
                
                ## Buscamos el mapa de google maps que contiene la información de las coordenadas
                image_element = browser.find_element(By.CSS_SELECTOR, "img.w.MD._S")
                image_src = image_element.get_attribute("src")
                
                ## extraemos las coordenadas buscando en el source del mapa
                coords = re.findall(r'center=([0-9.-]+),([0-9.-]+)', image_src)
                if coords:
                    lat, lon = coords[0]
                    data["Latitude"] = lat
                    data["Longitude"] = lon
                else:
                    data["Coordinates"] = "Coordinates not found in the image URL"
                ## Guardamos la ciudad actual
                data['city'] = current_city
            
                # Guardamos los datos en un jsonline, hacemos el append
                with open("extracted_data.jsonl", "a", encoding="utf-8") as jsonl_file:
                    json.dump(data, jsonl_file, ensure_ascii=False)
                    jsonl_file.write('\n')
                    
                    
            except Exception as e: ## En caso de levantar alguna excepción no se guardan los datos: sucede con los restaurantes promocionados sin reseñas
                print("Error:", str(e))
            # Cerramos la pestaña del restaurante
            browser.close()
            
            # Volvemos a la pestaña con la lista de restaurantes
            browser.switch_to.window(browser.window_handles[0])
        
        ## Buscamos la flecha para pasar de pagina 
        element = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-smoke-attr='pagination-next-arrow']")))

        try: # Debemos usar las acciones de selenium para hacer click en el botón
            actions = ActionChains(browser)
            actions.move_to_element(element).perform()

            element.click()
        except ElementClickInterceptedException:
            
            browser.execute_script("arguments[0].click();", element)
            
        browser.refresh()   # los refresh se usan a lo largo del script para liberar ram, ya que por alún motivo selenium usa mucha memoria
            
    browser.close()
                    
browser.quit()# Cerramos el driver
        
        

