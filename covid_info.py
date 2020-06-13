import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
import pyttsx3
import re

res = requests.get('https://www.worldometers.info/coronavirus/')
soup = BeautifulSoup(res.text, 'html.parser')
total_soup = soup.select('#maincounter-wrap')

# Keeps track of the world-wide cases
total_stats = []
# Keeps track of data for countries
countries_data = []
country_names = []

for element in total_soup:
    number = element.div.text.strip()
    total_stats.append(number)


# Gives the total number of cases in the world
def get_total_cases():
    return total_stats[0]


# Gives the total number of deaths in the world
def get_total_deaths():
    return total_stats[1]


# Gives the total number of cases recovered in the world
def get_total_recovered():
    return total_stats[2]


main_table = soup.find('table')
table_body = main_table.tbody
i = False

# To build a data set for all the countries
for tr in table_body.find_all('tr', {'style': ""}):
    if not tr.get('class', None):
        tds = tr.find_all('td')
        country = dict()
        country['name'] = tds[1].text.strip()
        country_names.append(tds[1].text.strip().lower())
        country['cases'] = tds[2].text.strip()
        country['deaths'] = tds[4].text.strip()
        countries_data.append(country)


# To get data for a particular country
def get_data_for_country(name):
    for country in countries_data:
        if country['name'].lower() == name.lower():
            return country
    return None


# To convert text to speech for replying
def speak(ans):
    speak_engine = pyttsx3.init()
    speak_engine.say(ans)
    speak_engine.runAndWait()


# To convert speach to text
def listen():
    r = sr.Recognizer()
    text = ""
    with sr.Microphone() as source1:
        r.adjust_for_ambient_noise(source1, duration=0.2)

        try:
            print("SS: Listening...")
            speak("listening")
            audio = r.listen(source1)
            text = r.recognize_google(audio)
            print("You: " + text)

        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))

        except sr.UnknownValueError:
            print("unknown error occured")
    return text.lower()


def main():
    answer = None
    print("Program started")
    END_PHRASE = ["stop", "top", "end", "ok"]
    text = None

    # Search patterns
    TOTAL_PATTERN = {
        re.compile("[\w\s]*recovered"): get_total_recovered,
        re.compile("[\w\s]*total [\w\s]*recovered cases"): get_total_recovered,
        re.compile("[\w\s]*total [\w\s]*cases"): get_total_cases,
        re.compile("[\w\s]*total cases"): get_total_cases,
        re.compile("[\w\s]*cases [\w\s]*world"): get_total_cases,
        re.compile("[\w\s]*recovered cases [\w\s]*world"): get_total_recovered,
        re.compile("[\w\s]*total [\w\s]*death"): get_total_deaths,
        re.compile("[\w\s]*deaths [\w\s]*world"): get_total_deaths
    }

    COUNTRY_PATTERN = {
        re.compile("[\w\s]*cases[\w\s]*"): lambda country: get_data_for_country(country)['cases'],
        re.compile("[\w\s]*death[\w\s]*"): lambda country: get_data_for_country(country)['deaths']
    }

    while True:
        text = listen()

        # Flag
        end = False

        # First check if it is country specific data
        for pattern, funct in COUNTRY_PATTERN.items():
            if pattern.match(text):
                words = set(text.split())
                for country in country_names:
                    if country in words:
                        answer = funct(country)
                        print("SS:", answer)
                        break
        if answer:
            speak(answer)
            answer = None
            continue

        # Then check if it is world-wide data
        for pattern, funct in TOTAL_PATTERN.items():
            if pattern.match(text):
                answer = funct()
                print("SS:", answer)
                break

        if answer:
            speak(answer)
            answer = None

        # STOP chat
        for words in END_PHRASE:
            if text.find(words) != -1:
                print("SS: Bye!")
                end = True
                break

        # Exit the loop
        if end:
            break


if __name__ == '__main__':
    main()
