# coding: utf-8
# Copyright 2023 Banana Juice LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime

import pytest

from .. import helpers


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ("1d", datetime.timedelta(days=1)),
        ("12d", datetime.timedelta(days=12)),
        ("8h", datetime.timedelta(hours=8)),
        ("83s", datetime.timedelta(seconds=83)),
        ("99ms", datetime.timedelta(milliseconds=99)),
        ("777us", datetime.timedelta(microseconds=777)),
        ("1w", datetime.timedelta(weeks=1)),
        ("7w", datetime.timedelta(weeks=7)),
    ),
)
def test_parse_timedelta(value: str, expected: datetime.timedelta):
    got = helpers.parse_timedelta(value)
    assert got == expected
