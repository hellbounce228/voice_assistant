import time
import random
from reprlib import aRepr
from turtledemo.forest import randomize
import pygame
import random
import os
import sys
import threading
import speech_recognition
import pyttsx3
import openai


###BUILDING THE VOICE ASSISTANT
# Настройка OpenAI
openai.api_key = "Api-key"

# Глобальные переменные
stop_speech = threading.Event()
stop_listening = threading.Event()
assistant_working = False




def speak_eng(text):
    """Озвучивает предоставленный текст."""
    engine = pyttsx3.init()
    engine.setProperty('voice','HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0')
    engine.setProperty('rate', 150)

    for part in text.split('.'):
        if stop_speech.is_set():  # Проверяем, нужно ли остановить речь
            engine.stop()
            break
        engine.say(part.strip())
        engine.runAndWait()


def safe_chat_eng(prompt):
    """Получает ответ от OpenAI API."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt + ' '},
            ],
            max_tokens=400,
            temperature=1,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("Error with OpenAI:", e)
        return "Извините, возникла ошибка."


def listen_for_keyword_eng():
    """Слушает ключевое слово для остановки речи."""
    recognizer = speech_recognition.Recognizer()

    while not stop_listening.is_set():  # Пока поток активен
        try:
            with speech_recognition.Microphone() as mic:
                print("Listening for the keyword...")
                recognizer.adjust_for_ambient_noise(mic, duration=0.5)
                audio = recognizer.listen(mic, timeout=5)  # Слушаем с таймаутом
                keyword = recognizer.recognize_google(audio, language="en-EN").lower()

                if "stop" in keyword:  # Замените "стоп" на нужное ключевое слово
                    print("Keyword detected: stopping speech.")
                    stop_speech.set()  # Устанавливаем флаг для остановки речи
        except speech_recognition.UnknownValueError:
            continue  # Игнорируем нераспознанные звуки
        except Exception as e:
            print("Error while listening:", e)


def voice_assistant_eng():
    """Основной цикл программы."""
    global stop_speech, stop_listening
    previous_prompt_x1 = "Hi! Tell me about yourself"
    previous_answer = "Hi! im your assistant."

    while assistant_working:
        recognizer = speech_recognition.Recognizer()
        stop_speech.clear()  # Сбрасываем событие для нового цикла
        stop_listening.clear()

        try:
            with speech_recognition.Microphone() as mic:
                #print("Waiting for input...")
                recognizer.adjust_for_ambient_noise(mic, duration=2)
                speak_eng('listening')
                audio = recognizer.listen(mic)
                text = recognizer.recognize_google(audio, language="en-EN").lower()
                #print(f"Recognized: {text}")

                # Построение контекста разговора
                question = text
                final_question = (
                    f"Here is some context: my first questions was: {previous_prompt_x1}, "
                    f"; and your answer was: {previous_answer}; and my final question is: {question}"
                )
                previous_prompt_x1 = question

                # Получение ответа от OpenAI
                answer = safe_chat_eng(final_question)
                previous_answer = answer

                # Запускаем поток для озвучивания
                speech_thread = threading.Thread(target=speak_eng, args=(answer,))
                speech_thread.start()

                # Запускаем поток для прослушивания ключевого слова
                listener_thread = threading.Thread(target=listen_for_keyword_eng)
                listener_thread.start()

                # Ждем завершения речи
                speech_thread.join()

                # Устанавливаем флаг завершения для потока прослушивания
                stop_listening.set()
                listener_thread.join()

        except speech_recognition.UnknownValueError:
            print("Could not understand the audio.")
        except KeyboardInterrupt:
            print("Exiting...")
            stop_listening.set()
            stop_speech.set()
            break







def speak_ru(text):
    """Озвучивает предоставленный текст."""
    engine = pyttsx3.init()
    engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_RU-RU_IRINA_11.0')
    engine.setProperty('rate', 150)

    for part in text.split('.'):
        if stop_speech.is_set():
            engine.stop()
            break
        engine.say(part.strip())
        engine.runAndWait()

def safe_chat_ru(prompt):
    """Получает ответ от OpenAI API."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты полезный помощник."},
                {"role": "user", "content": prompt + ' '},
            ],
            max_tokens=400,
            temperature=1,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("Error with OpenAI:", e)
        return "Извините, возникла ошибка."

def listen_for_keyword_ru():
    """Слушает ключевое слово для остановки речи."""
    recognizer = speech_recognition.Recognizer()

    while not stop_listening.is_set():
        try:
            with speech_recognition.Microphone() as mic:
                print("Listening for the keyword...")
                recognizer.adjust_for_ambient_noise(mic, duration=0.5)
                audio = recognizer.listen(mic, timeout=5)
                keyword = recognizer.recognize_google(audio, language="ru-RU").lower()

                if "стоп" in keyword:
                    print("Keyword detected: stopping speech.")
                    stop_speech.set()
        except speech_recognition.UnknownValueError:
            continue
        except Exception as e:
            print("Error while listening:", e)

