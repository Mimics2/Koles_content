import telebot
from telebot import types

# Вставьте сюда ваш токен бота
BOT_TOKEN = '8335870133:AAHwcXoy3usOWT4Y9F8cSOPiHwX5OO33hI8'

bot = telebot.TeleBot(BOT_TOKEN)

# Приветственное сообщение и основное меню
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_subscribe = types.KeyboardButton('Оформить подписку')
    btn_info = types.KeyboardButton('Информация')
    markup.add(btn_subscribe, btn_info)
    bot.reply_to(message, "Привет! Я бот для публикации постов. Чем могу помочь?", reply_markup=markup)

# Обработка команды /subscribe
@bot.message_handler(commands=['subscribe'])
def subscribe_command(message):
    bot.reply_to(message, "Здесь будет функция для оформления подписки.")

# Обработка кнопки "Оформить подписку"
@bot.message_handler(func=lambda message: message.text == 'Оформить подписку')
def handle_subscribe_button(message):
    subscribe_command(message)

# Обработка команды /info
@bot.message_handler(commands=['info'])
def info_command(message):
    bot.reply_to(message, "Здесь будет информация о подписках и тарифах.")

# Обработка кнопки "Информация"
@bot.message_handler(func=lambda message: message.text == 'Информация')
def handle_info_button(message):
    info_command(message)

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)

