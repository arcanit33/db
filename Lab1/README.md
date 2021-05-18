# Лабораторна робота No 1. Вивчення базових операцій обробки XML-документів

##  Виконав Нікітін Олександр Олександрович КП-81

14 варіант згідно номера у списку групи

| Базова сторінка (завдання 1) | Зміст завдання 2     | Адреса інтернет-магазину (завдання 3) |
|------------------------------|----------------------|---------------------------------------|
| www.stejka.com         | Вивести список гіперпосилань | www.mebli-lviv.com.ua |

## Лістинг коду

### Збирання даних зі сторінки www.stejka.com  

`src/scrapers/spiders/stejka.py`

```python
class StejkaSpider(scrapy.Spider):
    name = 'stejka'
    allowed_domains = ['stejka.com']
    start_urls = ['https://stejka.com/']

    def parse(self, response: Response):
        all_images = response.xpath("//div[@class='foto']/@style[starts-with(., 'background-image: url(/')]")
        all_text = response.xpath("//*[not(self::script)][not(self::style)][string-length(normalize-space(text())) > 30]/text()")
        yield {
            'url': response.url,
            'payload': [{'type': 'text', 'data': text.get().strip()} for text in all_text] +
                       [{'type': 'image', 'data': 'https://stejka.com' + image.get()[22:len(image.get())-2]} for image in all_images]
        }
        if response.url == self.start_urls[0]:
            all_links = response.xpath(
                "//a/@href[starts-with(., '/rus/')]")
            selected_links = ['https://stejka.com' + link.get() for link in all_links][:20]
            for link in selected_links:
                yield scrapy.Request(link, self.parse)

```

### Збирання даних зі сторінки www.mebli-lviv.com.ua

`src/scrapers/spiders/mebli.py`

```python
class MebliSpider(scrapy.Spider):
    name = 'mebli'
    allowed_domains = ['mebli-lviv.com.ua']
    start_urls = ['https://mebli-lviv.com.ua/ua/chairs/']

    def parse(self, response: Response):
        products = response.xpath("//div[contains(@class, 'product-block')]")[:19]
        for product in products:
            yield {
                'description': product.xpath(".//img[@class='img-responsive']/@title").get(),
                'price': product.xpath(".//span[@class='special-price']/text()").get(),
                'img': product.xpath(".//img[@class='img-responsive']/@src").get()
            }
```

### Запис зібраних даних до файлів

`src/scrapers/pipelines.py`

```python
class Lab1Sem2Pipeline(object):
    def __init__(self):
        self.root = None

    def open_spider(self, spider):
        self.root = etree.Element("data" if spider.name == "stejka" else "mebli")

    def close_spider(self, spider):
        with open('task%d.xml' % (1 if spider.name == "stejka" else 2), 'wb') as f:
            f.write(etree.tostring(self.root, encoding="UTF-8", pretty_print=True, xml_declaration=True))

    def process_item(self, item, spider):
        if spider.name == "stejka":
            page = etree.Element("page", url=item["url"])
            for payload in item["payload"]:
                fragment = etree.Element("fragment", type=payload["type"])
                fragment.text = payload["data"]
                page.append(fragment)
            self.root.append(page)
        else:
            product = etree.Element("product")
            desc = etree.Element("description")
            desc.text = item["description"]
            pr = etree.Element("price")
            pr.text = item["price"]
            img = etree.Element("image")
            img.text = item["img"]
            product.append(desc)
            product.append(pr)
            product.append(img)
            self.root.append(product)
        return item
```

### Завдання №1

`src/main.py`

```python
def task1():
    print("Task #1")
    root = etree.parse("task1.xml")
    pages = root.xpath("//page")
    print("Number of scrapped documents: %s" % len(pages))
    for page in pages:
        url = page.xpath("@url")[0]
        print("%s" % url)
```

### Завдання №2

`src/main.py`

```python
def task2():
    print("Task #2")
    transform = etree.XSLT(etree.parse("templateTask2.xsl"))
    result = transform(etree.parse("task2.xml"))
    result.write("task2.xhtml", pretty_print=True, encoding="UTF-8")
    webbrowser.open('file://' + os.path.realpath("task2.xhtml"))
```