def voice_assistant_ru():
    """Основной цикл голосового ассистента."""
    global stop_speech, stop_listening, assistant_working
    previous_prompt_x1 = "расскажи про себя"
    previous_answer = "Привет! Я твой помощник"

    while assistant_working:
        recognizer = speech_recognition.Recognizer()
        stop_speech.clear()
        stop_listening.clear()

        try:
            with speech_recognition.Microphone() as mic:
                #print("Waiting for input...")
                recognizer.adjust_for_ambient_noise(mic, duration=2)
                speak_ru('слушаю')
                audio = recognizer.listen(mic)

                text = recognizer.recognize_google(audio, language="ru-RU")
                #print(f"Recognized: {text}")

                # Построение контекста разговора
                question = text
                final_question = (
                    f"Вот вам немного контекста: первый вопрос была: {previous_prompt_x1}, "
                    f"и твой ответ: {previous_answer}; а мой финальный вопрос: {question}"
                )
                previous_prompt_x1 = question

                # Получение ответа от OpenAI
                answer = safe_chat_ru(final_question)
                previous_answer = answer

                # Поток для озвучивания
                speech_thread = threading.Thread(target=speak_ru, args=(answer,))
                speech_thread.start()

                # Поток для прослушивания ключевого слова
                listener_thread = threading.Thread(target=listen_for_keyword_ru)
                listener_thread.start()

                # Ждем завершения речи
                speech_thread.join()

                # Завершаем поток прослушивания
                stop_listening.set()
                listener_thread.join()

        except speech_recognition.UnknownValueError:
            print("Could not understand the audio.")
        except KeyboardInterrupt:
            print("Exiting...")
            stop_listening.set()
            stop_speech.set()
            break





pygame.font.init()


### PYGAME VARIABLES
fps = 30
displaywidth=420
displayheight=724
window = pygame.display.set_mode((displaywidth, displayheight))
black=(0,0,0)
red=(255,0,0)
white=(255,255,255)
font= pygame.font.SysFont('Arial', 40)
#window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((displaywidth, displayheight))
pygame.display.set_caption("Voice Assistant")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()

#loading pictures...
running = True

#start_assistant_button_img = pygame.image.load('startbutton.png')
bg_img = pygame.image.load('images/bg.png')
start_bg = pygame.image.load('images/start.png')
setting_button_img = pygame.image.load('images/settings_button.png')
usa_img = pygame.image.load('images/usa.png')
ukraine_img = pygame.image.load('images/ukraine.png')
get_back_img = pygame.image.load('images/get_back.png')




class Button():
    def __init__(self, image, x, y):
        self.image = image
        #self.image.set_colorkey(white)
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, win):
        win.blit(self.image, self.rect.topleft)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, win):
        win.blit(self.image, self.rect.topleft)


backgroundsprite = Sprite(bg_img, -6,0)
startbutton = Button(start_bg, 77, 271)
settingsbutton = Button(setting_button_img, 164, 464)
ukraine = Button(ukraine_img, 128, 560)
usa = Button(usa_img, 220, 560)
get_back_pseudo_button = Sprite(get_back_img, 164,464)


assistant_working=False
assistant_thread = None
in_menu = True
in_settings = False
russian_assistant=False
english_assistant=True
while running:
    screen.fill((33,33,33))
    for event in pygame.event.get():
        # check if window is closed
            if event.type == pygame.QUIT:
                running = False
            # check if clicked
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                #print(pos)
                if startbutton.is_clicked(pos) and not assistant_working:
                    #print('star button clicked')
                    assistant_working=True
                    if russian_assistant:
                        assistant_thread = threading.Thread(target=voice_assistant_ru, daemon=True)
                    if english_assistant:
                        assistant_thread = threading.Thread(target=voice_assistant_eng, daemon=True)
                    assistant_thread.start()
                elif startbutton.is_clicked(pos) and assistant_working:
                    assistant_working=False
                    #print('stop button clicked')
                    stop_speech.set()
                    stop_listening.set()
                if assistant_thread is not None and assistant_thread.is_alive():
                    assistant_thread.join(timeout=2)
                if settingsbutton.is_clicked(pos) and not in_settings:
                    #print('setting button clicked')
                    in_settings=True
                elif settingsbutton.is_clicked(pos) and in_settings:
                    #print('get back button clicked')
                    in_settings=False

                if in_settings and ukraine.is_clicked(pos):
                    russian_assistant=True
                    english_assistant=False
                    speak_ru('русский')
                    #print('lang changed to Russian')
                if in_settings and usa.is_clicked(pos):
                    english_assistant=True
                    russian_assistant=False
                    speak_eng('english')
                    #print('lang changed to English')

    if in_menu:
        backgroundsprite.draw(window)
        settingsbutton.draw(window)
        if not assistant_working:
            startbutton.draw(window)
        if in_settings:
            ukraine.draw(window)
            usa.draw(window)
            get_back_pseudo_button.draw(window)



    clock.tick(fps)
    all_sprites = pygame.sprite.Group()
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
