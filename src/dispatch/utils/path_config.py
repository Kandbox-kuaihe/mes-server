import os  
path = os.path.abspath(os.path.dirname(__file__))
DISPATCH_PATH = os.path.dirname(path)
ROOT_PATH  = os.path.dirname(os.path.dirname(DISPATCH_PATH))
# ROOT_PATH='/Users/nipanbo/Pictures/easydispatch/easydispatch' 
# DISPATCH_PATH='/Users/nipanbo/Pictures/easydispatch/easydispatch/src/dispatch'


if __name__ == "__main__":
    print(f"{ROOT_PATH=} \n {DISPATCH_PATH=}")
    
    