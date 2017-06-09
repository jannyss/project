from aiotg import Bot
from bs4 import BeautifulSoup
import re
import requests
import random


bot = Bot(api_token="198167022:AAGAsVWecf6y_Ul3e9BdleEirSxbH6HI1xs")

hello_message = '<b>Добро пожаловать!</b>\n ' \
                'Я - бот для поиска очень вкусных рецептов самых разнообразных блюд. \n ' \
                '/help - если хотите узнать команды, которыми я владею'


help_message = '/recipe название_блюда  -  <b>поиск любого блюда</b> \n' \
               '/details название_блюда желаемые_ингредиенты исключаемые_ингредиенты сложность - <b>подробное описание нужного блюда</b> \n' \
               'Если вы не хотите задавать какой-то параметр, напишите на его месте <b> - </b>\n' \
               'Если рецепт вам не понравился, повторите команду и вам будет предложен другой вариант\n' \
               '/dayrecipe - Рецепт дня\n' \
               '/start - стартовая страница и информация о боте'


def get_page(food, iningr, exingr, diff):
    url = 'http://www.gastronom.ru/search/type/recipe/?t=&title={food}&iningr={iningr}&exingr={exingr}&diff={diff}'.\
        format(food=food, iningr=iningr, exingr=exingr, diff=diff)
    response = requests.get(url)
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html5lib')
    tags = soup.find("div", class_="tags")
    tags = tags.find("span", class_="big-tag big-tag__muted myFixTag").text.split(": ")
    if int(tags[1]) != 0:
        p = random.randint(1, int(tags[1]))
        page = p // 24
        url = 'http://www.gastronom.ru/search/type/recipe/?t=&title={food}&page={page}&iningr={iningr}&exingr={exingr}&diff={diff}'.\
            format(food=food, page=page, iningr=iningr, exingr=exingr, diff=diff)
        print(url)
        response = requests.get(url)
        web_page = response.text
        soup = BeautifulSoup(web_page, 'html5lib')
        lis = soup.find_all("article", class_="article col-sm-4 col-ms-6 ")
        recipe_href = []
        # k = 0
        for j in lis:
            jj = j.find("a", class_="img full myFix")
            recipes = str(jj).split('"')
            for i in recipes:
                if re.findall('recipe', i):
                    recipe_href.append(i)
                    # k += 1
        k = random.randint(0, len(recipe_href)-1)
        url = 'http://www.gastronom.ru' + recipe_href[k]
        return url, page, k

def recipe_of_the_day():
    url = 'http://www.gastronom.ru/'
    response = requests.get(url)
    web_page = response.text
    soup = BeautifulSoup(web_page, 'html5lib')
    page = soup.find("a", attrs={"class": "img cbg h220-320 lazy lazy-big"})
    print(page)
    # tags = page.find("span", class_="big-tag big-tag__muted myFixTag").text.split(": ")
    recipe_href = []
    recipes = str(page).split('"')
    for i in recipes:
        if re.findall('recipe', i):
            recipe_href.append(i)

    url = 'http://www.gastronom.ru' + recipe_href[0]
    return url


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


@bot.command("/recipe")
async def recipe(chat, match):
    _, food = chat.message["text"].split()
    try:
        url, page, line = get_page(food, '', '', '')
        ingreds, steps, title, image = get_recipe(url)
        resp, stps = get_recipe_view(ingreds, steps, title)
        await chat.send_photo(image)
        await chat.send_text(resp, parse_mode='HTML')
        await chat.send_text("<b>Порядок выполнения</b>", parse_mode='HTML')
        step = 1
        for i in steps:
            r = "<i>Шаг " + str(step) + ":</i>" + i
            await chat.send_text(r, parse_mode='HTML')
            step += 1
    except Exception:
        resp = "Подобных рецептов не найдено. <i>Попробуйте что-нибудь другое ;) </i>"
        await chat.send_text(resp, parse_mode='HTML')


@bot.command("start")
async def start(chat, match):
    number = random.randint(0, 5)
    images = ['https://t4.ftcdn.net/jpg/00/70/38/17/240_F_70381792_QXu7w94kyMElcqxAeWsEfoyhzOl6rII8.jpg',
              'http://www.destiny.ru/uploads/posts/2014-03/1396088239_obed.jpg',
              'http://telegraf.com.ua/files/2013/03/zavtrak_eda-320x200.jpg',
              'https://img3.badfon.ru/original/1280x1024/4/3f/kurica-pischa-pir-yagody-tarelki.jpg',
              'http://www.gorod59.ru/uploads/iboard/19id7546099.jpg',
              'http://forums.realax.ru/saveimages/2016/09/29/emzqrunfd9yltgahs.jpg']
    await chat.send_photo(images[number])
    await chat.send_text(hello_message, parse_mode='HTML')

# легко = 11, средне = 12, сложно = 13

@bot.command("details")
async def params(chat, match):
    _, food, good, bad, diff = chat.message["text"].split()
    print(food, good, bad, diff)

    if food == "-": food = ''
    if good == "-": good = ''
    if bad == "-": bad = ''
    if diff == "-": diff = ''
    if diff == "легко": diff = 11
    if diff == "средне": diff = 12
    if diff == "сложно": diff = 13
    print(food, good, bad, diff)
    try:
        url, page, line = get_page(food, good, bad, diff)
        ingreds, steps, title, image = get_recipe(url)
        resp, stps = get_recipe_view(ingreds, steps, title)
        await chat.send_photo(image)
        await chat.send_text(resp, parse_mode='HTML')
        await chat.send_text("<b>Порядок выполнения</b>", parse_mode='HTML')
        step = 1
        for i in steps:
            r = "<i>Шаг " + str(step) + ":</i>" + i
            await chat.send_text(r, parse_mode='HTML')
            step += 1
    except Exception:
        resp = "Подобных рецептов не найдено. <i>Попробуйте что-нибудь другое ;) </i>"
        await chat.send_text(resp, parse_mode='HTML')


@bot.command("help")
async def params(chat, match):
    await chat.send_text(help_message, parse_mode='HTML')


@bot.command("/dayrecipe")
async def dayrecipe(chat, match):
    url = recipe_of_the_day()
    ingreds, steps, title, image = get_recipe(url)
    resp, stps = get_recipe_view(ingreds, steps, title)
    await chat.send_photo(image)
    await chat.send_text(resp, parse_mode='HTML')
    await chat.send_text("<b>Порядок выполнения</b>", parse_mode='HTML')
    step = 1
    for i in steps:
        r = "<i>Шаг " + str(step) + ":</i>" + i
        await chat.send_text(r, parse_mode='HTML')
        step += 1


if __name__ == '__main__':
    bot.stop_webhook()
    bot.run(debug=True)
