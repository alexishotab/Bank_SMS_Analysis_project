import telebot 
from telebot import types
from database import Database
from DataMethods import Short_analyse
from DataMethods import Long_analyse
import warnings

#db=Database('db.db3')
bot = telebot.TeleBot('YOUR TELEGRAM-BOT TOKEN')
#Spam warnings - Matplotlib plots outside main stream (they in data-classes)
warnings.filterwarnings("ignore", category = FutureWarning)
warnings.filterwarnings("ignore", category = UserWarning)
#Data-analytical classes, contains methods with printing and painting plots
short = Short_analyse()
long = Long_analyse()
# Создаем объект клавиатуры
menu = telebot.types.ReplyKeyboardMarkup(row_width = 2)

# Добавляем кнопки в клавиатуру
menu.add(telebot.types.KeyboardButton('Прогноз трат на N дней'),
         telebot.types.KeyboardButton('Средние расходы в разное время дня'),
         telebot.types.KeyboardButton('Общие расходы в разное время дня'),
         telebot.types.KeyboardButton('Стал ли я тратить больше?'),
         telebot.types.KeyboardButton('Статистика по всем вашим тратам'),
         telebot.types.KeyboardButton('Топ расходов за все время'))

@bot.message_handler(commands=['start', 'menu'])
def start_message(message: telebot.types.Message)->None:
    try:
        bot.send_message(message.chat.id,
                         "Выберите пункт меню:",
                         reply_markup=menu)
    except: bot.send_message(message.chat.id,
                         "Повторите попытку")

# Обрабатываем нажатия на кнопки
@bot.message_handler(content_types=['text'])
def handle_message(message: telebot.types.Message) -> None:
    try:
        if message.text \
            == 'Прогноз трат на N дней':
            bot.send_message(message.chat.id, 'Введите число - на сколько дней \
вперед нужен прогноз (до 14 включительно)')
            bot.register_next_step_handler(message, get_day_and_paint)
            
        elif message.text \
            == 'Средние расходы в разное время дня':
            short.preparing_data_for_timegraphics()
            short.bar_graphics()
            with open('barplot.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            with open('scatterplot.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            bot.send_message(message.chat.id,
                             'Графики расходов по времени дня за последние 2 недели')
            
        elif message.text \
            == 'Общие расходы в разное время дня':
            short.preparing_data_for_timegraphics()
            short.pie_graphic()
            with open('pieplot.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            bot.send_message(message.chat.id, 'График расходов по времени суток')

        elif message.text \
             == 'Стал ли я тратить больше?':
            bot.send_message(message.chat.id, 'Введите номера 2-ух месяцев через пробел\nПример ввода: "1 12"')
            bot.register_next_step_handler(message, get_months_and_print)
            
        elif message.text \
             == 'Статистика по всем вашим тратам':
            long.getting_groupped_data()
            long.preparing_data_for_model()
            predicted = long.training_model()
            mess = long.statistic_by_day(predicted)
            bot.send_message(message.chat.id, mess)
            
        elif message.text \
             == 'Топ расходов за все время':
            long.top_13_expenses()
            with open('dataframe.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            bot.send_message(message.chat.id, 'График суммы и ср.арифм. расходов')
            
        else:
            bot.send_message(message.chat.id, 'Команда не распознана')
    except: bot.send_message(message.chat.id,
                         "Повторите попытку")

#method for button 'Стал ли я тратить больше?' in `handle_message`
def get_months_and_print(message: telebot.types.Message) -> None:
    try:
        list1, list2, m1, m2 = long.prepare_data_for_ttest_month(message.text)
        string = long.ttest_month(list1, list2, m1, m2)
        bot.send_message(message.chat.id, string)
    except: bot.send_message(message.chat.id, 'Повторите попытку')

#method for button 'Прогноз трат на N дней' in `handle_message`
def get_day_and_paint(message: telebot.types.Message) -> None:
    try:
        day = int(message.text)
        if day <= 14 and day > 0:
            short.getting_groupped_data() 
            (pred, model2) = short.training_model()
            short.saving_graphic_of_model(day)
            with open('Selecting_regression.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            string =f"Вам предстоит потратить еще \
{round(pred[13+day]-pred[13],1)}р в ближайшие {day} \
{'день' if day<2 else 'дня' if day<5 else 'дней'}."
            bot.send_message(message.chat.id, string)
    except Exception as e:
        print("Ошибка:", e)
        bot.send_message(message.chat.id,
                         'Возникла ошибка. Проверьте ввод данных')

bot.polling()
