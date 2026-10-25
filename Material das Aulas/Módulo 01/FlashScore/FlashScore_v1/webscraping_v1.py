import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from time import sleep
from datetime import date, datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from tqdm.auto import tqdm
from tinydb import TinyDB,Query
from math import nan
from scipy.stats import poisson
from bs4 import BeautifulSoup

def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

def Dados_Jogo(id_jogo,dictionary,driver):
    driver.get(f'https://www.flashscore.com/match/{id_jogo}/#/match-summary/match-summary')
    dictionary['Id'] = id_jogo
    country = driver.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country').text.split(':')[0]
    date = driver.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[0]
    dictionary['Date'] = date.replace('.','/')
    time = driver.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[1]
    dictionary['Time'] = time
    league = driver.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country > a').text.split(' -')[0]
    dictionary['League'] = f'{country} - {league}'
    home = driver.find_element(By.CSS_SELECTOR,'div.duelParticipant__home').find_element(By.CSS_SELECTOR,'div.participant__participantName').text
    dictionary['Home'] = home
    away = driver.find_element(By.CSS_SELECTOR,'div.duelParticipant__away').find_element(By.CSS_SELECTOR,'div.participant__participantName').text
    dictionary['Away'] = away
    try:
        rodada = driver.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country > a').text.split('- ')[1]
        dictionary['Round'] = rodada
    except:
        dictionary['Round'] = '-'

def Temporada(dictionary,season):
    dictionary['Season'] = season

def Gols_HT_FT(id_jogo,dictionary,driver):
    try:
        if '1st Half' in driver.page_source:
            WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.smv__incidentsHeader')))
            home_goals_ht = driver.find_elements(By.CSS_SELECTOR,'div.smv__incidentsHeader div')[1].text.split('-')[0]
            dictionary['Goals_H_HT'] = int(home_goals_ht)
            away_goals_ht = driver.find_elements(By.CSS_SELECTOR,'div.smv__incidentsHeader div')[1].text.split('-')[1]
            dictionary['Goals_A_HT'] = int(away_goals_ht)
    except:
        pass
    home_goals_ft = driver.find_element(By.CSS_SELECTOR,'div.detailScore__wrapper').text.split('-')[0]
    dictionary['Goals_H_FT'] = int(home_goals_ft)
    away_goals_ft = driver.find_element(By.CSS_SELECTOR,'div.detailScore__wrapper').text.split('-')[1]
    dictionary['Goals_A_FT'] = int(away_goals_ft)

