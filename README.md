# hacks-ai-walruses

## Хакатон "Цифровой прорыв"

Кейс: ["**ИИ на страже популяции ненецких моржей**". Хабаровск, 2022.05.27-29](https://hacks-ai.ru/hackathons/755853)  
Команда **PytBools**:
- Алёшин Максим [hairymax](https://github.com/hairymax)
- Владимир Хомяков [rozendetr](https://github.com/rozendetr)
- Александр Белозёров [Belka8](https://github.com/Belka8)  

## Запуск обучения 
Обучение нейросети для детекции и сегментации проводилось в Google Colab pro c использованием фреймворка MMDetection    
`train_mask_rcnn.ipynb`

## Установка зависимостей
В файле requirements.txt находится список необходимых библиотек   
Описание устновки mmdetection и mmcv можно найти на офциальном сайте   
https://mmdetection.readthedocs.io/en/v2.21.0/get_started.html

## Веса обученной нейросети
https://drive.google.com/file/d/1-GD7yanzZ3HfQ0flyqG50GRfNUemwVjY/view?usp=sharing

## Запуск вебинтерфейса
```sh
python3 app/app.py
```
## Пример работа вебинтерфейса

https://user-images.githubusercontent.com/6792913/184539582-e10484ea-36e9-4be6-8ca1-fe1d5c1843f7.mp4

## Сертификат
[hacks-ai-certificate.pdf](https://github.com/hairymax/hacks-ai-walruses/files/9333488/hacks-ai-certificate.pdf)

## Решение
Решение команды Pytbools на тестовых изображениях представлен в файле pytbools.zip
