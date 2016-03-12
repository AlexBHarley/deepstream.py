import unittest
from src import Constants
from src.message import MessageBuilder


class TestMessageBuilderMethods(unittest.TestCase):
    MSG_SEP = Constants.MESSAGE_SEPARATOR
    PRT_SEP = Constants.MESSAGE_PART_SEPARATOR

    def test_get_message(self):
        self.assertEqual("A%sREQ%s" % (self.PRT_SEP, self.MSG_SEP), MessageBuilder.get_message(Constants.ACTIONS_ACK, Constants.ACTIONS_REQUEST, None))

if __name__ == '__main__':
    unittest.main()
