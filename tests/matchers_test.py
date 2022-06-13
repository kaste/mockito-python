# Copyright (c) 2008-2016 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from mockito.matchers import MatcherError
from .test_base import TestBase
from mockito import mock, verify, when
from mockito.matchers import and_, or_, not_, eq, neq, lt, lte, gt, gte, \
    any_, arg_that, contains, matches, captor, ANY, ARGS, KWARGS
import re


class TestConvenienceMatchers:
    def testBuiltinAnyStandsForOurAny(self):
        dummy = mock()
        dummy.foo(1)
        dummy.foo('a')
        dummy.foo(True)

        verify(dummy, times=3).foo(any)

        dummy.foo(a=12)
        verify(dummy).foo(a=any)

    def testOurAnyCanBeUsedAsAType(self):
        dummy = mock()
        dummy.foo(1)
        dummy.foo('a')
        dummy.foo(True)
        verify(dummy, times=3).foo(any_)


class TestAliases:
    def testANY(self):
        dummy = mock()
        dummy.foo(1)
        verify(dummy).foo(ANY)

    def testARGS(self):
        dummy = mock()
        dummy.foo(1)
        verify(dummy).foo(*ARGS)

    def testKWARGS(self):
        dummy = mock()
        dummy.foo(a=1)
        verify(dummy).foo(**KWARGS)


class MatchersTest(TestBase):
    def testVerifiesUsingContainsMatcher(self):
        ourMock = mock()
        ourMock.foo("foobar")

        verify(ourMock).foo(contains("foo"))
        verify(ourMock).foo(contains("bar"))


class AndMatcherTest(TestBase):
    def testShouldSatisfyIfAllMatchersAreSatisfied(self):
        self.assertTrue(
            and_(contains("foo"), contains("bar")).matches("foobar"))

    def testShouldNotSatisfyIfOneOfMatchersIsNotSatisfied(self):
        self.assertFalse(
            and_(contains("foo"), contains("bam")).matches("foobar"))

    def testShouldTreatNonMatchersAsEqMatcher(self):
        self.assertTrue(and_("foo", any_(str)).matches("foo"))
        self.assertFalse(and_("foo", any_(int)).matches("foo"))


class OrMatcherTest(TestBase):
    def testShouldSatisfyIfAnyOfMatchersIsSatisfied(self):
        self.assertTrue(
            or_(contains("foo"), contains("bam")).matches("foobar"))

    def testShouldNotSatisfyIfAllOfMatchersAreNotSatisfied(self):
        self.assertFalse(
            or_(contains("bam"), contains("baz")).matches("foobar"))

    def testShouldTreatNonMatchersAsEqMatcher(self):
        self.assertTrue(or_("foo", "bar").matches("foo"))
        self.assertFalse(or_("foo", "bar").matches("bam"))


class NotMatcherTest(TestBase):
    def testShouldSatisfyIfInnerMatcherIsNotSatisfied(self):
        self.assertTrue(not_(contains("foo")).matches("bar"))

    def testShouldNotSatisfyIfInnerMatcherIsSatisfied(self):
        self.assertFalse(not_(contains("foo")).matches("foo"))

    def testShouldTreatNonMatchersAsEqMatcher(self):
        self.assertTrue(or_("foo", "bar").matches("foo"))


class EqMatcherTest(TestBase):
    def testShouldSatisfyIfArgMatchesGivenValue(self):
        self.assertTrue(eq("foo").matches("foo"))

    def testShouldNotSatisfyIfArgDoesNotMatchGivenValue(self):
        self.assertFalse(eq("foo").matches("bar"))


class NeqMatcherTest(TestBase):
    def testShouldSatisfyIfArgDoesNotMatchGivenValue(self):
        self.assertTrue(neq("foo").matches("bar"))

    def testShouldNotSatisfyIfArgMatchesGivenValue(self):
        self.assertFalse(neq("foo").matches("foo"))


class LtMatcherTest(TestBase):
    def testShouldSatisfyIfArgIsLessThanGivenValue(self):
        self.assertTrue(lt(5).matches(4))

    def testShouldNotSatisfyIfArgIsEqualToGivenValue(self):
        self.assertFalse(lt(5).matches(5))

    def testShouldNotSatisfyIfArgIsGreaterThanGivenValue(self):
        self.assertFalse(lt(5).matches(6))


