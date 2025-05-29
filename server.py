from telegram.ext import Application, MessageHandler, filters
from config import Token_for_Bot

def main():
    aplication = Application.builder().token(Token_for_Bot).build()
    
    
if __name__ == "__main__":
    main()