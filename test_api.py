import pytest
import requests
import random

# Тест для создания объявления (TC-1.1.1)
def test_create_item(base_url):
    payload = {
        "sellerID": 123456,
        "name": "Test Item",
        "price": 1000
    }
    response = requests.post(f"{base_url}/item", json=payload)
    assert response.status_code == 200
    assert "status" in response.json()

# Тест для создания объявления с разными sellerID (TC-1.1.2)
def test_create_item_with_different_seller_ids(base_url):
    seller_ids = [111111, 555555, 999999]
    for seller_id in seller_ids:
        payload = {
            "sellerID": seller_id,
            "name": f"Item with sellerID {seller_id}",
            "price": 100
        }
        response = requests.post(f"{base_url}/item", json=payload)
        assert response.status_code == 200
        assert "status" in response.json()

# Тест для попытки создания объявления без обязательных полей (TC-1.2.1.1)
def test_create_item_missing_seller_id(base_url):
    payload = {
        "name": "Test Item",
        "price": 1000
    }
    response = requests.post(f"{base_url}/item", json=payload)
    assert response.status_code == 400
    assert "messages" in response.json()["result"]

# Тест для попытки создания объявления без обязательных полей (TC-1.2.1.2)
def test_create_item_missing_name(base_url):
    payload = {
       "sellerID": 111112,
       "price": 100
     }
    response = requests.post(f"{base_url}/item", json=payload)
    assert response.status_code == 400
    assert "messages" in response.json()["result"]

# Тест для попытки создания объявления без обязательных полей (TC-1.2.1.3)
def test_create_item_missing_price(base_url):
    payload =  {
       "sellerID": 111113,
       "name": "Neg_test Item"
     }
    response = requests.post(f"{base_url}/item", json=payload)
    assert response.status_code == 400
    assert "message" in response.json()

# Тест для попытки создания объявления с некорректным типом данных id (TC-1.2.2.1)
def test_create_item_invalid_id_type(base_url):
    payload = {
        "sellerID": "invalid_id",
        "name": "Test Item",
        "price": 1000
    }
    response = requests.post(f"{base_url}/item", json=payload)
    assert response.status_code == 400
    assert "messages" in response.json()["result"]

# Тест для попытки создания объявления с некорректным типом данных name (TC-1.2.2,2)
def test_create_item_invalid_name_type(base_url):
    payload = {
        "sellerID": 1296548,
        "name": 1,
        "price": 1000
    }
    response = requests.post(f"{base_url}/item", json=payload)
    assert response.status_code == 400
    assert "messages" in response.json()["result"]

# Тест для попытки создания объявления с некорректным типом данных name (TC-1.2.2,3)
def test_create_item_invalid_price_type(base_url):
    payload = {
        "sellerID": 1296548,
        "name": "Valid Name",
        "price": "invalid price"
    }
    response = requests.post(f"{base_url}/item", json=payload)
    assert response.status_code == 400
    assert "messages" in response.json()["result"]

# Тест для получения объявления по ID (TC-2.1.1)

def test_get_item_by_id(base_url):
    # 1. Создаем объявление через POST-запрос
    create_payload = {
        "sellerID": 789012,
        "name": "Test Item for GET",
        "price": 750
    }
    create_response = requests.post(f"{base_url}/item", json=create_payload)
    # Проверяем успешное создание
    assert create_response.status_code == 200
    assert "status" in create_response.json()

    # 2. Извлекаем ID из поля status (формат: "Сохранили объявление - <UUID>")
    status_message = create_response.json()["status"]
    item_id = status_message.split(" - ")[-1]

    # 3. Получаем объявление по извлеченному ID
    get_response = requests.get(f"{base_url}/item/{item_id}")

    # 4. Проверяем ответ
    assert get_response.status_code == 200

    response_data = get_response.json()

    # 5. Проверка структуры ответа согласно swagger.yaml
    assert isinstance(response_data, list)
    assert len(response_data) > 0

    item_data = response_data[0]

    # Обязательные поля из документации
    required_fields = [
        "id",
        "sellerId",
        "name",
        "price",
        "statistics"
    ]

    for field in required_fields:
        assert field in item_data, f"Отсутствует обязательное поле {field}"

    # Проверка соответствия данных
    assert item_data["id"] == item_id
    assert item_data["name"] == create_payload["name"]
    assert item_data["price"] == create_payload["price"]

    # Проверка статистики
    stats = item_data["statistics"]
    assert isinstance(stats, dict)
    assert all(key in stats for key in ["likes", "viewCount", "contacts"])

