from oncotator.DuplicateAnnotationException import DuplicateAnnotationException
from oncotator.MutationData import MutationData
from oncotator.MutationDataFactory import MutationDataFactory
from oncotator.utils.NameColumnCollapser import NameColumnCollapser
from test.TestUtils import TestUtils

__author__ = 'lichtens'

import unittest

TestUtils.setupLogging(__file__, __name__)


class NameColumnCollapserTest(unittest.TestCase):
    def test_simple_collapse(self):
        """Ensure simple rules for numeric collapsing are honored"""
        m1 = MutationDataFactory.default_create(chr="1", start="10000", end="10000")
        m1.createAnnotation('ALT_F2R1', "34|36")
        m1.createAnnotation('i_t_Foxog', ".509|.511")
        m1.createAnnotation('i_tumor_f', ".200|.210")
        m1.createAnnotation('hamilcar', "0|0")
        m1.createAnnotation('donotcollapse', "1|45")

        m2 = MutationDataFactory.default_create(chr="1", start="10000", end="10000")
        m2.createAnnotation('ALT_F2R1', "36|38")
        m2.createAnnotation('i_t_Foxog', ".500|.510")
        m2.createAnnotation('i_tumor_f', ".100|.110")
        m2.createAnnotation('hamilcar', "0.01|0")
        m2.createAnnotation('barca', "0.02|0")
        m2.createAnnotation('donotcollapse', "100|4500")

        cc = NameColumnCollapser()
        cc.update_mutation(m1)
        self.assertEqual(m1['ALT_F2R1'], "34")
        self.assertEqual(float(m1['i_t_Foxog']), float(".510"))
        self.assertEqual(float(m1['i_tumor_f']), float(".205"))
        self.assertEqual(float(m1['hamilcar']), float("0"))
        self.assertEqual(m1['donotcollapse'], "1|45")

        cc.update_mutation(m2)
        self.assertEqual(m2['ALT_F2R1'], "36")
        self.assertEqual(float(m2['i_t_Foxog']), float(".505"))
        self.assertEqual(float(m2['i_tumor_f']), float(".105"))
        self.assertEqual(float(m2['hamilcar']), float("0.005"))
        self.assertEqual(float(m2['barca']), float("0.01"))
        self.assertEqual(m2['donotcollapse'], "100|4500")

    def test_cannot_collapse(self):
        """Make sure that we move on when we cannot collapse values."""
        m1 = MutationDataFactory.default_create(chr="1", start="10000", end="10000")
        m1.createAnnotation('ALT_F2R1', "|36")
        m1.createAnnotation('i_t_Foxog', "|")
        m1.createAnnotation('i_tumor_f', "")
        m1.createAnnotation('hamilcar', "0|blah")
        m1.createAnnotation('barca', "carthage_rules")
        m1.createAnnotation('donotcollapse', "1|45")

        cc = NameColumnCollapser()
        cc.update_mutation(m1)
        self.assertEqual(m1['ALT_F2R1'], "36")
        self.assertEqual(m1['i_t_Foxog'], "")
        self.assertEqual(m1['i_tumor_f'], "")
        self.assertEqual(m1['hamilcar'], "0|blah")
        self.assertEqual(m1['barca'], "carthage_rules")
        self.assertEqual(m1['donotcollapse'], "1|45")

    def test_updating_annotation_source(self):
        """Test that a String can be passed in to update the annotation source if columns are collapsed"""
        m1 = MutationDataFactory.default_create(chr="1", start="10000", end="10000")
        m1.createAnnotation('ALT_F2R1', "|36", annotationSource="TEST")
        cc = NameColumnCollapser()
        cc.update_mutation(m1, "foo")
        self.assertEqual(m1.getAnnotation("ALT_F2R1").getDatasource(), "foo")

    def test_not_updating_annotation_source(self):
        """Test that do not have to update annotation source if columns are collapsed"""
        m1 = MutationDataFactory.default_create(chr="1", start="10000", end="10000")
        m1.createAnnotation('ALT_F2R1', "|36", annotationSource="TEST")
        cc = NameColumnCollapser()
        cc.update_mutation(m1)
        self.assertEqual(m1.getAnnotation("ALT_F2R1").getDatasource(), "TEST")

    def test_annotation_copy(self):
        """Test that we can create a backup annotation with the old values after collapsing, if requested."""
        m1 = MutationDataFactory.default_create(chr="1", start="10000", end="10000")
        m1.createAnnotation('ALT_F2R1', "|36", annotationSource="TEST")
        cc = NameColumnCollapser()
        cc.update_mutation(m1, new_annotation_source="foo", copy_old_suffix="_full")
        self.assertEqual(m1["ALT_F2R1_full"], "|36")
        self.assertEqual(m1["ALT_F2R1"], "36")
        self.assertEqual(m1.getAnnotation("ALT_F2R1_full").getDatasource(), "TEST")
        self.assertTrue(m1.getAnnotation("ALT_F2R1").getDatasource() != m1.getAnnotation("ALT_F2R1_full").getDatasource())

    def test_annotation_copy_collision(self):
        """Test that annotation copy will use the bahavior of the mutation in case of collision due to suffix"""
        m1 = MutationDataFactory.default_create(chr="1", start="10000", end="10000")
        m1.createAnnotation('ALT_F2R1', "30|36", annotationSource="TEST")
        m1.createAnnotation('ALT_F2R1_full', "going_to_be_overwritten", annotationSource="TEST")

        is_exception_seen = False
        cc = NameColumnCollapser()
        try:
            cc.update_mutation(m1, copy_old_suffix="_full")
        except DuplicateAnnotationException as dae:
            is_exception_seen = True
        self.assertTrue(is_exception_seen, "Did not see duplicate annotation exception")

        m1 = MutationDataFactory.default_create(chr="1", start="10000", end="10000", allow_overwriting=True)
        m1.createAnnotation('ALT_F2R1', "30|36", annotationSource="TEST")
        m1.createAnnotation('ALT_F2R1_full', "going_to_be_overwritten", annotationSource="TEST")
        cc = NameColumnCollapser()
        cc.update_mutation(m1, copy_old_suffix="_full")
        self.assertEqual(m1['ALT_F2R1_full'], "30|36")
        self.assertEqual(m1['ALT_F2R1'], "30")


if __name__ == '__main__':
    unittest.main()
