# acoGO Home Assistant Integration

Интеграция для Home Assistant для управления воротами через API acoGO.

## Установка

### Через HACS (рекомендуется)

1. Убедитесь, что HACS установлен в вашем Home Assistant
2. Добавьте этот репозиторий как пользовательский репозиторий в HACS
3. Найдите "acoGO Gate Control" в HACS и установите
4. Перезапустите Home Assistant

### Ручная установка

1. Скопируйте папку `custom_components/acogo` в папку `custom_components` вашего Home Assistant
2. Перезапустите Home Assistant

## Настройка

1. Перейдите в **Настройки** → **Устройства и службы**
2. Нажмите **Добавить интеграцию**
3. Найдите **acoGO Gate Control**
4. Введите ваш email и пароль от аккаунта acoGO
5. Интеграция автоматически найдет доступные устройства

## Использование

После настройки интеграции в Home Assistant появятся:

- Кнопки для открытия ворот для каждого найденного устройства
- Каждое устройство будет иметь уникальный идентификатор (devId)

### Автоматизация

Вы можете использовать кнопки в автоматизациях:

```yaml
automation:
  - alias: 'Открыть ворота по расписанию'
    trigger:
      - platform: time
        at: '07:00:00'
    action:
      - service: button.press
        target:
          entity_id: button.acogo_01_01_26_79_open_gate
```

## Функциональность

- **Авторизация**: Безопасное хранение учетных данных
- **Автоматическое обнаружение**: Находит все доступные устройства
- **Повторная авторизация**: Автоматически обновляет токены при необходимости
- **Уникальные ID**: Каждая установка имеет уникальный device ID
- **Логирование**: Подробные логи для отладки

## Поддержка

При возникновении проблем:

1. Проверьте логи Home Assistant
2. Убедитесь в правильности учетных данных
3. Создайте issue в этом репозитории с описанием проблемы
