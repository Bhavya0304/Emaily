from dotenv import load_dotenv
import os


def Load():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.join(current_dir,"../",".env")
    load_dotenv(dotenv_path=current_dir)