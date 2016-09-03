import unittest
from train import *
from subprocess import check_output

class splitTest(unittest.TestCase):

    #def testRandomSplit(self):
    #    #TODO

    def testRandomProjectSplit(self):
        input_dir = "/home/ccasal/cachelm_for_code_suggestion/evaluation/data/diverse_java"
        parts = randomProjectSplit(input_dir, 10, ".tokens")
        totalLen = 0
        for p in parts:
            totalLen += len(p)
        print(totalLen)
        #self.assertTrue(totalLen == 21393)

    def testBalancedProjectSplit(self):
        input_dir = "/home/ccasal/cachelm_for_code_suggestion/evaluation/data/diverse_java"
        parts = balancedProjectSplit(input_dir, 10, ".tokens")
        totalLen = 0
        print(parts)
        for p in parts:
            print("Size: " + str(len(p)))
            totalLen += len(p)
        print(totalLen)
        #self.assertTrue(totalLen == 21393)


if __name__=="__main__":
    unittest.main()
