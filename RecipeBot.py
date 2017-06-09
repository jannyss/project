from bs4 import BeautifulSoup
import telebot
import re
import requests
import random
from telebot import types


access_token = "198167022:AAGAsVWecf6y_Ul3e9BdleEirSxbH6HI1xs"
bot = telebot.TeleBot(access_token)

hello_message = '<b>Добро пожаловать!</b>\n ' \
                'Я - бот для поиска очень вкусных рецептов самых разнообразных блюд. \n '

'''def get_url_recipe(food, page, line):
    url = 'http://www.gastronom.ru/search/type/recipe/?t=&title={food}&page={page}'.format(food=food, page=page)
    response = requests.get(url)
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html5lib')
    lis = soup.find_all("article", class_="article col-sm-4 col-ms-6 ")
    recipe_href = []
    k = 0
    for j in lis:
        jj = j.find("a", class_="img full myFix")
        recipes = str(jj).split('"')
        for i in recipes:
            if re.findall('recipe', i):
                recipe_href.append(i)
                k += 1
    url = 'http://www.gastronom.ru' + recipe_href[line]
    return url, page, line'''


# получение адреса нужной страницы, номер страницы и номер рецепта на этой странице
def get_page(food):
    url = 'http://www.gastronom.ru/search/type/recipe/?t=&title={food}'.format(food=food)
    response = requests.get(url)
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html5lib')
    tags = soup.find("div", class_="tags")
    tags = tags.find("span", class_="big-tag big-tag__muted myFixTag").text.split(": ")
    if int(tags[1]) != 0:
        p = random.randint(1, int(tags[1]))
        page = p // 24
        url = 'http://www.gastronom.ru/search/type/recipe/?t=&title={food}&page={page}'.format(food=food, page=page)
        response = requests.get(url)
        web_page = response.text
        soup = BeautifulSoup(web_page, 'html5lib')
        lis = soup.find_all("article", class_="article col-sm-4 col-ms-6 ")
        recipe_href = []
        k = 0
        for j in lis:
            jj = j.find("a", class_="img full myFix")
            recipes = str(jj).split('"')
            for i in recipes:
                if re.findall('recipe', i):
                    recipe_href.append(i)
                    k += 1
        k = random.randint(0, len(recipe_href)-1)
        url = 'http://www.gastronom.ru' + recipe_href[k]
        return url, page, k


# получение списка ингредиентов, списка шагов выполнения, названия рецепта и ссылки на картинку данного рецепта
def get_recipe(url):
    response = requests.get(url)
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html5lib')
    ingredients_list = soup.find_all("li", attrs={"class": "ingredient"})
    ingredients_list = [ingredient.text for ingredient in ingredients_list]
    title = soup.find("title").text
    title = title.split(',')

    steps_list = soup.find_all("div", attrs={"class": "step instruction"})
    steps = []
    for step in steps_list:
        st = step.find("p")
        st = st.text
        st = st.strip()
        steps.append(st)

    # time = soup.find("p", attrs={"class": "big", "itemprop": "totalTime"}).text
    image = soup.find("meta", attrs={"property": "og:image"})
    img = str(image).split('"')
    for i in img:
        if re.findall('http', i):
            href = i
    return ingredients_list, steps, title[0], href




'''
@bot.message_handler(content_types=['text'])
def recipe(message):
    try:
        ingred, steps, time, title, image = get_recipe(get_page(message.text))
        ingredients = "<b>Ингредиенты для вашего блюда:</b> \n"
        for i in ingred:
            ingredients += "- " + i
            ingredients += '\n'
        ingredients += '\n'

        stps = "<b>Порядок выполнения:</b>\n"
        k = 1
        for i in steps:
            stps += "<i>Шаг " + str(k) + "</i>. " + i + '\n'
            k += 1

        tm = "<b>Время выполнения:</b> " + time + '\n'

        resp = '<b>' + title + '</b>\n' + ingredients + stps + tm
        bot.send_photo(message.chat.id, image)
    except Exception:
        resp = 'По вашему запросу ничего не найдено'
    bot.send_message(message.chat.id, resp, parse_mode='HTML')


'''