class LteMatcherTest(TestBase):
    def testShouldSatisfyIfArgIsLessThanGivenValue(self):
        self.assertTrue(lte(5).matches(4))

    def testShouldSatisfyIfArgIsEqualToGivenValue(self):
        self.assertTrue(lte(5).matches(5))

    def testShouldNotSatisfyIfArgIsGreaterThanGivenValue(self):
        self.assertFalse(lte(5).matches(6))


class GtMatcherTest(TestBase):
    def testShouldNotSatisfyIfArgIsLessThanGivenValue(self):
        self.assertFalse(gt(5).matches(4))

    def testShouldNotSatisfyIfArgIsEqualToGivenValue(self):
        self.assertFalse(gt(5).matches(5))

    def testShouldSatisfyIfArgIsGreaterThanGivenValue(self):
        self.assertTrue(gt(5).matches(6))


class GteMatcherTest(TestBase):
    def testShouldNotSatisfyIfArgIsLessThanGivenValue(self):
        self.assertFalse(gte(5).matches(4))

    def testShouldSatisfyIfArgIsEqualToGivenValue(self):
        self.assertTrue(gte(5).matches(5))

    def testShouldSatisfyIfArgIsGreaterThanGivenValue(self):
        self.assertTrue(gte(5).matches(6))


class ArgThatMatcherTest(TestBase):
    def testShouldSatisfyIfPredicateReturnsTrue(self):
        self.assertTrue(arg_that(lambda arg: arg > 5).matches(10))

    def testShouldNotSatisfyIfPredicateReturnsFalse(self):
        self.assertFalse(arg_that(lambda arg: arg > 5).matches(1))


class ContainsMatcherTest(TestBase):
    def testShouldSatisfiySubstringOfGivenString(self):
        self.assertTrue(contains("foo").matches("foobar"))

    def testShouldSatisfySameString(self):
        self.assertTrue(contains("foobar").matches("foobar"))

    def testShouldNotSatisfiyStringWhichIsNotSubstringOfGivenString(self):
        self.assertFalse(contains("barfoo").matches("foobar"))

    def testShouldNotSatisfiyEmptyString(self):
        self.assertFalse(contains("").matches("foobar"))

    def testShouldNotSatisfiyNone(self):
        self.assertFalse(contains(None).matches("foobar"))


class MatchesMatcherTest(TestBase):
    def testShouldSatisfyIfRegexMatchesGivenString(self):
        self.assertTrue(matches('f..').matches('foo'))

    def testShouldAllowSpecifyingRegexFlags(self):
        self.assertFalse(matches('f..').matches('Foo'))
        self.assertTrue(matches('f..', re.IGNORECASE).matches('Foo'))

    def testShouldNotSatisfyIfRegexIsNotMatchedByGivenString(self):
        self.assertFalse(matches('f..').matches('bar'))


class ArgumentCaptorTest(TestBase):
    def test_matches_anything_by_default(self):
        assert captor().matches(12)
        assert captor().matches("anything")
        assert captor().matches(int)

    def test_matches_is_constrained_by_inner_matcher(self):
        assert captor(any_(int)).matches(12)
        assert not captor(any_(int)).matches("12")

    def test_all_values_initially_is_empty(self):
        c = captor()
        assert c.all_values == []

    def test_captures_all_values(self):
        m = mock()
        c = captor()

        when(m).do(c)
        m.do("any")
        m.do("thing")

        assert c.all_values == ["any", "thing"]

    def test_captures_only_matching_values(self):
        m = mock()
        c = captor(any_(int))

        when(m).do(c)
        m.do("any")
        m.do("thing")
        m.do(21)

        assert c.all_values == [21]

    def test_captures_all_values_while_verifying(self):
        m = mock()
        c = captor()

        m.do("any")
        m.do("thing")
        verify(m, times=2).do(c)

        assert c.all_values == ["any", "thing"]

    def test_remember_last_value(self):
        m = mock()
        c = captor()

        when(m).do(c)
        m.do("any")
        m.do("thing")

        assert c.value == "thing"

    def test_remember_last_value_while_verifying(self):
        m = mock()
        c = captor()

        m.do("any")
        m.do("thing")
        verify(m, times=2).do(c)

        assert c.value == "thing"

    def test_accessing_value_throws_if_nothing_captured_yet(self):
        c = captor()
        with self.assertRaises(MatcherError):
            _ = c.value

