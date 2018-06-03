from emg_shield import EMGShieldController
from passwords import PasswordCollectionThread

samples = 9
name = 'ale'

if __name__ == '__main__':
    controller = EMGShieldController()
    print("Bienvenido!")
    for x in range(1, samples + 1):
        truesense = PasswordCollectionThread(controller, name, x)

        input("Presione enter para continuar...")
        truesense.start()
        # To improve record key presses
        password = input()
        truesense.stop()