def Odds_Math_Odds(id_jogo,dictionary,driver):
    url_match_odds = f'https://www.flashscore.com/match/{id_jogo}/#/odds-comparison/1x2-odds/full-time'
    driver.get(url_match_odds)
    sleep(1)
    if driver.current_url == url_match_odds:
        WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.ui-table')))
        table_odds = driver.find_element(By.CSS_SELECTOR,'div.ui-table')
        linha_ml_ft = table_odds.find_element(By.CSS_SELECTOR,'div.ui-table__row')
        dictionary['Odd_H'] = float(linha_ml_ft.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
        dictionary['Odd_D'] = float(linha_ml_ft.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
        dictionary['Odd_A'] = float(linha_ml_ft.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[2].text)
        
def Odds_Over_Under(id_jogo,dictionary,driver):
    url_over_under = f'https://www.flashscore.com/match/{id_jogo}/#/odds-comparison/over-under/full-time'
    driver.get(url_over_under)
    sleep(1)
    if driver.current_url == url_over_under:
        WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.ui-table')))
        linhas = driver.find_elements(By.CSS_SELECTOR,'div.ui-table__body')
        for linha in linhas:
            if (len(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')) > 1):
                total_gols = linha.find_element(By.CSS_SELECTOR,'span.oddsCell__noOddsCell').text.replace('.','')
                if total_gols == '25':
                    over = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                    under = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                    dictionary[f'Odd_Over{total_gols}'] = over
                    dictionary[f'Odd_Under{total_gols}'] = under
                
def Odds_BTTS(id_jogo,dictionary,driver):
    url_btts = f'https://www.flashscore.com/match/{id_jogo}/#/odds-comparison/both-teams-to-score/full-time'
    driver.get(url_btts)
    sleep(1)
    if driver.current_url == url_btts:
        WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.ui-table')))
        linha = driver.find_element(By.CSS_SELECTOR,'div.ui-table__row')
        dictionary['Odd_BTTS_Yes'] = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
        dictionary['Odd_BTTS_No'] = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
        
def Odds_Dupla_Chance(id_jogo,dictionary,driver):
    url_dupla_chance = f'https://www.flashscore.com/match/{id_jogo}/#/odds-comparison/double-chance/full-time'
    driver.get(url_dupla_chance)
    sleep(1)
    if driver.current_url == url_dupla_chance:
        WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.ui-table')))
        linha = driver.find_element(By.CSS_SELECTOR,'div.ui-table__row')
        dictionary['Odd_1X'] = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
        dictionary['Odd_12'] = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
        dictionary['Odd_X2'] = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[2].text)

def Odds_Handicap_Asiatico(id_jogo,dictionary,driver):
    url_handicap_asiatico = f'https://www.flashscore.com/match/{id_jogo}/#/odds-comparison/asian-handicap/full-time'
    driver.get(url_handicap_asiatico)
    sleep(1)
    if driver.current_url == url_handicap_asiatico:
        WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.ui-table')))
        linhas = driver.find_elements(By.CSS_SELECTOR,'div.ui-table__body')
        for linha in linhas:
            if (len(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')) > 1):
                linha_handcap = linha.find_element(By.CSS_SELECTOR,'span.oddsCell__noOddsCell').text
                if (linha_handcap == '-1.5'):
                    linha_handcap = linha_handcap.replace('-','')
                    linha_handcap = linha_handcap.replace('.','')
                    ah_home = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                    ah_away = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                    dictionary[f'Odd_AH_Neg{linha_handcap}_H'] = ah_home
                    dictionary[f'Odd_AH_Pos{linha_handcap}_A'] = ah_away
                elif (linha_handcap == '-1'):
                    linha_handcap = linha_handcap.replace('-','')
                    ah_home = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                    ah_away = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                    dictionary[f'Odd_AH_Pos{linha_handcap}0_H'] = ah_home
                    dictionary[f'Odd_AH_Neg{linha_handcap}0_A'] = ah_away
                elif (linha_handcap == '-0.5'):
                    linha_handcap = linha_handcap.replace('-','')
                    linha_handcap = linha_handcap.replace('.','')
                    ah_home = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                    ah_away = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                    dictionary[f'Odd_AH_Neg{linha_handcap}_H'] = ah_home
                    dictionary[f'Odd_AH_Pos{linha_handcap}_A'] = ah_away
                elif (linha_handcap == '0'):
                    ah_home = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                    ah_away = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                    dictionary[f'Odd_AH_Pos{linha_handcap}0_H'] = ah_home
                    dictionary[f'Odd_AH_Neg{linha_handcap}0_A'] = ah_away
                elif (linha_handcap == '+0.5'):
                    linha_handcap = linha_handcap.replace('+','')
                    linha_handcap = linha_handcap.replace('.','')
                    ah_home = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                    ah_away = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                    dictionary[f'Odd_AH_Pos{linha_handcap}_H'] = ah_home
                    dictionary[f'Odd_AH_Neg{linha_handcap}_A'] = ah_away
                elif (linha_handcap == '+1'):
                    linha_handcap = linha_handcap.replace('+','')
                    ah_home = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                    ah_away = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                    dictionary[f'Odd_AH_Pos{linha_handcap}0_H'] = ah_home
                    dictionary[f'Odd_AH_Neg{linha_handcap}0_A'] = ah_away
                elif (linha_handcap == '+1.5'):
                    linha_handcap = linha_handcap.replace('+','')
                    linha_handcap = linha_handcap.replace('.','')
                    ah_home = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[0].text)
                    ah_away = float(linha.find_elements(By.CSS_SELECTOR,'a.oddsCell__odd')[1].text)
                    dictionary[f'Odd_AH_Pos{linha_handcap}_H'] = ah_home
                    dictionary[f'Odd_AH_Neg{linha_handcap}_A'] = ah_away

def Odds_Correct_Score(id_jogo,dictionary,driver):
    url_correct_score = f'https://www.flashscore.com/match/{id_jogo}/#/odds-comparison/correct-score/full-time'
    driver.get(url_correct_score)
    sleep(1)
    if driver.current_url == url_correct_score:
        WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.ui-table')))
        for celula in driver.find_elements(By.CSS_SELECTOR,'div.ui-table__body'):
            linha = celula.find_element(By.CSS_SELECTOR,'div.ui-table__row')
            placar = linha.find_element(By.CSS_SELECTOR,'span.oddsCell__noOddsCell').text.replace(':','-')
            if (placar == '0-0'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '0-1'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '0-2'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '0-3'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '1-0'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '1-1'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '1-2'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '1-3'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '2-0'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '2-1'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '2-2'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '2-3'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '3-0'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '3-1'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '3-2'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '3-3'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd
            elif (placar == '4-4'):
                odd = float(linha.find_element(By.CSS_SELECTOR,'a.oddsCell__odd').text)
                dictionary[f'Odd_CS_{placar}'] = odd

def Minutos_dos_Gols(id_jogo,dictionary,driver):
    def trata_minuto(minuto):
        minuto = minuto
        if "'" in minuto:
            minuto = minuto.replace("'","")
        if ":" in minuto:
            minuto = minuto.split(':')[0]
        if "+" in minuto:
            minuto = minuto.split('+')[0]
        return int(minuto)
    url = f'https://www.flashscore.com/match/{id_jogo}/#/match-summary/match-summary'
    if driver.current_url != url:
        driver.get(url)
    try:
        WebDriverWait(driver, 8).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.smv__verticalSections')))
        soup = driver.page_source
        soup = BeautifulSoup(driver.page_source)
        min_goals_home = []
        min_goals_away = []
        try:
            home_incidents = soup.find_all('div',{"class":['smv__homeParticipant']})
            for i in home_incidents:
                if ('smv__incidentHomeScore' in str(i)) | ('footballOwnGoal-ico' in str(i)):
                    min_goals_home.append(trata_minuto(i.find('div',{"class":['smv__timeBox']}).text))
            dictionary['Goals_Minutes_Home'] = min_goals_home
        except:
            dictionary['Goals_Minutes_Home'] = min_goals_home
        try:
            away_incidents = soup.find_all('div',{"class":['smv__awayParticipant']})
            for i in away_incidents:
                if ('smv__incidentAwayScore' in str(i)) | ('footballOwnGoal-ico' in str(i)):
                    min_goals_away.append(trata_minuto(i.find('div',{"class":['smv__timeBox']}).text))
            dictionary['Goals_Minutes_Away'] = min_goals_away
        except:
                dictionary['Goals_Minutes_Away'] = min_goals_away
    except:
        pass                    
