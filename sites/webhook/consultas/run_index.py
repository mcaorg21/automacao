



class Rodar_Flask():
    def __init__(self):
        self.a = 0

    def main(self):
        exec(open("/home/gustavo/Desktop/automacao-python/sites/webhook/consultas/index.py").read())




if __name__ == '__main__':
    ab = Rodar_Flask()
    ab.main()