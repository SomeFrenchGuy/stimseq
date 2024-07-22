#include <stdio.h>
#include <NIDAQmx.h>
#define DAQmxErrChk(functionCall)            \
    if (DAQmxFailed(error = (functionCall))) \
        goto Error;                          \
    else


/* Generic Example using DAQmx */

int main(void)
{
    int32 error = 0;
    TaskHandle taskHandle = 0;
    int32 read;
    float64 data[1000];
    char errBuff[2048] = {'\0'};

    // DAQmx analog voltage channel and timing parameters
    DAQmxErrChk(DAQmxCreateTask("", &taskHandle));

    DAQmxErrChk(DAQmxCreateAIVoltageChan(taskHandle, "Dev1/ai0", "", DAQmx_Val_Cfg_Default, -10.0, 10.0, DAQmx_Val_Volts, NULL));

    DAQmxErrChk(DAQmxCfgSampClkTiming(taskHandle, "", 10000.0, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 1000));

    // DAQmx Start Code
    DAQmxErrChk(DAQmxStartTask(taskHandle));

    // DAQmx Read Code
    DAQmxErrChk(DAQmxReadAnalogF64(taskHandle, 1000, 10.0, DAQmx_Val_GroupByChannel, data, 1000, &read, NULL));

    // Stop and clear task
Error:
    if (DAQmxFailed(error))
        DAQmxGetExtendedErrorInfo(errBuff, 2048);
    if (taskHandle != 0)
    {
        DAQmxStopTask(taskHandle);
        DAQmxClearTask(taskHandle);
    }
    if (DAQmxFailed(error))
        printf("DAQmx Error: %s\n", errBuff);
    return 0;
}