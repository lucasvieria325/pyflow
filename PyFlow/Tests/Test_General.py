from TestsBase import *


class TestGeneral(unittest.TestCase):

    def setUp(self):
        print('\t[BEGIN TEST]', self._testMethodName)
        GraphTree(GraphBase("testGraph"))

    def tearDown(self):
        print('--------------------------------\n')
        GraphTree().clear()

    def test_add_int_no_exec(self):
        packages = GET_PACKAGES()
        intlib = packages['PyflowBase'].GetFunctionLibraries()["IntLib"]
        foos = intlib.getFunctions()

        addNode1 = NodeBase.initializeFromFunction(foos["add"])
        addNode2 = NodeBase.initializeFromFunction(foos["add"])

        GraphTree().activeGraph().addNode(addNode1)
        GraphTree().activeGraph().addNode(addNode2)

        addNode1.setData('a', 5)

        connection = connectPins(addNode1.getPinByName('out', PinSelectionGroup.Outputs), addNode2.getPinByName('a', PinSelectionGroup.Inputs))
        self.assertEqual(connection, True, "FAILED TO ADD EDGE")
        self.assertEqual(addNode2.getData('out'), 5, "NODES EVALUATION IS INCORRECT")

    def test_foo_node_ref_set_data(self):
        packages = GET_PACKAGES()
        randomLib = packages['PyflowBase'].GetFunctionLibraries()["RandomLib"]
        defaultLib = packages['PyflowBase'].GetFunctionLibraries()["DefaultLib"]
        randomLibFoos = randomLib.getFunctions()
        defaultLibFoos = defaultLib.getFunctions()

        randintNode = NodeBase.initializeFromFunction(randomLibFoos["randint"])
        printNode = NodeBase.initializeFromFunction(defaultLibFoos["pyprint"])

        GraphTree().activeGraph().addNode(randintNode)
        GraphTree().activeGraph().addNode(printNode)

        self.assertIsNotNone(randintNode)
        self.assertIsNotNone(printNode)

        pRandIntResultPin = randintNode.getPinByName('Result', PinSelectionGroup.Outputs)
        pRandIntOutExecPin = randintNode.getPinByName('outExec', PinSelectionGroup.Outputs)
        pRandIntInExecPin = randintNode.getPinByName('inExec', PinSelectionGroup.Inputs)
        pPrintInputValuePin = printNode.getPinByName('entity', PinSelectionGroup.Inputs)
        pPrintInputExecPin = printNode.getPinByName('inExec', PinSelectionGroup.Inputs)
        self.assertIsNotNone(pRandIntResultPin)
        self.assertIsNotNone(pPrintInputValuePin)
        self.assertIsNotNone(pRandIntOutExecPin)
        self.assertIsNotNone(pPrintInputExecPin)

        edge1Created = connectPins(pRandIntOutExecPin, pPrintInputExecPin)
        edge2Created = connectPins(pRandIntResultPin, pPrintInputValuePin)
        self.assertEqual(edge1Created, True, "FAILED TO CONNECT EXECS")
        self.assertEqual(edge2Created, True, "FAILED TO CONNECT INT AND ANY")

        values = set()
        for i in range(10):
            pRandIntInExecPin.call()
            values.add(pPrintInputValuePin.currentData())
        self.assertGreater(len(values), 1)

    def test_reconnect_value(self):
        packages = GET_PACKAGES()

        defaultLib = packages['PyflowBase'].GetFunctionLibraries()["DefaultLib"]
        foos = defaultLib.getFunctions()

        n1 = NodeBase.initializeFromFunction(foos["makeBool"])
        n2 = NodeBase.initializeFromFunction(foos["makeBool"])
        n3 = NodeBase.initializeFromFunction(foos["makeBool"])

        GraphTree().activeGraph().addNode(n1)
        GraphTree().activeGraph().addNode(n2)
        GraphTree().activeGraph().addNode(n3)

        n1Out = n1.getPinByName('out', PinSelectionGroup.Outputs)
        n3b = n3.getPinByName('b', PinSelectionGroup.Inputs)
        # connect n1.out and n3.b
        c1 = connectPins(n1Out, n3b)
        # check connection was created
        self.assertEqual(c1, True)
        # check n1.out affects on n3.b
        self.assertEqual(n3b in n1Out.affects, True)
        # check n3.b affected by n1.out
        self.assertEqual(n1Out in n3b.affected_by, True)

        n2Out = n2.getPinByName('out', PinSelectionGroup.Outputs)
        # connect n2.out to n3.b
        # n3.b is connected with n1.out
        # we expect n3.b breaks all connections before connecting with n2.out
        c2 = connectPins(n2Out, n3b)
        # check connections successfull
        self.assertEqual(c2, True)
        # check n2.out affects on n3.b
        self.assertEqual(n3b in n2Out.affects, True, "incorrect connection")
        # check n3.b affected by n2.out
        self.assertEqual(n2Out in n3b.affected_by, True, "incorrect")
        # check n1.out really disconnected
        self.assertEqual(n1Out.affects, set(), "not cleared")

    def test_are_pins_connected(self):
        packages = GET_PACKAGES()
        intlib = packages['PyflowBase'].GetFunctionLibraries()["IntLib"]
        foos = intlib.getFunctions()

        addNode1 = NodeBase.initializeFromFunction(foos["add"])
        addNode2 = NodeBase.initializeFromFunction(foos["add"])

        GraphTree().activeGraph().addNode(addNode1)
        GraphTree().activeGraph().addNode(addNode2)

        pinOut = addNode1.getPinByName('out', PinSelectionGroup.Outputs)
        pinInp = addNode2.getPinByName('a', PinSelectionGroup.Inputs)
        bConnected = connectPins(pinOut, pinInp)
        self.assertEqual(bConnected, True, "FAILED TO ADD EDGE")
        self.assertEqual(arePinsConnected(pinOut, pinInp), True)

        disconnected = disconnectPins(pinInp, pinOut)
        self.assertEqual(disconnected, True, "pins are not disconnected")
        self.assertEqual(arePinsConnected(pinOut, pinInp), False)

    def test_create_var(self):
        v1 = GraphTree().activeGraph().createVariable()
        self.assertEqual(v1.uid in GraphTree().activeGraph().vars, True)

    def test_get_any_var(self):
        packages = GET_PACKAGES()

        # create any type variable
        v1 = GraphTree().activeGraph().createVariable()
        v1.value = False

        # create variable getter node
        varGetterClass = packages["PyflowBase"].GetNodeClasses()['getVar']
        varGetterInstance = varGetterClass('v1Getter', v1)
        GraphTree().activeGraph().addNode(varGetterInstance)

        # create print node
        defaultLib = packages["PyflowBase"].GetFunctionLibraries()['DefaultLib']
        printerInstance = NodeBase.initializeFromFunction(defaultLib.getFunctions()['pyprint'])
        GraphTree().activeGraph().addNode(printerInstance)

        # connect to print node input
        varOutPin = varGetterInstance.getPinByName('value', PinSelectionGroup.Outputs)
        self.assertIsNotNone(varOutPin)
        printInPin = printerInstance.getPinByName('entity', PinSelectionGroup.Inputs)
        printInExecPin = printerInstance.getPinByName('inExec', PinSelectionGroup.Inputs)
        connected = connectPins(varOutPin, printInPin)
        self.assertEqual(connected, True, "var getter is not connected")

        # print variable value and check it
        printInExecPin.call()
        self.assertEqual(printInPin.currentData(), False)
        # next, change variable value (Not varGetterInstance varOutPin! Note we are not touching it anymore)
        # this will broadcast valueChanged on v1, which will trigger dirty propagation from varOutPin
        # varGetterInstance.onVarValueChanged and v1.valueChanged were connected in getVar.postCreate
        v1.value = True
        # following line will trigger compute on print node, which will ask data on it's inputs
        # Inputs on print node will be dirty, data will be asked on varGetterInstance varOutPin
        printInExecPin.call()
        self.assertEqual(printInPin.currentData(), True)

    def test_get_bool_var(self):
        packages = GET_PACKAGES()

        # create bool variable
        v1 = GraphTree().activeGraph().createVariable('BoolPin')
        v1.value = False

        # create variable getter node
        varGetterClass = packages["PyflowBase"].GetNodeClasses()['getVar']
        # since variable is bool, bool pin will be created
        varGetterInstance = varGetterClass('v1Getter', v1)
        GraphTree().activeGraph().addNode(varGetterInstance)

        # create print node
        defaultLib = packages["PyflowBase"].GetFunctionLibraries()['DefaultLib']
        printerInstance = NodeBase.initializeFromFunction(defaultLib.getFunctions()['pyprint'])
        GraphTree().activeGraph().addNode(printerInstance)

        # connect to print node input
        varOutPin = varGetterInstance.getPinByName('value', PinSelectionGroup.Outputs)
        printInPin = printerInstance.getPinByName('entity', PinSelectionGroup.Inputs)
        printInExecPin = printerInstance.getPinByName('inExec', PinSelectionGroup.Inputs)
        connected = connectPins(varOutPin, printInPin)
        self.assertEqual(connected, True, "var getter is not connected")

        # print variable value and check it
        printInExecPin.call()
        self.assertEqual(printInPin.currentData(), False)
        # next, change variable value (Not varGetterInstance varOutPin! Note we are not touching it anymore)
        # this will broadcast valueChanged on v1, which will trigger dirty propagation from varOutPin
        # varGetterInstance.onVarValueChanged and v1.valueChanged were connected in getVar.postCreate
        v1.value = True
        # following line will trigger compute on print node, which will ask data on it's inputs
        # Inputs on print node will be dirty, data will be asked on varGetterInstance varOutPin
        printInExecPin.call()
        self.assertEqual(printInPin.currentData(), True)

    def test_kill_variable(self):
        packages = GET_PACKAGES()

        # create any type variable
        v1 = GraphTree().activeGraph().createVariable()
        v1.value = False

        # create variable getter node
        varGetterClass = packages["PyflowBase"].GetNodeClasses()['getVar']
        varGetterInstance = varGetterClass('v1Getter', v1)
        GraphTree().activeGraph().addNode(varGetterInstance)

        # create print node
        defaultLib = packages["PyflowBase"].GetFunctionLibraries()['DefaultLib']
        printerInstance = NodeBase.initializeFromFunction(defaultLib.getFunctions()['pyprint'])
        GraphTree().activeGraph().addNode(printerInstance)

        # connect to print node input
        varOutPin = varGetterInstance.getPinByName('value', PinSelectionGroup.Outputs)
        printInPin = printerInstance.getPinByName('entity', PinSelectionGroup.Inputs)
        printInExecPin = printerInstance.getPinByName('inExec', PinSelectionGroup.Inputs)
        connected = connectPins(varOutPin, printInPin)
        self.assertEqual(connected, True, "var getter is not connected")

        GraphTree().activeGraph().killVariable(v1)
        self.assertEqual(v1 not in GraphTree().activeGraph().vars, True, "variable not killed")
        self.assertEqual(varGetterInstance.uid not in GraphTree().activeGraph().nodes, True, "get var not killed")
        connected = arePinsConnected(varOutPin, printInPin)
        self.assertEqual(connected, False, "get var node is removed, but pins are still connected")

    def test_set_any_var(self):
        packages = GET_PACKAGES()

        # create any type variable
        v1 = GraphTree().activeGraph().createVariable()
        # type checking will not be performed since this is any type
        v1.value = False

        # create variable setter node
        varSetterClass = packages["PyflowBase"].GetNodeClasses()['setVar']
        varSetterInstance = varSetterClass('v1Setter', v1)
        setterAdded = GraphTree().activeGraph().addNode(varSetterInstance)
        self.assertEqual(setterAdded, True)

        # set new value to setter node input pin
        inExecPin = varSetterInstance.getPinByName('exec', PinSelectionGroup.Inputs)
        inPin = varSetterInstance.getPinByName('inp', PinSelectionGroup.Inputs)
        outPin = varSetterInstance.getPinByName('out', PinSelectionGroup.Outputs)
        self.assertIsNotNone(inExecPin)
        self.assertIsNotNone(inPin)
        self.assertIsNotNone(outPin)
        # next we set data to setter node
        inPin.setData(True)
        # And fire input exec pin.
        # We expect it will call compute
        # which will update variable value
        inExecPin.call()
        # check variable value
        self.assertEqual(v1.value, True, "variable value is not set")

    def test_set_bool_var(self):
        import pyrr
        packages = GET_PACKAGES()

        # create bool type variable
        v1 = GraphTree().activeGraph().createVariable('BoolPin')
        # this will accept only bools
        v1.value = False

        # create variable setter node
        varSetterClass = packages["PyflowBase"].GetNodeClasses()['setVar']
        varSetterInstance = varSetterClass('v1Setter', v1)
        setterAdded = GraphTree().activeGraph().addNode(varSetterInstance)
        self.assertEqual(setterAdded, True)

        # set new value to setter node input pin
        inExecPin = varSetterInstance.getPinByName('exec', PinSelectionGroup.Inputs)
        inPin = varSetterInstance.getPinByName('inp', PinSelectionGroup.Inputs)
        outPin = varSetterInstance.getPinByName('out', PinSelectionGroup.Outputs)
        self.assertIsNotNone(inExecPin)
        self.assertIsNotNone(inPin)
        self.assertIsNotNone(outPin)
        # next we set data to setter node
        inPin.setData(True)
        # And fire input exec pin.
        # We expect it will call compute
        # which will update variable value
        inExecPin.call()
        # check variable value
        self.assertEqual(v1.value, True, "variable value is not set")

    def test_subgraph_simple(self):
        """Here we create subgraph node with two add nodes connected inside [add1.out -> add2.a]

        switch active graph to subgraph and back to root
        check subgraph node exposes pins from underlined graph inputs/outputs nodes
        add nodes to different graphs of GraphTree
        check inner pins broadcasts changes to outer companion pins on subgraph node

        """
        packages = GET_PACKAGES()

        GT = GraphTree()

        # create empty subgraph
        subgraphNodeClass = packages['PyflowBase'].GetNodeClasses()['subgraph']
        subgraphNodeInstance = subgraphNodeClass('subgraph')
        GT.activeGraph().addNode(subgraphNodeInstance)
        self.assertEqual(GT.getRootGraph().name, "testGraph", "root graph is invalid")
        self.assertEqual(GT.activeGraph().name, "testGraph")

        # try add graph inputs to root. None expected
        inputsRoot = GT.activeGraph().getInputNode()
        self.assertEqual(inputsRoot, None, "graph inputs node make no sense in root graph")

        # step inside subgraph
        GT.switchGraph(subgraphNodeInstance.name)
        self.assertEqual(GT.activeGraph().name, subgraphNodeInstance.name, "failed to enter subgraph")

        # add input output nodes to expose pins to outer subgraph node
        inputs1 = GT.activeGraph().getInputNode()
        outputs1 = GT.activeGraph().getOutputNode()
        self.assertIsNotNone(inputs1, "failed to create graph inputs node")
        self.assertIsNotNone(outputs1, "failed to create graph outputs node")

        # create out pin on graphInputs node
        # this should expose input pin on subgraph node
        outPin = inputs1.addOutPin()
        self.assertEqual(len(subgraphNodeInstance.namePinInputsMap), 1, "failed to expose input pin")
        self.assertEqual(list(subgraphNodeInstance.inputs.values())[0].name, outPin.name)

        # change inner pin name and check it is reflected outside
        outPin.setName("first")
        self.assertEqual(list(subgraphNodeInstance.inputs.values())[0].name, outPin.name, "name is not synchronized")

        # create input pin on graphOutputs node
        # this should expose output pin on subgraph node
        inPin = outputs1.addInPin()
        self.assertEqual(len(subgraphNodeInstance.namePinOutputsMap), 1, "failed to expose input pin")
        self.assertEqual(list(subgraphNodeInstance.outputs.values())[0].name, inPin.name)

        # change inner pin name and check it is reflected outside
        inPin.setName("first")
        self.assertEqual(list(subgraphNodeInstance.outputs.values())[0].name, inPin.name, "name is not synchronized")

        subgraphInPin = subgraphNodeInstance.getPinByName('first', PinSelectionGroup.Inputs)
        self.assertIsNotNone(subgraphInPin, "failed to find subgraph out pin")
        subgraphOutPin = subgraphNodeInstance.getPinByName('first', PinSelectionGroup.Outputs)
        self.assertIsNotNone(subgraphOutPin, "failed to find subgraph out pin")

        # add simple calculation
        foos = packages['PyflowBase'].GetFunctionLibraries()["IntLib"].getFunctions()

        addNode1 = NodeBase.initializeFromFunction(foos["add"])
        addNode2 = NodeBase.initializeFromFunction(foos["add"])
        GT.activeGraph().addNode(addNode1)
        GT.activeGraph().addNode(addNode2)
        addNode1.setData("b", 1)
        addNode2.setData("b", 1)
        connection = connectPins(addNode1.getPinByName('out', PinSelectionGroup.Outputs), addNode2.getPinByName('a', PinSelectionGroup.Inputs))
        self.assertEqual(connection, True)

        # connect add nodes with graph inputs/outputs
        # this connections should change outside companion pins types and update its values by type's default values
        connected = connectPins(inputs1.getPinByName('first'), addNode1.getPinByName('a'))
        self.assertIsNotNone(subgraphInPin.currentData(), "outer pin data is invalid")
        self.assertEqual(connected, True)
        self.assertIsNotNone(inputs1.getPinByName('first').currentData(), "output companion pin data is incorrect")

        connected = connectPins(outputs1.getPinByName('first'), addNode2.getPinByName('out'))
        self.assertIsNotNone(subgraphOutPin.currentData(), "outer pin data is")
        self.assertEqual(connected, True)
        self.assertIsNotNone(outputs1.getPinByName('first').currentData(), "output companion pin data is incorrect")

        # go back to root graph
        GT.switchGraph("testGraph")
        self.assertEqual(GT.activeGraph().name, "testGraph", "failed to return back to root from subgraph node")

        # check exposed pins added
        self.assertEqual(len(subgraphNodeInstance.inputs), 1)
        self.assertEqual(len(subgraphNodeInstance.outputs), 1)

        # connect getter to subgraph output pin
        defaultLibFoos = packages['PyflowBase'].GetFunctionLibraries()["DefaultLib"].getFunctions()
        printNode = NodeBase.initializeFromFunction(defaultLibFoos["pyprint"])
        GT.activeGraph().addNode(printNode)

        connected = connectPins(printNode.getPinByName('entity'), subgraphOutPin)
        self.assertEqual(connected, True)

        # check value
        printNode.getPinByName('inExec').call()
        self.assertEqual(printNode.getPinByName('entity').currentData(), 2)

        # connect another add node to exposed subgraph input
        addNode3 = NodeBase.initializeFromFunction(foos["add"])
        GT.activeGraph().addNode(addNode3)
        addNode3.setData('a', 1)
        connected = connectPins(addNode3.getPinByName('out'), subgraphInPin)
        self.assertEqual(connected, True)

        # any pin should be connected, because we have int calculations inside subgraph
        self.assertEqual(subgraphInPin.hasConnections(), True, "subgraph input pin has no connections")

        # check value
        printNode.getPinByName('inExec').call()
        self.assertEqual(printNode.getPinByName('entity').currentData(), 3)

        # kill inner pins and check outer companions killed also
        self.assertEqual(len(subgraphNodeInstance.pins), 2)
        inPin.kill()
        self.assertEqual(len(subgraphNodeInstance.outputs), 0, "outer companion pin is not killed")
        self.assertEqual(len(subgraphNodeInstance.pins), 1)
        outPin.kill()
        self.assertEqual(len(subgraphNodeInstance.inputs), 0, "outer companion pin is not killed")
        self.assertEqual(len(subgraphNodeInstance.pins), 0, "outer companion pins are not killed")


if __name__ == '__main__':
    unittest.main()
