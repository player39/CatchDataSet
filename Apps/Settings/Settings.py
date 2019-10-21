
import os


# strRootPath = os.path.abspath(os.path.join(os.getcwd(), '../..'))
strRootPath = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

print(strRootPath)