#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <math.h>

int main(void) {

    unsigned int horas = 4;
    long int ms = 3600*horas;

    printf("\n\n-------- SISTEMA DE REINICIALIZAÇÃO AGENDADA ----------\n");
    printf(">>> SISTEMA AGENDADO PARA REINICIAR A CADA %d HORAS <<<\n", horas);
    fflush(stdout);

    while(true) {

        for (int i=ms; i >= 0; i--) {
            printf("\rAguardando: %.2f horas...", (float)i/3600);
            fflush(stdout);
            nanosleep((const struct timespec[]){{1, 0}}, NULL);
        }

        printf("\nReiniciando serviços");
        fflush(stdout);   

        popen("killall chrome");
        popen("killall xterm");
        popen("/home/gustavo/Desktop/automacao-python/shell_scripts/automacao.sh", "w");
        popen("/home/gustavo/Desktop/automacao-python/shell_scripts/ngrok_s.sh", "w");
        popen("/home/gustavo/Desktop/automacao-python/automacao_app/PainelAutomacao.sh", "w");

    }
}