`src/task2.xsl`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml">
    <xsl:output
        method="xml"
        doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"
        doctype-public="-//W3C//DTD XHTML 1.1//EN"
        indent="yes"
    />
    <xsl:template match="/">
        <html xml:lang="en">
            <head>
                <title>Task 2</title>
            </head>
            <body>
                <h1>Table of products:</h1>
                <xsl:apply-templates select="/mebli"/>
                <xsl:if test="count(/mebli/product) = 0">
                    <p>There are no products available</p>
                </xsl:if>
            </body>
        </html>
    </xsl:template>
    <xsl:template match="/mebli">
        <table border="1">
            <thead>
                <tr>
                    <td>Image</td>
                    <td>Description</td>
                    <td>Price, UAH</td>
                </tr>
            </thead>
            <tbody>
                <xsl:apply-templates select="/mebli/product"/>
            </tbody>
        </table>
    </xsl:template>
    <xsl:template match="/mebli/product">
        <tr>
            <td>
                 <xsl:apply-templates select="image"/>
            </td>
            <td>
                <xsl:apply-templates select="description"/>
            </td>
            <td>
                <xsl:apply-templates select="price"/>
            </td>
        </tr>
    </xsl:template>
    <xsl:template match="image">
        <img alt="image of product">
            <xsl:attribute name="src">
                <xsl:value-of select="text()"/>
            </xsl:attribute>
        </img>
    </xsl:template>
    <xsl:template match="price">
        <xsl:value-of select="text()"/>
    </xsl:template>
    <xsl:template match="description">
        <xsl:value-of select="text()"/>
    </xsl:template>
</xsl:stylesheet>