# Тест для попытки получения несуществующего объявления (TC-2.2.1)
def test_get_nonexistent_item(base_url):
    item_id = "nonexistent_id"
    response = requests.get(f"{base_url}/item/{item_id}")
    assert response.status_code == 404
    assert "message" in response.json()["result"]
# По результатам предыдущего теста - дополнительный тест с указанием id в формате UUID
def test_get_nonexistent_right_format(base_url):
    item_id = "00000000-0000-0000-0000-000000000000"
    response = requests.get(f"{base_url}/item/{item_id}")
    assert response.status_code == 404
    assert "message" in response.json()["result"]


# Получение всех объявлений по идентификатору продавца (TC-3.1)
# Проверка успешного статуса ответа (TC-3.1.1)

def test_get_items_response_structure(base_url):
    seller_id = 789012
    response = requests.get(f"{base_url}/{seller_id}/item")
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0

# Проверка соответствия sellerID (TC-3.1.2)
def test_items_seller_id_match(base_url):
    seller_id = 789012
    response = requests.get(f"{base_url}/{seller_id}/item")
    response_data = response.json()
    for item in response_data:
        assert item["sellerId"] == seller_id, f"Неверный sellerId в объявлении {item['id']}"

#  Проверка наличия обязательных полей (TC-3.1.4)
def test_items_have_required_fields(base_url):
    seller_id = 789012
    response = requests.get(f"{base_url}/{seller_id}/item")
    response_data = response.json()
    for item in response_data:
        assert "id" in item
        assert "name" in item
        assert "price" in item
        assert "statistics" in item

# Проверка структуры статистики (TC-3.1.5)
def test_items_statistics_structure(base_url):
    seller_id = 789012
    response = requests.get(f"{base_url}/{seller_id}/item")
    response_data = response.json()
    for item in response_data:
        stats = item["statistics"]
        assert "likes" in stats
        assert "viewCount" in stats

# Тест для попытки получения объявлений для несуществующего sellerID (TC-3.2.1)
def test_get_items_nonexistent_seller_id(base_url):
    # Генерируем случайный sellerID в допустимом диапазоне
    nonexistent_seller_id = random.randint(111111, 999999)

    # 2. Проверяем наличие объявлений для этого sellerID
    max_attempts = 5
    for _ in range(max_attempts):
        response = requests.get(f"{base_url}/{nonexistent_seller_id}/item")
        if response.status_code == 200 and len(response.json()) == 0:
            break

        nonexistent_seller_id = random.randint(111111, 999999)
    else:
        pytest.skip("Не удалось найти свободный sellerID после 5 попыток")

    # Проверяем ожидаемый статус
    response = requests.get(f"{base_url}/{nonexistent_seller_id}/item")

    # Если статус 200, но список объявлений пуст - это ожидаемое поведение
    if response.status_code == 200:
        items = response.json()
        assert isinstance(items, list)
        assert len(items) == 0

    # Если статус 404 - проверяем сообщение
    elif response.status_code == 404:
        assert "message" in response.json()

    # 5. Если получен неожиданный статус - тест падает
    else:
        pytest.fail(f"Неожиданный статус: {response.status_code}")
# Попытка получения объявлений с некорректным форматом sellerID (TC-3.2.2)
def test_get_item_invalid_sellerid(base_url):
    seller_id = "invalid_sellerid_type"
    response = requests.get(f"{base_url}/{seller_id}/item")
    assert response.status_code == 400
    assert "message" in response.json()["result"]

# Тест для получения статистики по объявлению (TC-4.1.1)
def test_get_statistics_by_item_id(base_url):
    item_id = "34553ac8-4b07-404c-8ea3-c284c24a59a9"  # Замените на реальный ID
    response = requests.get(f"{base_url}/statistic/{item_id}")
    assert response.status_code == 200
    assert "likes" in response.json()[0]
    assert "viewCount" in response.json()[0]
    assert "contacts" in response.json()[0]

# Тест для попытки получения статистики для несуществующего объявления (формат id - не UUID) (TC-4.2.1)
def test_get_statistics_nonexistent_item(base_url):
    item_id = "nonexistent-id"
    response = requests.get(f"{base_url}/statistic/{item_id}")
    assert response.status_code == 404
    assert "message" in response.json()['result']

def test_get_statistics_nonexistent_uuiditem(base_url):
    # Валидный UUID, но несуществующий
    item_id = "00000000-0000-0000-0000-000000000000"
    response = requests.get(f"{base_url}/statistic/{item_id}")
    assert response.status_code == 404
    assert "message" in response.json()['result']