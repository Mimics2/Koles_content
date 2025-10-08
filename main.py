import telebot
from telebot import types
import datetime
import db  # Наш модуль для работы с базой данных
import payments  # Наш модуль для работы с платежами

# Замените на ваш токен бота
BOT_TOKEN = '8335870133:AAHwcXoy3usOWT4Y9F8cSOPiHwX5OO33hI8'

bot = telebot.TeleBot(BOT_TOKEN)

# Тарифные планы
TARIFFS = {
    'mini': {'price': 1, 'channels': 1, 'posts_per_day': 2, 'duration_days': 30},
    'standard': {'price': 4, 'channels': 3, 'posts_per_day': 6, 'duration_days': 30},
    'pro': {'price': 10, 'channels': 'безлимит', 'posts_per_day': 'безлимит', 'duration_days': 30}
}

# Приветственное сообщение и основное меню
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Добавляем пользователя в базу данных при первом контакте
    db.add_user(message.from_user.id, message.from_user.username)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_subscribe = types.KeyboardButton('Оформить подписку')
    btn_info = types.KeyboardButton('Информация')
    markup.add(btn_subscribe, btn_info)
    bot.reply_to(message, "Привет! Я бот для публикации постов. Чем могу помочь?", reply_markup=markup)

# Обработка команды /subscribe и кнопки "Оформить подписку"
@bot.message_handler(commands=['subscribe'], func=lambda message: True)
@bot.message_handler(func=lambda message: message.text == 'Оформить подписку')
def show_subscription_options(message):
    markup = types.InlineKeyboardMarkup()
    for tariff_name, tariff_info in TARIFFS.items():
        price = tariff_info['price']
        button_text = f"{tariff_name.capitalize()} - ${price}"
        callback_data = f"buy_{tariff_name}"
        markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
    
    bot.send_message(message.chat.id, "Выберите тарифный план:", reply_markup=markup)

# Обработка кнопки с тарифом (inline keyboard)
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_tariff_callback(call):
    tariff_name = call.data.split('_')[1]
    tariff_info = TARIFFS.get(tariff_name)
    
    if not tariff_info:
        bot.send_message(call.message.chat.id, "Тариф не найден.")
        return

    amount = tariff_info['price']
    currency = 'USDT'
    description = f"Подписка на тариф {tariff_name}"
    payload = f"user_{call.from_user.id}_tariff_{tariff_name}"
    
    invoice_data = payments.create_invoice(amount, currency, description, payload)

    if invoice_data and invoice_data.get('ok'):
        invoice_url = invoice_data['result']['pay_url']
        invoice_id = invoice_data['result']['invoice_id']
        
        markup = types.InlineKeyboardMarkup()
        btn_pay = types.InlineKeyboardButton("Перейти к оплате", url=invoice_url)
        btn_check = types.InlineKeyboardButton("Я оплатил", callback_data=f"check_{invoice_id}_{tariff_name}")
        markup.add(btn_pay)
        markup.add(btn_check)
        
        bot.send_message(call.message.chat.id, 
                         f"Счет на {amount} {currency} создан. Нажмите кнопку, чтобы оплатить.",
                         reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "Не удалось создать счет. Попробуйте позже.")

# Обработка кнопки "Я оплатил"
@bot.callback_query_handler(func=lambda call: call.data.startswith('check_'))
def handle_check_payment(call):
    try:
        data_parts = call.data.split('_')
        # Получаем invoice_id и tariff_name из callback_data
        invoice_id = data_parts[1]
        tariff_name = data_parts[2]
        
        bot.answer_callback_query(call.id, text="Проверяю статус платежа...")
        
        status = payments.check_invoice_status(invoice_id)
        
        if status == 'paid':
            # Если оплата прошла, обновляем базу данных
            tariff_info = TARIFFS.get(tariff_name)
            end_date = datetime.date.today() + datetime.timedelta(days=tariff_info['duration_days'])
            db.update_subscription(call.from_user.id, tariff_name, end_date.isoformat())
            
            bot.send_message(call.message.chat.id, "✅ Платеж успешно подтвержден! Ваша подписка активирована.")
        else:
            bot.send_message(call.message.chat.id, f"Статус платежа: **{status}**. Пожалуйста, подождите или попробуйте еще раз.")
            
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Произошла ошибка при проверке платежа: {e}")

# Обработка команды /info и кнопки "Информация"
@bot.message_handler(commands=['info'], func=lambda message: True)
@bot.message_handler(func=lambda message: message.text == 'Информация')
def info_command(message):
    user_info = db.get_user(message.from_user.id)
    if user_info:
        subscription_type = user_info[3] if user_info[3] else "Нет"
        subscription_end = user_info[4] if user_info[4] else "Нет"
        
        info_text = (
            f"**Информация о вашем аккаунте:**\n"
            f"ID: `{message.from_user.id}`\n"
            f"Подписка: **{subscription_type}**\n"
            f"Действительна до: **{subscription_end}**"
        )
        bot.send_message(message.chat.id, info_text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Ваши данные не найдены. Пожалуйста, напишите /start.")

# Запуск бота
if __name__ == "__main__":
    db.init_db()
    bot.polling(none_stop=True)
