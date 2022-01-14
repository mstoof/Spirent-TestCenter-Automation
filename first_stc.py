"""
    Goal: Simple Python Initialization for Spirent Testcenter API communication
    Maintainer: Maurice Stoof
    E-Mail: maurice@mcstoof.com
    Date: 14-01-2022
"""
from StcPython import StcPython


# Variables used throughout the script
log_file = 'mylog.txt'
# Initialize Spirent TestCenter Python
stc = StcPython()
chassisAddress = '192.168.2.152'
slot = 1
p1 = 1
p2 = 2


print(f"Using {chassisAddress}/{slot}/1")
print(f"Using {chassisAddress}/{slot}/2")

# Setup the log file
stc.config('automationoptions', loglevel='info', logto=log_file)


print('Create a Project - root')
project = stc.create("Project")

print('Get Project Attributes')
project_attrbs = stc.get(project, 'name')
print(project_attrbs)

print(f'Create multiple Ports in {project}')
port1 = stc.create('port', under=project)
port2 = stc.create('port', under=project)

stc.config(port1, location=f"//{chassisAddress}/{slot}/{p1}")
stc.config(port2, location=f"//{chassisAddress}/{slot}/{p2}")

print('Creating StreamBlock IE Traffic on Port 1')
streamBlock = stc.create('streamBlock', under=port1)
generator = stc.get(port1, 'children-generator')
analyzer = stc.get(port2, 'children-Analyzer')

print('Attaching Ports..')
stc.perform('AttachPorts', portList=[port1, port2], autoConnect='TRUE')
stc.apply()

print('Call Subscribe...')
port1GeneratorResult = stc.subscribe(Parent=project,
                                     ResultParent=port1,
                                     ConfigType='Generator',
                                     resulttype='GeneratorPortResults',
                                     filenameprefix=f"Generator_port1_counter_{port1}",
                                     interval=2
                                     )
port2AnalyzerResult = stc.subscribe(Parent=project,
                                    ResultParent=port2,
                                    ConfigType='Analyzer',
                                    resulttype='AnalyzerPortResults',
                                    )




print("Starting Traffic")
stc.perform('AnalyzerStart', analyzerList=analyzer)
print(f'start {analyzer}')

# wait for analyzer to start
stc.sleep(1)

stc.perform('GeneratorStart', generatorList=generator)
print(f'start {generator}')

# generate traffic for 5 seconds
print('Sleep 5 seconds...')
stc.sleep(5)

print("Stopping Traffic...")
stc.perform('GeneratorStop', generatorList=generator)
stc.perform('AnalyzerStop', analyzerList=analyzer)
print(f'stop {generator}')
print(f'stop {analyzer}')

print('Call Unsubscribe...')
stc.unsubscribe(port2AnalyzerResult)
stc.unsubscribe(port1GeneratorResult)

print('Call Disconnect...')
stc.disconnect(chassisAddress)
stc.delete(project)




# Send the configurations to Spirent Testcenter
stc.apply()