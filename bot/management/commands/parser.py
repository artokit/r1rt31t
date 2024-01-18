from selenium import webdriver
import time
from bot.models import Comment
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://kaifshop.biz")
input("Войдите в аккаунт: ")
for i in range(140):
    driver.get(f'https://kaifshop.biz/rating?page={i}')
    time.sleep(3)

    for elem in driver.find_elements(By.CLASS_NAME, 'review'):
        nickname = elem.find_element(By.CLASS_NAME, 'username').text.strip()
        footer = elem.find_element(By.CSS_SELECTOR, '.review__footer.flex-align-center')
        city = footer.find_element(By.CLASS_NAME, 'ml-auto').text.strip()
        date = footer.text.replace(city, '').strip()
        stars_count = len(elem.find_elements(By.CSS_SELECTOR, '.fa.fa-star'))
        product = elem.find_element(By.CSS_SELECTOR, '.mb-1.flex-align-center').text.replace('Товар:', '').strip()
        content = elem.find_element(By.CSS_SELECTOR, '.review__text').text.strip()
        print(f"Страница: {i}")
        print(
            f"{product}\n"
            f"{nickname} {date}\n"
            f"Оценка: {stars_count}\n"
            f"{content}\n\n"
        )

        if Comment.objects.filter(content=content):
            print("Такой товар уже есть :(")
            continue

        c = Comment(
            nickname=nickname,
            date=date,
            content=content,
            count_of_stars=stars_count,
            name_of_product=product
        )
        c.save()