# красивый вывод рецепта
def get_recipe_view(ingreds, steps, title):
    ingredients = "<b>Ингредиенты для вашего блюда:</b> \n"
    for i in ingreds:
        ingredients += "- " + i
        ingredients += '\n'
    ingredients += '\n'
    stps = "<b>Порядок выполнения:</b>\n"
    k = 1
    for i in steps:
        stps += "Шаг " + str(k) + ". " + i + '\n'
        k += 1
    resp = '<b>' + title + '</b>\n' + ingredients
    return resp, stps


@bot.message_handler(commands=['recipe'])
def start(m):
    _, food = m.text.split()
    url1, page1, line1 = get_page(food)
    ingred1, steps1, title1, image1 = get_recipe(url1)
    url2, page2, line2 = get_page(food)
    ingred2, steps2, title2, image2 = get_recipe(url2)
    url3, page3, line3 = get_page(food)
    ingred3, steps3, title3, image3 = get_recipe(url3)
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    # инлайн-кнопки с рецептами, которые можно выбрать
    btns.append(types.InlineKeyboardButton(text=title1, callback_data='{food}/{page}/{line}'.format(food=food, page=page1, line=line1)))
    btns.append(types.InlineKeyboardButton(text=title2, callback_data='{food}/{page}/{line}'.format(food=food, page=page2, line=line2)))
    btns.append(types.InlineKeyboardButton(text=title3, callback_data='{food}/{page}/{line}'.format(food=food, page=page3, line=line3)))
    keyboard.add(*btns)
    bot.send_message(m.chat.id, "Мы нашли кое-что для вас, выберите наиболее подходящий вариант", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda c:True)
def inline(c):
    food, page, line = c.data.split('/')
    url = 'http://www.gastronom.ru/search/type/recipe/?t=&title={food}&page={page}'.format(food=food, page=page)
    response = requests.get(url)
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html5lib')
    lis = soup.find_all("article", class_="article col-sm-4 col-ms-6 ")
    recipe_href = []
    k = 0
    for j in lis:
        jj = j.find("a", class_="img full myFix")
        recipes = str(jj).split('"')
        for i in recipes:
            if re.findall('recipe', i):
                recipe_href.append(i)
                k += 1
    url = 'http://www.gastronom.ru' + recipe_href[int(line)]
    ingreds, steps, title, image = get_recipe(url)
    resp, stps = get_recipe_view(ingreds, steps, title)
    bot.send_photo(c.message.chat.id, image)
    bot.send_message(c.message.chat.id, resp, parse_mode='HTML')
    step = 1
    for i in steps:
        r = "<i>Шаг " + str(step) + ":</i>" + i
        bot.send_message(c.message.chat.id, r, parse_mode='HTML')
        step += 1


@bot.message_handler(commands=['start'])
def start(m):
    number = random.randint(0, 5)
    images = ['https://t4.ftcdn.net/jpg/00/70/38/17/240_F_70381792_QXu7w94kyMElcqxAeWsEfoyhzOl6rII8.jpg',
              'http://www.destiny.ru/uploads/posts/2014-03/1396088239_obed.jpg',
              'http://telegraf.com.ua/files/2013/03/zavtrak_eda-320x200.jpg',
              'https://img3.badfon.ru/original/1280x1024/4/3f/kurica-pischa-pir-yagody-tarelki.jpg',
              'http://www.gorod59.ru/uploads/iboard/19id7546099.jpg',
              'http://forums.realax.ru/saveimages/2016/09/29/emzqrunfd9yltgahs.jpg']

    bot.send_photo(m.chat.id, images[number])
    bot.send_message(m.chat.id, hello_message, parse_mode='HTML')


if __name__ == '__main__':
    bot.polling(none_stop=True)