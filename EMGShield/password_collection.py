from emg_shield import EMGShieldController
from passwords import PasswordCollectionThread

samples = 1
name = 'Luis'

if __name__ == '__main__':
    controller = EMGShieldController()
    print("Bienvenido!")
    for x in range(1, samples + 1):
        truesense = PasswordCollectionThread(controller, name, x)

        print("Esta es la muestra {}".format(x))
        input("Presione enter para continuar...")

        print("Ingrese el nombre de usuario 'test@test.com' y luego presione enter:")
        truesense.start()
        # To improve record key presses
        user = input()
        print("Ingrese la contraseña 'esta es una contraseña muy larga' y luego presione enter:")
        password = input()
        truesense.stop()