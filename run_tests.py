#!/usr/bin/env python3.6
from tests.plugtest_block import PlugtestBlockClass
from tests.plugtest_block_client import PlugtestBlockClientClass
from tests.plugtest_core import PlugtestCoreClass
from tests.plugtest_core_client import PlugtestCoreClientClass
from tests.plugtest_link import PlugtestLinkClass
from tests.plugtest_link_client import PlugtestLinkClientClass
from tests.plugtest_observe import PlugtestObserveClass
from tests.pugtest_observe_client import PlugtestObserveClientClass

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
