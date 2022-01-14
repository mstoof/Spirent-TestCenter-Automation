"""
    Goal: Spirent TestCenter API
    Tasks:
      - Create Project
      - Configure Ports
      - Create SteamBlocks (Traffic Generator)
      - Attaching Ports
      - Subscription
      - Traffic Generation
      - Stop Traffic
      - Unsubscription
      - Disconnect
"""
from StcPython import StcPython


class SpirentTestCenter():
    def __init__(self):
        self.chassis_address = '192.168.2.152'
        self.slot = 1
        self.location = f"//{self.chassis_address}/{self.slot}"
        self.log_file = "mylog.txt"
        self.stc = StcPython
        self.stc.config('automationoptions', loglevel='info', logto=self.log_file)
        self.project = self.stc.create("Project")
        self.project_attrbs = self.stc.get(self.project, 'name')

    def create_ports(self):
        """

        :param ports: A list of ports that need to be configured
        :return: A list of configured ports
        """
        port1 = self.stc.create('port', under=self.project)
        port2 = self.stc.create('port', under=self.project)

        self.stc.config(port1, location=f"{self.location}")
        self.stc.config(port2, location=f"{self.location}")

        port_list = [port1, port2]

        return port_list

    def create_streamblock(self, port_list):
        self.stc.create('streamBlock', under=port_list[0])
        generator = self.stc.get(port_list[0], 'children_generator')
        analyzer = self.stc.get(port_list[1], 'children-Analyzer')

        return generator, analyzer

    def attach_ports(self, port_list):
        self.stc.perform('AttachPorts', portList=port_list, autoConnect='TRUE')
        self.stc.apply()

    def subscription(self, port_list, analyzer, generator):
        port1GeneratorResult = self.stc.subscribe(Parent=self.project,
                                                  ResultParent=port_list[0],
                                                  ConfigType='Generator',
                                                  resulttype='GeneratorPortResults',
                                                  filenameprefix=f"Generator_port1_counter_{port_list[0]}",
                                                  interval=2
                                                  )

        port2AnalyzerResult = self.stc.subscribe(Parent=self.project,
                                                 ResultParent=port_list[1],
                                                 ConfigType='Analyzer',
                                                 resulttype='AnalyzerPortResults'
                                                 )
        # Start Traffic...
        self.stc.perform('AnalyzerStart', analyzerList=analyzer)
        self.stc.sleep(1)

        self.stc.perform('GeneratorStart', generatorList=generator)

        # Generate Traffic for 5 seconds
        self.stc.sleep(5)

        # Stopping Traffic...

        self.stc.perform('GeneratorStop', generatorList=generator)
        self.stc.perform('AnalyzerStop', analyzerList=analyzer)

        return port1GeneratorResult, port2AnalyzerResult

    def quit(self, port1GeneratorResult, port2AnalyzerResult):
        self.stc.unsubscribe(port1GeneratorResult)
        self.stc.unsubscribe(port2AnalyzerResult)

        self.stc.disconnect(self.chassis_address)
        self.stc.delete(self.project)


if __name__ == '__main__':
    # Initialize Testcenter class
    stc = SpirentTestCenter()

    print('Configure Ports')
    port_list = stc.create_ports()

    print('Create Traffic SteamBlock')
    generator, analyzer = stc.create_streamblock(port_list)

    print('Attach Ports')
    stc.attach_ports()

    print('Subscription')
    port1GeneratorResult, port2AnalyzerResult = stc.subscription(port_list, analyzer, generator)

    print('Quit the program ')
    stc.quit()

