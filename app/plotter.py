# plotter.py
"""
Генерация графика с трендом прохождения/провалов тестов
"""
import matplotlib.pyplot as plt
import os
import random

def generate_trend_plot(team: str) -> str:
    """
    Создание графика тренда прохождения и провалов тестов по отчетам
    """
    # Для демонстрации создаем фиктивные данные
    reports = ["Отчет 1", "Отчет 2", "Текущий"]
    passed = [random.randint(80, 100) for _ in reports]
    failed = [random.randint(0, 20) for _ in reports]

    plt.figure(figsize=(6, 4))
    plt.plot(reports, passed, label='Passed', marker='o')
    plt.plot(reports, failed, label='Failed', marker='x')
    plt.title(f"Динамика статусов тестов: {team}")
    plt.xlabel("Запуски")
    plt.ylabel("Кол-во тестов")
    plt.legend()
    plt.tight_layout()
    
    path = f"charts/{team}_trend.png"
    os.makedirs("charts", exist_ok=True)
    plt.savefig(path)
    plt.close()
    return path
