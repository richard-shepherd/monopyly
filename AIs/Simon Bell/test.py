###########################################################
## File        : test.py
## Description : 

import sys, os
import datetime
import logging
import logging.config
import decimal,fractions

import unittest

import snowboarderDB

class MyTestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.db=snowboarderDB.SnowboarderDB()
        except Exception as err:
            assert False, "Exception thrown: "+str(err)

    def setUp(self):
        """Call before every test case."""
        print('Calling \'setUp\'')

    def tearDown(self):
        """Call after every test case."""
        print('Calling \'tearDown\'')

    """Test cases. Note that all test method names must begin with 'test'."""

    def testA(self):
        print('Calling \'testA\'')
        try:
            selection='distinct PropertySetName'
            source='Property'
            criteria='PropertyName=\'Old Kent Road\''
            results=self.db.Query(selection,source,criteria,'')
            assert True
        except Exception as err:
            assert False, "Exception thrown: "+str(err)

    def testB(self):
        print('Calling \'testB\'')
        try:
            propertyNames=['Vine Street', 'Strand', 'Trafalgar Square', 'Pall Mall', 'Northumberland Avenue', 'Regent Street', 'Bond Street']
            self.db.UpdateOwnership(propertyNames)
            results=self.db.Query('PropertyName,Owned','Property','','')
            assert True
        except Exception as err:
            assert False, "Exception thrown: "+str(err)

    def testC(self):
        print('Calling \'testC\'')
        try:
            # unitTest=snowboarderDB.SnowboarderDB()
            propertyName='Vine Street'
            self.db.UpdateDealAttempts(propertyName)
            results=self.db.Query('*','Property','PropertyName=\''+propertyName+'\'','')
            assert True
        except Exception as err:
            assert False, "Exception thrown: "+str(err)

    def testD(self):
        print('Calling \'testD\'')
        try:
            # unitTest=snowboarderDB.SnowboarderDB()
            results=self.db.FindMissingProperties()
            assert True
        except Exception as err:
            assert False, "Exception thrown: "+str(err)

if __name__=='__main__':
    try:
        print("Starting tests")
        # unittest.main() # run all tests
        suite=unittest.TestSuite()
        suite.addTest(MyTestCases('testB'))
        suite.addTest(MyTestCases('testC'))
        suite.addTest(MyTestCases('testD'))
        unittest.TextTestRunner(verbosity=1).run(suite)
        print("Finished tests")
    except Exception as err:
        print("Exception thrown: "+str(err))

