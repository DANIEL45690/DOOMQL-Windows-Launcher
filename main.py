#!/usr/bin/env python3
"""
DOOMQL One-File Launcher for Windows - By @concole_hack
Запустите этот файл двойным кликом!
"""

import sys
import os
import subprocess
import time
import json
import sqlite3
from pathlib import Path


def main():
    print("🎮 DOOMQL Windows Launcher")
    print("=" * 50)

    # Проверяем Python
    print("\n[1/4] Checking Python...")
    try:
        import psycopg2

        print("✅ psycopg2 installed")
    except:
        print("Installing psycopg2-binary...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"]
        )

    # Проверяем Docker
    print("\n[2/4] Checking Docker...")
    docker_available = False
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.split(',')[0]}")
            docker_available = True
        else:
            print("❌ Docker not running")
    except:
        print("❌ Docker not installed")

    # Если Docker не доступен, используем SQLite
    if not docker_available:
        print("\n⚠️  Docker not available, using SQLite fallback")
        return run_sqlite_version()

    # Запускаем базу данных
    print("\n[3/4] Starting database...")
    try:
        # Останавливаем старые контейнеры
        subprocess.run(["docker", "stop", "doomql_win"], capture_output=True)
        subprocess.run(["docker", "rm", "doomql_win"], capture_output=True)

        # Запускаем новый
        print("Starting PostgreSQL container...")
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "doomql_win",
                "-p",
                "5432:5432",
                "-e",
                "POSTGRES_PASSWORD=postgres",
                "postgres:latest",
            ],
            check=True,
        )

        print("⏳ Waiting for database... (10 seconds)")
        time.sleep(10)

    except Exception as e:
        print(f"❌ Docker error: {e}")
        print("\nFalling back to SQLite...")
        return run_sqlite_version()

    # Запускаем игру
    print("\n[4/4] Starting game...")
    run_postgresql_game()


def run_sqlite_version():
    """SQLite версия без Docker"""
    print("\n" + "=" * 50)
    print("🎮 DOOMQL SQLITE VERSION")
    print("=" * 50)

    # Создаем базу
    conn = sqlite3.connect("doomql_game.db")
    cur = conn.cursor()

    # Создаем таблицы
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS game_state (
        player_id INTEGER PRIMARY KEY,
        player_name TEXT,
        x REAL DEFAULT 4.0,
        y REAL DEFAULT 4.0,
        dir REAL DEFAULT 0.0,
        hp INTEGER DEFAULT 100
    )
    """
    )

    # Добавляем игрока
    player_name = input("Enter player name: ") or "Player1"
    cur.execute(
        """
    INSERT OR REPLACE INTO game_state (player_id, player_name, x, y, dir, hp)
    VALUES (1, ?, 4.0, 4.0, 0.0, 100)
    """,
        (player_name,),
    )
    conn.commit()

    # Игровой цикл
    x, y = 4.0, 4.0
    hp = 100

    while True:
        os.system("cls" if os.name == "nt" else "clear")

        print(f"👤 Player: {player_name} | HP: {hp}")
        print(f"📍 Position: X={x:.1f}, Y={y:.1f}")
        print("\n" + "#" * 30)

        # Простая графика
        for gy in range(10):
            row = ""
            for gx in range(20):
                if gx == int(x) and gy == int(y):
                    row += "@"
                elif gx == 0 or gx == 19 or gy == 0 or gy == 9:
                    row += "#"
                else:
                    row += "."
            print(row)

        print("#" * 30)
        print("\nControls: W/A/S/D - Move, X - Shoot, Q - Quit")
        print("Cheats: H - Heal (+50 HP), T - Teleport")

        key = input("\nCommand: ").upper()

        if key == "Q":
            break
        elif key == "W":
            y = max(1, y - 1)
        elif key == "S":
            y = min(8, y + 1)
        elif key == "A":
            x = max(1, x - 1)
        elif key == "D":
            x = min(18, x + 1)
        elif key == "X":
            print("💥 Bang! You shot!")
            time.sleep(1)
        elif key == "H":
            hp = min(100, hp + 50)
            print("💚 Healed +50 HP!")
            time.sleep(1)
        elif key == "T":
            x, y = 10, 5
            print("✨ Teleported!")
            time.sleep(1)

        # Обновляем базу
        cur.execute(
            "UPDATE game_state SET x=?, y=?, hp=? WHERE player_id=1", (x, y, hp)
        )
        conn.commit()

    conn.close()
    print("\n👋 Game saved to doomql_game.db")


def run_postgresql_game():
    """PostgreSQL версия с Docker"""
    try:
        import psycopg2

        print("\nConnecting to PostgreSQL...")
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="postgres",
            user="postgres",
            password="postgres",
        )
        conn.autocommit = True
        cur = conn.cursor()

        print("✅ Connected!")
        print("\n🎮 Game would start here...")
        print("(Full game requires DOOMQL SQL files)")

        # Простая демонстрация
        cur.execute("SELECT version()")
        print(f"\nDatabase: {cur.fetchone()[0]}")

        input("\nPress Enter to exit...")
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        input("\nPress Enter to try SQLite version...")
        run_sqlite_version()


if __name__ == "__main__":
    # Для Windows - скрываем быстрое закрытие
    if os.name == "nt":
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n👋 Game stopped")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            input("\nPress Enter to exit...")
    else:
        main()
