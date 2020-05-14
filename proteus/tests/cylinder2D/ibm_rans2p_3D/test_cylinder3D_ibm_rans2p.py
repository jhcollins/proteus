"""Tests for 3d flow around an immersed boundary cylinder with rans2p"""
from proteus.iproteus import *
from proteus import Comm
from proteus import Context
import tables
import importlib
import pytest


comm = Comm.get()
Profiling.logLevel = 7
Profiling.verbose = True
import numpy as np

class Test_ibm():

    @classmethod
    def setup_class(cls):
        cls._scriptdir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0,cls._scriptdir)
    @classmethod
    def teardown_class(cls):
        sys.path.remove(cls._scriptdir)
        pass

    def setup_method(self, method):
        """Initialize the test problem. """
        self.aux_names = []

    def teardown_method(self, method):
        """ Tear down function """
        FileList = ['cylinder_ibm_T1_ibm_3D_rans2p.h5','cylinder_ibm_T1_ibm_3D_rans2p.xmf'
                   ]
        for file in FileList:
            if os.path.isfile(file):
                os.remove(file)
            else:
                pass



#     def test_ex1(self):
#         self.compare_name = "T8P2"
#         self.example_setting("T=8.0 vspaceOrder=2 onlySaveFinalSolution=True")

    @pytest.mark.skip(reason="need to redo after history revision")                         
    def test_ex2(self):
        self.compare_name = "T1_ibm_3D_rans2p"
        self.example_setting("T=0.01 onlySaveFinalSolution=True")
        self.teardown_method(self)


    def example_setting(self, pre_setting):
        Context.contextOptionsString = pre_setting

        from . import cylinder_so as my_so
        reload(my_so)
        # defined in iproteus
        opts.profile = False
        opts.gatherArchive = True
        
        pList=[]
        nList=[]
        sList=[]
        for (pModule,nModule) in my_so.pnList:
            pList.append(
                importlib.import_module("."+pModule,
                                        "proteus.tests.cylinder2D.ibm_rans2p_3D"))
            nList.append(
                importlib.import_module("."+nModule,
                                        "proteus.tests.cylinder2D.ibm_rans2p_3D"))
            if pList[-1].name == None:
                pList[-1].name = pModule
            reload(pList[-1])  # Serious error
            reload(nList[-1])

        if my_so.sList == []:
            for i in range(len(my_so.pnList)):
                s = default_s
                sList.append(s)
        else:
            sList = my_so.sList
        my_so.name += "_ibm_"+self.compare_name #save data with different filename
        # NUMERICAL SOLUTION #
        ns = proteus.NumericalSolution.NS_base(my_so,
                                               pList,
                                               nList,
                                               sList,
                                               opts)
        self.aux_names.append(ns.modelList[0].name)
        ns.calculateSolution(my_so.name)

        actual = tables.open_file('cylinder_ibm_T1_ibm_3D_rans2p'+'.h5','r')
        expected_path = 'comparison_files/' + 'comparison_u_t2.csv'
        np.testing.assert_almost_equal(np.fromfile(os.path.join(self._scriptdir, expected_path),sep=","),np.array(actual.root.u_t2),decimal=10)
        actual.close()

