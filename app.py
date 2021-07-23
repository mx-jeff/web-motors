import json
import requests
from utils.webdriver_handler import scroll
from utils.setup import setSelenium
from utils.parser_handler import init_parser, remove_duplicates, init_crawler
from utils.file_handler import dataToExcel, load_links, remove_duplicates_txt, save_to_json
from time import sleep
import requests

from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException


def verbose(text):
    verbose = True
    if verbose:
        print(text)


def getCarsByLink():
    def make_requests(actualPage):
        limit = 24
        req = requests.get(f'https://www.webmotors.com.br/api/search/car?url=https://www.webmotors.com.br/carros%2Festoque%3F&actualPage={actualPage}&displayPerPage={limit}&order=1&showMenu=true&showCount=true&showBreadCrumb=true&testAB=false&returnUrl=false')

        return req


    def extract_link(data):
        cars_link = []
        for car in data["SearchResults"]:
            id = car["UniqueId"]
            make = car["Specification"]['Make']['Value']
            version = car["Specification"]["Version"]["Value"]
            model = car["Specification"]["Model"]["Value"]
            ports = f"{car['Specification']['NumberPorts']}-portas"
            year = car["Specification"]["YearFabrication"]

            link = f"https://www.webmotors.com.br/comprar/{make}/{model}/{version}/{ports}/{year}/{id}"
            cars_link.append(link)
        
        # print(f"{len(cars_link)} Extraídos", end="\r")
        return cars_link

    # save_to_json(req.json(),'cars')
    # with open('cars.json', encoding="utf-8") as file:
    #     data = json.load(file)
    
    i = 1
    while True:
        try:
            req = make_requests(i)
        
        except Exception as error:
            print(f'> {error}')
            break

        data = req.json()
        links = extract_link(data)
        with open('links.txt','a') as file:
            for link in links:
                file.write(f'{link}\n')

        print(f'{i} páginas extraídas!', end="\r")

        i += 1

        if not "SearchResults" in data or len(data["SearchResults"]) == 0:
            break

    remove_duplicates_txt()


def getDetails(url):
    try:
        driver = setSelenium(False)
        driver.get(url)
        verbose('> Esperando página carregar...')
        driver.implicitly_wait(10)
        
        button_exists = True
        try:
            # click no botão para mostrar telefone
            verbose('> 1 Click no botão do telefone')
            driver.find_element_by_id('CardSellerPhoneViewPrivate').click()
        
        except ElementClickInterceptedException:
            verbose('> tentando remover popup se existe...')
            remove_popups(driver)
            driver.find_element_by_id('CardSellerPhoneViewPrivate').click()
            
        except NoSuchElementException:
            verbose('> Informações não achadas! continuando...')
            button_exists = False
            pass

        finally:
            sleep(5)

        if button_exists:
            time = 0
            while True :
                verbose('> verificando se o botão esta carregando...')
                if time >= 10:
                    print('> Erro de rede ou não existe!')
                    break

                try:
                    driver.find_element_by_id('VehicleSellerPrivatePhone_0')
                
                except NoSuchElementException:
                    sleep(5)
                    time += 1

                else:
                    verbose('> Telefone achado...')
                    break


        verbose('> Raspando dados...')
        soap = parse_results(driver)
        driver.quit()

        data = {}
        data['Nome'] = soap.find('h2', id="VehicleSellerPrivateName").text
        try:
            data['Telefone'] = soap.find('strong', id="VehicleSellerPrivatePhone_0").text

        except AttributeError:
            data['Telefone'] = 'Não existete'

        data['Estado'] = soap.find('span', id="VehicleSellerPrivateState").text
        data['Tipo de pessoa'] = soap.find('p', id="VehicleSellerPrivateTypeAd").text

        print('\n')
        for key, value in data.items():
            print(f'> {key}: {value}')
        print('\n')

        dataToExcel({ 'Nome': [data['Nome']], 'Telefone': [data['Telefone']], 'Estado': [data['Estado']], 'Tipo de pessoa': [data['Tipo de pessoa']] }, 'web-motors.csv')

    except KeyboardInterrupt:
        verbose('> Saindo volte sempre...')
        driver.quit()

    except Exception:
        driver.quit()
        raise


def getCars(driver):
    driver.get("https://www.webmotors.com.br/carros-usados/estoque?tipoveiculo=carros-usados&precoate=500000&precode=100000&anunciante=Pessoa%20F%C3%ADsica")
        
    verbose('> Selecionando carros...')
    driver.implicitly_wait(10)
    scroll(driver)
    driver.implicitly_wait(20)

    soap = parse_results(driver)
    driver.quit()
    container = soap.find('div', class_="ContainerCardVehicle")

    raw_links = [link['href'] for link in container.find_all('a')]
    links = remove_duplicates(raw_links)

    verbose(f"> {len(links)} Carros encontrados!")
    
    for index, link in enumerate(links):
        verbose(f": Extraindo {index + 1} carro...")
        getDetails(link)


def parse_results(driver):
    html = driver.find_element_by_tag_name('html')
    src_code = html.get_attribute('outerHTML')
    return init_parser(src_code)


def remove_popups(driver):
    driver.find_element_by_css_selector('.modal--close').click()
    sleep(3)
    driver.find_element_by_css_selector('.sc-htoDjs.gtMZoW').click()


def main():
    '''
    Insert your code here
    '''
    print('~' *40)
    print(str('Web Motors crawler').center(40))
    print('~' *40)

    getCarsByLink()
    links = load_links('links_sanlitized')
    
    print(f"{len(links)} links encontrados!")
    for index, link in enumerate(links):
        print(f'Extraíndo {index} de {len(links)}')
        getDetails(link)


if __name__ == "__main__":
    main()