```

## Лістинг згенерованих файлів

### task1.xml

```xml
<?xml version='1.0' encoding='UTF-8'?>
<data>
  <page url="https://stejka.com/">
    <fragment type="text">Stejka - туристический портал Украины. Путешествия, достопримечательности, отели, гостиницы, рестораны, такси.</fragment>
    <fragment type="text">Добро пожаловать в наш ресторанно-гостиничный комплекс "35км"! Отель расположен в самом начале города Борисполь, если заезжать со стороны Киева Гостиница...</fragment>
    <fragment type="text">Туристична фірма "Смак Пригод". Ми пропонуємо широкий асортимент курортів, готельна база яких який постійно оновлюється, а якість відпочинку невпинно покращується. .  ...</fragment>
    <fragment type="text">Такси Попутка - все пассажирские перевозки в городе Киев, а также области.Актуальные рассценки - на посадку, за километр по городу и за его пределами.Встреча с...</fragment>
    <fragment type="text">Доверяйте свой отдых профессионалам. Туристическое агентство «Воля Тревел»организует Ваш отпуск с визита в офис и до его окончания, а именно посадки в Одессе.Помимо...</fragment>
    <fragment type="text">Услуги Star Taxi ценяться пассажирами и используются давно и успешно. Высокий уровень обслуживания и профессионализм</fragment>
    <fragment type="text">водителей могут широко использоваться при организации...</fragment>
    <fragment type="text">Идеально подходит для размещения организованых груп. Здание отдельное, большая охраняемая парковка. В здании расположено кафе, комплекс расположен...</fragment>
    <fragment type="text">«Cтильная, изысканная 2 к кв люкс посуточно,документы»</fragment>
    <fragment type="text">Предлагаем для проживания 2-х комнатную квартиру, в которой Вы сможете почувствовать домашний уют и комфорт. Неповторимый имидж квартиры, придает ей яркую индивидуальность...</fragment>
    <fragment type="text">Туристическое агентство «Sunny Travel» c радостью поможем туристам отправиться в любую точку мира. Наша задача сделать Ваше путешествие приятным и ярким!Мы ознакомим...</fragment>
    <fragment type="text">Гостиничный комплекс «Панська хата» приглашает отдохнуть в одном из самых красивых мест Полтавской области Великой Багачке на берегу реки Псёл.У нас Вы сможете...</fragment>
    <fragment type="text">Каменец-Подольский и не только...Тематические турыЭкскурсионное сопровождение (украинский, немецкий, русский, польский...)Экскурсионные программы: исторические...</fragment>
    <fragment type="text">отчет «Что посмотреть в Ужгороде за 4 дня кроме сакуры?»</fragment>
    <fragment type="text">Давно хотели поехать в Ужгород на цветение сакуры. Но все знакомые говорили, что несколько дней там делать нечего, все посмотришь за один день. Добираться двое суток, а потом через день уехать? Но охота пуще неволи и вот билеты куплены, хостел заказан, маршрут разработан. Я расскажу, что мы посмотрели в Ужгороде и его окрестностях...</fragment>
    <fragment type="text">отчет «Что делать в Крыму зимой»</fragment>
    <fragment type="text">Вопреки расхожему мнению, туристическая жизнь в Крыму не замирает даже зимой. Чтобы читатель мог в полной мере оценить преимущества зимнего Крыма, мы расскажем, какие достопримечательности полуострова открыты зимой и чем там можно заняться.</fragment>
    <fragment type="text">отчет «Чудеса природы-самые большие приливы в Европе»</fragment>
    <fragment type="text">На северо-западе Франции, на берегу Ла-Манша ( или как раньше его называли - Английского канала ) расположен небольшой город Сен-Мало. Город находится практически на острове - только узкая полоска суши соединяет его с материковой частью, там, на материке находится уже современный город, но интересен, конечно, старинный, на острове...</fragment>
    <fragment type="text">отчет «Клод Моне - живые картины»</fragment>
    <fragment type="text">Клод Моне родился 14 ноября 1840 года в Париже, умер 5 декабря 1926 года в Живерни.Когда мальчику было 5 лет, семья переехала в Гавр - там и проходит юность художника.Отец Моне был бакалейщиком и хотел, чтобы сын продолжил семейное дело. Однако, это дело было ему совсем не по душе - учился он очень плохо и неохотно - бродяжничал и занимался...</fragment>
    <fragment type="text">С чего же начать?...Наверное, все-таки с признания в любви! Франция действительно покорила и завоевала наши сердца.Поехали во Францию только по настоянию дочери - она там бывала несколько раз и очень восхищалась. Мы к этим восхищениям относились достаточно скептично, но....Действительность потрясла и превзошла все наши ожидания.О...</fragment>
    <fragment type="text">отчет «Поездка в Грузию: Батуми»</fragment>
    <fragment type="text">За последние несколько лет Батуми превратился в популярнейший среди туристов город и ведь не зря…  При  подъезде  открывается красивенный вид на город – подумалось что Батуми это Нью-Йорк в миниатюре. В Батуми мы ехали из Тбилиси, путь не близкий, 7-8 часов в маршрутке (проезд стоит 20 лари=11$=130 грн).  Благодаря...</fragment>
    <fragment type="text">Вітаємо всіх і ласкаво просимо до компанії Avants Loan INC. Ми - команда фінансової підтримки, яка займається міжнародними...</fragment>
    <fragment type="text">Что может быть лучше баньки в выходной день? Только банька с девчонками)))</fragment>
    <fragment type="text">В отеле предоставляются интимные услуги...</fragment>
    <fragment type="text">Хто в Жашкові відповідає за боротьбу з короновірусом</fragment>
    <fragment type="text">Часто слышал от своих знакомых, вернувшихся с летнего...</fragment>
    <fragment type="text">Чернигов - один из старейших городов Украины, второй по...</fragment>
    <fragment type="text">Как-то так случилось, что свое двадцать третье День Рождения...</fragment>
    <fragment type="text">Миниатюрный городок (4 тыс. жителей), затерявшийся в лесах...</fragment>
    <fragment type="text">Вопреки расхожему мнению, туристическая жизнь в Крыму...</fragment>
    <fragment type="text">Письменные и графические материалы защищены авторским правом законодательства Украины, перепечатка материалов разрешена только с письменного соглашения владельца</fragment>
    <fragment type="text">Юридическая поддержка агентство "Солби"</fragment>
    <fragment type="text">Туристический портал Украины Stejka.com: Туризм, путешествия, отдых. Отели, гостиницы, рестораны. Достопримечательности, замки, крепости, руины, парки, музеи, церкви, интересные места, горнолыжные курорты. База такси, каталог турфирм по всем городам Украины. Бронирование отелей по Украине и всему миру. Отдых в Крыму, Карпатах. Рейтинги лучших достопримечательностей, городов, замков и горнолыжных курортов, а также отчеты туристов. Последние туристические новости со всех уголков мира. Окунись в приключения!</fragment>
    <fragment type="text">Регистрация займёт у вас не более 15 секунд!</fragment>
    <fragment type="text">Введите ваш e-mail, на него будет отправленна ссылка для восстановления пароля.</fragment>
    <fragment type="image">https://stejka.com/cache/600_400_min/4to_posmotret_v_ujgorode_za_4_dnja_krome_4.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/600_400_min/asrcetv5fn.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/600_400_min/4udesa_prirodysamye_bolwie_prilivy_v_mir_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/600_400_min/klod_mone__jivye_kartiny_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/600_400_min/sobory_francii_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/600_400_min/poezdka_v_gruziju_batumi_1.JPG</fragment>
  </page>
  <page url="https://stejka.com/rus/kievskaja/">
    <fragment type="text">Фотоотчеты туристов о Украине и не только</fragment>
    <fragment type="text">«Гострі Говди» -  острые скалы подземного мира</fragment>
    <fragment type="text">Дрогобыч - нефтяной Дубай Украины :)</fragment>
    <fragment type="text">Вітаємо всіх і ласкаво просимо до компанії Avants Loan INC. Ми - команда фінансової підтримки, яка займається міжнародними...</fragment>
    <fragment type="text">Что может быть лучше баньки в выходной день? Только банька с девчонками)))</fragment>
    <fragment type="text">В отеле предоставляются интимные услуги...</fragment>
    <fragment type="text">Хто в Жашкові відповідає за боротьбу з короновірусом</fragment>
    <fragment type="text">Бытует мнение, что в восточной Украине смотреть совершенно...</fragment>
    <fragment type="text">Мыс Фиолент это довольно интересное место. С одной точки...</fragment>
    <fragment type="text">«Достопримечательности Дрогобыча»</fragment>
    <fragment type="text">Из всей временно оккупированной Галиции австро-венграм...</fragment>
    <fragment type="text">«Страусиная ферма недалеко от Керчи»</fragment>
    <fragment type="text">Летом пару раз с гостями побывала на страусиной ферме...</fragment>
    <fragment type="text">«Вилково. Староверы и дельта Дуная»</fragment>
    <fragment type="text">Кажется, такого странного города я не видел ни до, ни (пока...</fragment>
    <fragment type="text">Письменные и графические материалы защищены авторским правом законодательства Украины, перепечатка материалов разрешена только с письменного соглашения владельца</fragment>
    <fragment type="text">Юридическая поддержка агентство "Солби"</fragment>
    <fragment type="text">Регистрация займёт у вас не более 15 секунд!</fragment>
    <fragment type="text">Введите ваш e-mail, на него будет отправленна ссылка для восстановления пароля.</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/balykowu4inka_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/belaja_cerkov_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/berezan_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/boguslav_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/borispol_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/borodjanka_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/borwev1_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/brovary_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/bu4a_2.JPG</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/vasilkov_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/vorzel_4.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/vywgorod_2.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/irpen_8.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/kagarlyk_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/kiev_2.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/kon4azaspa_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/ljutej_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/nemewaevo_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/obuxov_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/perejaslav__xmelnickiy_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/puwavodica_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/rakitnoe_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/rjiwev_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/skvira_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/fastov_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_100_min/jagotin_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_90_min/na_styke_trjox_kultur_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_90_min/gostr_govdi___ostrye_skaly_podzemnogo_mira_1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_90_min/drogoby4__neftjanoy_dubay_ukrainy__1.jpg</fragment>
    <fragment type="image">https://stejka.com/cache/150_90_min/fa4jsmekyk.jpg</fragment>
  </page>
    ...
```

### task2.xml

```xml
<?xml version='1.0' encoding='UTF-8'?>
<mebli>
  <product>
    <description>Стілець CORNELIO</description>
    <price>2.543грн</price>
    <image>https://mebli-lviv.com.ua/image/cache//catalog/products/halmar/stiltsi-halmar/cornelio-stilets-halmar-200x200.jpg</image>
  </product>
  <product>
    <description>Стілець EMILIO</description>
    <price>2.156грн</price>
    <image>https://mebli-lviv.com.ua/image/cache//catalog/products/halmar/stiltsi-halmar/emilio-stilets-halmar-200x200.jpg</image>
  </product>
  <product>
    <description>Стілець MATTEO</description>
    <price>2.747грн</price>
    <image>https://mebli-lviv.com.ua/image/cache//catalog/products/halmar/stiltsi-halmar/matteo-stilets-halmar-200x200.jpg</image>
  </product>
  <product>
    <description>Стілець PAOLO</description>
    <price>2.448грн</price>
    <image>https://mebli-lviv.com.ua/image/cache//catalog/products/halmar/stiltsi-halmar/paolo-stilets-halmar-200x200.jpg</image>
  </product>
  <product>
    <description>Стілець PEPPI</description>
    <price>1.469грн</price>
    <image>https://mebli-lviv.com.ua/image/cache//catalog/products/halmar/stiltsi-halmar/peppi-kremowy-stilets-halmar-200x200.jpg</image>
  </product>
    ...
```

### task2.xhtml

```xhtml
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <title>Task 2</title>
  </head>
  <body>
    <h1>Table of products:</h1>
    <table border="1">
      <thead>
        <tr>
          <td>Image</td>
          <td>Description</td>
          <td>Price, UAH</td>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <img alt="image of product" src="https://mebli-lviv.com.ua/image/cache//catalog/products/halmar/stiltsi-halmar/cornelio-stilets-halmar-200x200.jpg"/>
          </td>
          <td>Стілець CORNELIO</td>
          <td>2.543грн</td>
        </tr>
        <tr>
          <td>
            <img alt="image of product" src="https://mebli-lviv.com.ua/image/cache//catalog/products/halmar/stiltsi-halmar/emilio-stilets-halmar-200x200.jpg"/>
          </td>
          <td>Стілець EMILIO</td>
          <td>2.156грн</td>
        </tr>
        <tr>
          <td>
            <img alt="image of product" src="https://mebli-lviv.com.ua/image/cache//catalog/products/halmar/stiltsi-halmar/matteo-stilets-halmar-200x200.jpg"/>
          </td>
          <td>Стілець MATTEO</td>
          <td>2.747грн</td>
        </tr>
    ...
```

## Приклади роботи програми

![lab](1.png)

![lab](2.png)

![lab](3.png)
