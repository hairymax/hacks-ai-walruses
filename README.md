# hacks-ai-walruses

## Хакатон "Цифровой прорыв"

Кейс. "**ИИ на страже популяции ненецких моржей**". Хабаровск, 2022.05.27-29
Команда **PytBools**

## Запуск обучения 
Обучение нейросети для детекции и сегментации проводилось на colab pro c использованием фреймворка MMDetection    
train_mask_rcnn.ipynb

## Установка зависимостей
в файле requirements.txt находится список необходимых библиотек   
Описание устновки mmdetection и mmcv можно найти на офциальном сайте   
https://mmdetection.readthedocs.io/en/v2.21.0/get_started.html

## Веса обученной нейросети
https://drive.google.com/file/d/1-GD7yanzZ3HfQ0flyqG50GRfNUemwVjY/view?usp=sharing

## Запуск вебинтерфейса
```sh
python3 app/app.py
```
## Пример работа вебинтерфейса
https://drive.google.com/file/d/1P2IDwXN5JdZkW8l5CHhEcZNk1K8kdCu6/view?usp=sharing
Предсказание модели выполняется на CPU, поскольку по условию задания необходимо, чтобы решение работало на ноутбуке без видеокарты

## Решение
Решение команды Pytbools на тестовых изображениях представлен в файле pytbools.zip
