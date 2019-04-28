#include <sys/types.h>
#include <sys/ipc.h>
#include <pthread.h>
#include "s3c2410-adc.h"
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>

#define TUBE_IOCTROL  0x11
#define DOT_IOCTROL   0x12
#define ADC_DEV		"/dev/adc/0raw"
static int adc_fd = -1;

static int init_ADdevice(void)
{
	if((adc_fd=open(ADC_DEV, O_RDWR))<0){
		printf("Error opening %s adc device\n", ADC_DEV);
		return -1;
	}
}

static int GetADresult(int channel)
{
	int PRESCALE=0XFF;
	int data=ADC_WRITE(channel, PRESCALE);
	write(adc_fd, &data, sizeof(data));
	read(adc_fd, &data, sizeof(data));
	return data;
}
static int stop=0;

static void* comMonitor(void* data)
{
	getchar();
	stop=1;
	return NULL;
}

void jmdelay(int n) {
    int i,j,k;
    for (i=0;i<n;i++)
        for (j=0;j<100;j++)
            for (k=0;k<100;k++);
}

int main() {
    int fd;
    int i,j,k;
    int o;
    int d;
    int d2;
    char tmp[2];
    pthread_t th_com;
    void * retval;
    unsigned int LEDWORD;
    unsigned int MLEDA[8];
    unsigned char LEDCODE[10]={0xc0,0xf9,0xa4,0xb0,0x99,0x92,0x82,0xf8,0x80,0x90};
    unsigned char dd_data[16][10]={{0xff,0,0,0,0,0,0,0,0,0},
	{0,0xff,0,0,0,0,0,0,0,0},
	{0,0,0xff,0,0,0,0,0,0,0},
	{0,0,0,0xff,0,0,0,0,0,0},
	{0,0,0,0,0xff,0,0,0,0,0},
	{0,0,0,0,0,0xff,0,0,0,0},
	{0,0,0,0,0,0,0xff,0,0,0},
	{0,0,0,0,0,0,0,0xff,0,0},
	{0x1,0x1,0x1,0x1,0x1,0x1,0x1,0x1,0,0},
	{0x2,0x2,0x2,0x2,0x2,0x2,0x2,0x2,0,0},
	{0x4,0x4,0x4,0x4,0x4,0x4,0x4,0x4,0,0},
	{0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0,0},
	{0x10,0x10,0x10,0x10,0x10,0x10,0x10,0x10,0,0},
	{0x20,0x20,0x20,0x20,0x20,0x20,0x20,0x20,0,0},
	{0x40,0x40,0x40,0x40,0x40,0x40,0x40,0x40,0,0},
	{0x80,0x80,0x80,0x80,0x80,0x80,0x80,0x80,0,0},
    };


	//set s3c44b0 AD register and start AD
	if(init_ADdevice()<0)
		return -1;                                 

    fd=open("/dev/led/0raw",O_RDWR);
    if (fd < 0) {
        printf("####Led device open fail####\n");
        return (-1);
    }

    LEDWORD=0xff00;
    printf("will enter TUBE LED  ,please waiting .............. \n");
    LEDWORD=0xff00;
    ioctl(fd,0x11,LEDWORD);
    sleep(1);

    printf("will enter DIG LED  ,please waiting .............. \n");
    sleep(1);
	/* Create the threads */
	pthread_create(&th_com, NULL, comMonitor, 0);

	while( stop==0 ){
			d=((int)GetADresult(0))/11;

		LEDWORD=(LEDCODE[d/10]<<8)|LEDCODE[d%10];
            ioctl(fd,0x12,LEDWORD);
            jmdelay(500);
		d2=((int)GetADresult(1))/11;
               
              ioctl(fd,0x11,0xff00);
                write(fd,dd_data[d2%16],10);
			
		usleep(1);
	}
	pthread_join(th_com, &retval);

    close(fd);
    return 0;

}

