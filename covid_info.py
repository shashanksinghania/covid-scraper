import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
import pyttsx3

res = requests.get('https://www.worldometers.info/coronavirus/')
soup = BeautifulSoup(res.text, 'html.parser')
total_soup = soup.select('#maincounter-wrap')

# Keeps track of the world-wide cases
total_stats = []

for element in total_soup:
    number = element.div.text.strip().replace(',', '')
    total_stats.append(int(number))

main_table = soup.find('table')
table_body = main_table.tbody
i = 0

countries_data = []
for tr in table_body.find_all('tr', {'style':""}):
    if not tr.get('class', None):
        tds = tr.find_all('td')
        country = dict()
        country['name'] = tds[1].text.strip()
        country['cases'] = tds[2].text.strip()
        country['deaths'] = tds[4].text.strip()
        countries_data.append(country)

print(total_stats)
print(countries_data)

r = sr.Recognizer()


# To convert text to speech for replying
def speak(text):
    speak_engine = pyttsx3.init()
    speak_engine.say(text)
    speak_engine.runAndWait()


