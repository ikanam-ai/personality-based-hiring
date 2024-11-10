<p align="center">
     <img src="extensions/views/logo.svg" alt="Логотип проекта" width="600" style="display: inline-block; vertical-align: middle; margin-right: 10px;"/><br/>
</p>


## Подбор кандидатов на вакансию по типу личности

Проект предназначен для разработки системы, которая использует искусственный интеллект для анализа видеовизиток кандидатов и сопоставления их типа личности с требованиями вакансий. Решение позволит работодателям находить наиболее подходящих кандидатов, а соискателям — анализировать свои видеовизитки на соответствие определенному типу личности.

## Описание

Современный рынок труда сталкивается с проблемой подбора кандидатов, чьи личные качества и профессиональные особенности соответствуют требованиям вакансий. Несоответствие типа личности кандидата и специфики профессии может привести к текучести кадров, а также увеличению расходов на поиск подходящих специалистов. В то же время многие кандидаты не уверены в своем карьерном пути. Разработка системы, которая будет использовать видеоанализ для оценки типа личности, поможет решать эти проблемы.

Проект включает:
- Модели для оценки типа личности по видеовизитке кандидата.
- Графический интерфейс для загрузки видеовизиток соискателями.
- Систему, которая сопоставляет тип личности кандидатов с требованиями вакансий.
- Метрики для оценки качества работы модели и лидерборд для участников.

## Минимальные требования сервера для ML части
- CPU: 2 ядра
- ОЗУ: 2 ГБ
- SSD/HDD: 10gb

## Установка

Для установки и запуска проекта используйте [Poetry](https://python-poetry.org/), чтобы управлять зависимостями и виртуальной средой.

### 1. Установите Poetry

Если у вас еще не установлен Poetry, выполните следующую команду для его установки:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Клонируйте репозиторий

Клонируйте репозиторий проекта:

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

### 3. Установите зависимости

Используйте Poetry для установки всех зависимостей:

```bash
poetry install
```

### 4. Активируйте виртуальную среду

Запустите виртуальную среду, чтобы работать с проектом:

```bash
poetry shell
```

## Screencast

https://github.com/user-attachments/assets/3778f3e1-7410-4cbe-a873-70f484fd392f








## Использование

### Для соискателей: 

Загрузите свою видеовизитку на платформу, чтобы система оценила ваш тип личности и предложила рекомендации по карьерному пути.

### Для работодателей: 

Загрузите архив видеовизиток, чтобы система предложила наиболее подходящих кандидатов, соответствующих типу личности и требованиям профессии.
