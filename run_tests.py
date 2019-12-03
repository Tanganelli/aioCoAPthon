#!/usr/bin/env python3.6
from aiocoapthon.tests.plugtest_block import PlugtestBlockClass
from aiocoapthon.tests.plugtest_block_client import PlugtestBlockClientClass
from aiocoapthon.tests.plugtest_core import PlugtestCoreClass
from aiocoapthon.tests.plugtest_core_client import PlugtestCoreClientClass
from aiocoapthon.tests.plugtest_link import PlugtestLinkClass
from aiocoapthon.tests.plugtest_link_client import PlugtestLinkClientClass
from aiocoapthon.tests.plugtest_observe import PlugtestObserveClass
from aiocoapthon.tests.plugtest_observe_client import PlugtestObserveClientClass

__author__ = 'Giacomo Tanganelli'


if __name__ == '__main__':  # pragma: no cover
    tests = PlugtestCoreClass()
    tests.main()
    tests = PlugtestLinkClass()
    tests.main()
    tests = PlugtestBlockClass()
    tests.main()
    tests = PlugtestObserveClass()
    tests.main()
    tests = PlugtestCoreClientClass()
    tests.main()
    tests = PlugtestLinkClientClass()
    tests.main()
    tests = PlugtestBlockClientClass()
    tests.main()
    tests = PlugtestObserveClientClass()
    tests.main()
