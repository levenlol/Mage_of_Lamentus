@echo off
call "./.venv/Scripts/activate.bat"

call python -m src.card_adder
call update_prices.bat