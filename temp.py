import re

class Mir():
  '''
  classdocs
  '''

  def __init__(self, srcfile):
    self.srcf = srcfile
    self.dstf = 'extract.txt'
    self.data = ''
    self.flag = False

  def extract(seft):
    f_read = open(self.srcf, 'r')
    f_save = open(self.dstf, 'w')

    for line in f_read.readlines():
      match = re.search(r'^\~.*([A-Z][A-Z])$')
      if match:
        data = data + line + '\n'
        print(data)

    f_save.write(data)
    f_save.close()

def main():
  mir = Mir('mir.txt')
  mir.extract

if __name__ == '__main__':
  main()




