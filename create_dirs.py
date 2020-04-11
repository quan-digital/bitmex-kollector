import os 
 
try:
    # Create target directories
    os.mkdir('data')
    os.mkdir('data/ws')
    os.mkdir('data/error')
    os.mkdir('data/execution')
    os.mkdir('data/liquidation')
    os.mkdir('data/chat')

except FileExistsError:
    print("Directories already exist")