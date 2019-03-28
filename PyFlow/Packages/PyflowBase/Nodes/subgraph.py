import os
import json
import weakref

from PyFlow.Core import NodeBase
from PyFlow.Core import GraphBase
from PyFlow.Core.GraphTree import GraphTree
from PyFlow.Core.Common import *


class subgraph(NodeBase):
    """this node encapsulates a graph, like compound in xsi

    pins can be edited only from inside the subgraph
    """
    def __init__(self, name):
        super(subgraph, self).__init__(name)
        self.rawGraph = None
        self.__inputsMap = {}  # { self.[inputPin]: innerOutPin }
        self.__outputsMap = {}  # { self.[outputPin]: innerInPin }

    @staticmethod
    def pinTypeHints():
        return {'inputs': [], 'outputs': []}

    @staticmethod
    def category():
        return 'Common'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return 'Encapsulate a graph inside a node'

    def onGraphInputPinCreated(self, outPin):
        """Reaction when pin added to graphInputs node

        Arguments:
            outPin {PinBase} -- output pin on graphInputs node
        """

        # add companion pin for graphInputs node's output pin
        subgraphInputPin = self.addInputPin(outPin.name,
                                            outPin.dataType,
                                            outPin.defaultValue(),
                                            outPin.call,
                                            outPin.constraint)
        subgraphInputPin.supportedDataTypes = outPin.supportedDataTypes
        self.__inputsMap[subgraphInputPin] = outPin
        pinAffects(subgraphInputPin, outPin)
        # connect
        outPin.nameChanged.connect(subgraphInputPin.setName)

        def onInnerOutKilled(*args, **kwargs):
            self.__inputsMap.pop(subgraphInputPin)
            subgraphInputPin.kill()
        outPin.killed.connect(onInnerOutKilled, weak=False)

        # watch if something is connected to inner companion
        # and change default value
        def onInnerOutConnected(other):
            subgraphInputPin._data = other.currentData()
        outPin.onPinConnected.connect(onInnerOutConnected, weak=False)

    def onGraphInputPinDeleted(self, inPin):
        # remove companion pin for inner graphInputs node pin
        print("onGraphInputPinDeleted", inPin.getName())

    def onGraphOutputPinCreated(self, inPin):
        """Reaction when pin added to graphOutputs node

        Arguments:
            inPin {PinBase} -- input pin on graphOutputs node
        """

        # add companion pin for graphOutputs node's input pin
        subgraphOutputPin = self.addOutputPin(inPin.name,
                                              inPin.dataType,
                                              inPin.defaultValue(),
                                              inPin.call,
                                              inPin.constraint)
        subgraphOutputPin.supportedDataTypes = inPin.supportedDataTypes
        self.__outputsMap[subgraphOutputPin] = inPin
        pinAffects(inPin, subgraphOutputPin)
        # connect
        inPin.nameChanged.connect(subgraphOutputPin.setName)

        def onInnerInpPinKilled(*args, **kwargs):
            subgraphOutputPin.kill()
            self.__outputsMap.pop(subgraphOutputPin)
        inPin.killed.connect(onInnerInpPinKilled, weak=False)

        # watch if something is connected to inner companion
        # and change default value
        def onInnerInpPinConnected(other):
            subgraphOutputPin._data = other.currentData()
        inPin.onPinConnected.connect(onInnerInpPinConnected, weak=False)

    def onGraphOutputPinDeleted(self, outPin):
        # remove companion pin for inner graphOutputs node pin
        print("onGraphOutputPinDeleted", outPin.getName())

    def postCreate(self, jsonTemplate=None):
        self.rawGraph = GraphBase(self.name)
        GraphTree().addChildGraph(self.rawGraph)

        # connect with pin creation events and add dynamic pins
        self.rawGraph.onInputPinCreated.connect(self.onGraphInputPinCreated)
        self.rawGraph.onInputPinDeleted.connect(self.onGraphInputPinDeleted)
        self.rawGraph.onOutputPinCreated.connect(self.onGraphOutputPinCreated)
        self.rawGraph.onOutputPinDeleted.connect(self.onGraphOutputPinDeleted)

    def compute(self):
        # get data from subgraph node input pins and put it to inner companions
        # for inputPin, innerOutPin in self.__inputsMap.items():
        #     innerOutPin.setData(inputPin.getData())

        # put data from inner graph pins to outer subgraph node output companions
        for outputPin, innerPin in self.__outputsMap.items():
            outputPin.setData(innerPin.getData())
