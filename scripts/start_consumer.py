import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cdc.consumer import start_consumer

if __name__ == "__main__":
    start_consumer()
    print("consumidor iniciado")
