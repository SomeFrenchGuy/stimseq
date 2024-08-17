#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#include "stimseq.h"
#include "logger.h"
#include "sequence_loader.h"
#include "sequence_parser.h"

#include <NIDAQmx.h>

// Period between Samples (in ms) 
// When changed, sample_number calculation should also be changed
#define SAMPLE_PERIOD   1

// Wiring info
#define VALVES_DO   "Dev1/port0"
#define PIEZO_DO    "Dev1/port1/line0"
#define LED_AO      "Dev1/ao0"
#define TTL_DI      "Dev1/PFI0"

// Timeout for Digital / Analog write to buffer (in s)
#define TIMEOUT     10

// Generic DAQmx Error Checker (From Doc)
#define DAQmxErrChk(functionCall) if( DAQmxFailed(error=(functionCall)) ) goto Error; else

// The task handler for DAQmx
static TaskHandle  task_handle_do = 0;
static TaskHandle  task_handle_ao = 0;


static int pack(bool array [], unsigned int size, bool little_endian);

bool load_sequence(const TimeStep * sequence, const int sequence_size)
{
    int32 error = 0;

    // Number of sample per second
    float64 sample_rate = (float64) SAMPLE_PERIOD * 1000;

    // Number of samples to be written is equal to the number of milliseconds
    // Should be changed if SAMPLE_PERIOD is modififed
    uInt64 sample_number = (uInt64) sequence[sequence_size - 1].time;
    char error_buffer[2048] = {'\0'};

    uInt32 *time_stamp = malloc(sample_number * sizeof(uInt32));
    float64 *led_voltage = malloc(sample_number * sizeof(float64));
    
    // Data organized like this:
    // [Chan 0 Sample 0, Chan 1 Sample 0, Chan 0 Sample1, Chan 1 Sample1, etc]
    // Chan 0 being for Valves and Chan 1 for Piezo
    uInt8 *do_samples = malloc(2 * sample_number * sizeof(uInt8));


    // Re-arrange Time Steps data for DAQ mx
    int j = -1;
    for (int i = 0; i < sample_number; i++)
    {
        if (sequence[j+1].time == i)
        {
            j++;
        }

        time_stamp[i] = sequence[j].time;
        led_voltage[i] = (float64) sequence[j].led_voltage;
        do_samples[2*i] = pack((bool []) {                        \
                                            sequence[j].valves[0],  \
                                            sequence[j].valves[1],  \
                                            sequence[j].valves[2],  \
                                            sequence[j].valves[3],  \
                                            sequence[j].valves[4],  \
                                            sequence[j].valves[5],  \
                                            sequence[j].valves[6],  \
                                            sequence[j].valves[7]} , 8, true);
        do_samples[2*i + 1] = sequence[j].piezo_trigger;
    }

    print_log(DEBUG, "    | Timestamp | Led Voltage | Piezo | Valves");
    for (int i = 0; i < sample_number; i++)
    {
        print_log(DEBUG, "%4i|%11i|%13i|%7i| %i", i, time_stamp[i], led_voltage[i], do_samples[2*i + 1], do_samples[2*i]);
    }

    // DAQmx task init
    print_log(DEBUG, "DAQmx - Task init");
    DAQmxErrChk(DAQmxCreateTask("stimseq Digital Outputs", &task_handle_do));
    DAQmxErrChk(DAQmxCreateTask("stimseq Analog Outputs", &task_handle_ao));

    // Setup Channels
    print_log(DEBUG, "DAQmx - Setup Channels");
	DAQmxErrChk(DAQmxCreateDOChan(task_handle_do, VALVES_DO, "Valves",DAQmx_Val_ChanForAllLines));
	DAQmxErrChk(DAQmxCreateDOChan(task_handle_do, PIEZO_DO, "Piezo", DAQmx_Val_ChanPerLine));
	DAQmxErrChk(DAQmxCreateAOVoltageChan(task_handle_ao, LED_AO, "LED", 0, 10, DAQmx_Val_Volts, NULL));

    // Setup Sample generation timing
    print_log(DEBUG, "DAQmx - Setup Sample generation timing");
    // DAQmxErrChk(DAQmxCfgSampClkTiming(task_handle_do, "OnboardClock", sample_rate, DAQmx_Val_Falling, DAQmx_Val_FiniteSamps, sample_number));
    // DAQmxErrChk(DAQmxCfgSampClkTiming(task_handle_ao, "OnboardClock", sample_rate, DAQmx_Val_Falling, DAQmx_Val_FiniteSamps, sample_number));
    DAQmxErrChk(DAQmxCfgDigEdgeAdvTrig(task_handle_ao, "Dev1/PFI0", DAQmx_Val_Rising));
    DAQmxErrChk(DAQmxCfgDigEdgeAdvTrig(task_handle_do, "Dev1/PFI0", DAQmx_Val_Rising));


    // Setup trigger signal
    print_log(DEBUG, "DAQmx - Setup trigger signal");
	DAQmxErrChk (DAQmxCfgDigEdgeStartTrig(task_handle_do, TTL_DI, DAQmx_Val_Rising));
	DAQmxErrChk (DAQmxCfgDigEdgeStartTrig(task_handle_ao, TTL_DI, DAQmx_Val_Rising));

    // Setup sample Generations
    print_log(DEBUG, "DAQmx - Setup sample Generations");
	DAQmxErrChk(DAQmxWriteDigitalU8(task_handle_do, sample_number, 0, TIMEOUT, DAQmx_Val_GroupByScanNumber, do_samples, NULL, NULL));
	DAQmxErrChk(DAQmxWriteAnalogF64(task_handle_ao, sample_number, 0, TIMEOUT, DAQmx_Val_GroupByScanNumber, led_voltage, NULL, NULL));

    // Enable task
    print_log(DEBUG, "DAQmx - Enable task");
	DAQmxErrChk(DAQmxStartTask(task_handle_do));
	DAQmxErrChk(DAQmxStartTask(task_handle_ao));

    // Wait for the tasks to end
    print_log(DEBUG, "DAQmx - Wait for the tasks to end");
	DAQmxErrChk (DAQmxWaitUntilTaskDone(task_handle_do, 20.0));
	DAQmxErrChk (DAQmxWaitUntilTaskDone(task_handle_ao, 20.0));

    // Free Memory and return
    print_log(DEBUG, "Free Memory and return");
    free(time_stamp);
    free(led_voltage);
    free(do_samples);
    return true;

// Stop and clear task
Error:
    if (DAQmxFailed(error) )
    {
        DAQmxGetExtendedErrorInfo(error_buffer,2048);
    }

    if (task_handle_do != 0)
    {
        DAQmxStopTask(task_handle_do);
        DAQmxClearTask(task_handle_do);
    }

    if (task_handle_ao != 0)
    {
        DAQmxStopTask(task_handle_ao);
        DAQmxClearTask(task_handle_ao);
    }

    if (DAQmxFailed(error))
    {
        print_log(ERROR, "DAQmx Error: %s\n", error_buffer);
    }
    

    // Free Memory and return
    free(time_stamp);
    free(led_voltage);
    free(do_samples);
    return false;
}



// Pack an array of bool into a single int
// WARNING do not use to pack more bool than the size of int (32)
// Little_endian = true if array should be read from right to left
static int pack(bool array [], unsigned int size, bool little_endian)
{ 
	int packed_value = 0; 

    if (little_endian)
    {
        for (int i = 0; i < size; i++) { 
            if(array[size - (i + 1)]) 
            {
                packed_value |=  (1 << i);
            }
        } 
    }
    else
    {
        for (int i = 0; i < size; i++) { 
            if(array[i]) 
            {
                packed_value |=  (1 << i);
            }
        }
    }
	return packed_value; 
}