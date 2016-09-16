import os
import itertools
from unittest import TestCase, mock

from MedusaPackager import MedusaPackager


class TestFind_package_files(TestCase):
    sample_package = [
                        r"sample/3901805/access/3901805_ChicagoProfessionalCampus_1960-61.tif",
                        r"sample/3901805/access/3901805_ChicagoProfessionalCampus_1962.tif",
                        r"sample/3901805/access/3901805_UIatChicagoCircle_1969-70.tif",
                        r"sample/3901805/access/3901805_UIatChicagoCircle_1970-71.tif",
                        r"sample/3901805/access/3901805_UIatChicagoCircle_1971-72.tif",
                        r"sample/3901805/access/3901805_UIattheMedical Center_1970-71.tif",
                        r"sample/3901805/access/3901805_UIattheMedical Center_1971-72.tif",
                        r"sample/3901805/access/3901805_UIattheMedicalCenter_1969-70.tif",
                        r"sample/3901805/access/3901805_UICampus_1960-61.tif",
                        r"sample/3901805/access/3901805_UICampus_1962.tif",
                        r"sample/3901805/access/3901805_UICampus_1963.tif",
                        r"sample/3901805/access/3901805_UICampus_1964.tif",
                        r"sample/3901805/access/3901805_UICampus_1965.tif",
                        r"sample/3901805/access/3901805_UICampus_1966.tif",
                        r"sample/3901805/access/3901805_UICampus_1967.tif",
                        r"sample/3901805/access/3901805_UICampus_1968.tif",
                        r"sample/3901805/access/3901805_UICampus_1969-70.tif",
                        r"sample/3901805/access/3901805_UICampus_1969.tif",
                        r"sample/3901805/access/3901805_UICampus_1970-71.tif",
                        r"sample/3901805/access/3901805_UICampus_1971-72.tif",
                        r"sample/3901805/access/3901805_UIMedicalCenterCampusChicago_1969.tif",
                        r"sample/3901805/access/Thumbs.db",
                        r"sample/3901805/preservation master/3901805_ChicagoProfessionalCampus_1960-61.tif",
                        r"sample/3901805/preservation master/3901805_ChicagoProfessionalCampus_1962.tif",
                        r"sample/3901805/preservation master/3901805_UIatChicagoCircle_1969-70.tif",
                        r"sample/3901805/preservation master/3901805_UIatChicagoCircle_1970-71.tif",
                        r"sample/3901805/preservation master/3901805_UIatChicagoCircle_1971-72.tif",
                        r"sample/3901805/preservation master/3901805_UIattheMedical Center_1970-71.tif",
                        r"sample/3901805/preservation master/3901805_UIattheMedical Center_1971-72.tif",
                        r"sample/3901805/preservation master/3901805_UIattheMedicalCenter_1969-70.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1960-61.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1962.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1963.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1964.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1965.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1966.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1967.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1968.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1969-70.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1969.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1970-71.tif",
                        r"sample/3901805/preservation master/3901805_UICampus_1971-72.tif",
                        r"sample/3901805/preservation master/3901805_UIMedicalCenterCampus,Chicago_1969.tif",
                        r"sample/3901805/preservation master/Thumbs.db"
                    ]

    def setUp(self):
        with mock.patch("os.walk") as test_walk:
            test_walk.return_value = [
                ('sample/20160429_MappingHsitory_mm', ['3901805'], []),
                ('sample/20160429_MappingHsitory_mm/3901805',
                 ['access', 'preservation master'], []),
                ('sample/20160429_MappingHsitory_mm/3901805/access',
                     [],
                     ['3901805_ChicagoProfessionalCampus_1960-61.tif',
                      '3901805_ChicagoProfessionalCampus_1962.tif',
                      '3901805_UIatChicagoCircle_1969-70.tif',
                      '3901805_UIatChicagoCircle_1970-71.tif',
                      '3901805_UIatChicagoCircle_1971-72.tif',
                      '3901805_UIattheMedical Center_1970-71.tif',
                      '3901805_UIattheMedical Center_1971-72.tif',
                      '3901805_UIattheMedicalCenter_1969-70.tif',
                      '3901805_UICampus_1960-61.tif',
                      '3901805_UICampus_1962.tif',
                      '3901805_UICampus_1963.tif',
                      '3901805_UICampus_1964.tif',
                      '3901805_UICampus_1965.tif',
                      '3901805_UICampus_1966.tif',
                      '3901805_UICampus_1967.tif',
                      '3901805_UICampus_1968.tif',
                      '3901805_UICampus_1969-70.tif',
                      '3901805_UICampus_1969.tif',
                      '3901805_UICampus_1970-71.tif',
                      '3901805_UICampus_1971-72.tif',
                      '3901805_UIMedicalCenterCampusChicago_1969.tif',
                      'Thumbs.db']),
                ('sample/20160429_MappingHsitory_mm/3901805/preservation master',
                 [], ['3901805_ChicagoProfessionalCampus_1960-61.tif',
                      '3901805_ChicagoProfessionalCampus_1962.tif',
                      '3901805_UIatChicagoCircle_1969-70.tif',
                      '3901805_UIatChicagoCircle_1970-71.tif',
                      '3901805_UIatChicagoCircle_1971-72.tif',
                      '3901805_UIattheMedical Center_1970-71.tif',
                      '3901805_UIattheMedical Center_1971-72.tif',
                      '3901805_UIattheMedicalCenter_1969-70.tif',
                      '3901805_UIattheMedicalCenter_1969-70.TIF',
                      '3901805_UIattheMedicalCenter_1969-70.foo',
                      '3901805_UICampus_1960-61.tif',
                      '3901805_UICampus_1962.tif',
                      '3901805_UICampus_1963.tif',
                      '3901805_UICampus_1964.tif',
                      '3901805_UICampus_1965.tif',
                      '3901805_UICampus_1966.tif',
                      '3901805_UICampus_1967.tif',
                      '3901805_UICampus_1968.tif',
                      '3901805_UICampus_1969-70.tif',
                      '3901805_UICampus_1969.tif',
                      '3901805_UICampus_1970-71.tif',
                      '3901805_UICampus_1971-72.tif',
                      '3901805_UIMedicalCenterCampus,Chicago_1969.tif',
                      'Thumbs.db']),

            ]

            self.package = MedusaPackager.find_package_files(r"")

    def test_find_package_imageonly(self):

        for file in self.package.all_image_files:
            ext = os.path.splitext(file)[1]
            self.assertNotEqual(ext, ".db", msg="Found system file{}".format(file))
            self.assertTrue(ext.lower() in MedusaPackager.VALID_IMAGE_EXTENSIONS, msg="{} is not a valid file type".format(file))

    def test_find_package_ignored(self):
        for file in self.package.ignored_files:
            ext = os.path.splitext(file)[1]
            self.assertTrue(ext.lower() not in MedusaPackager.VALID_IMAGE_EXTENSIONS,
                            msg="{} is a valid file type and shouldn't be in the ignored files".format(file))

    def test_split_item_level_iter(self):
        for item in MedusaPackager.split_items(self.package, MedusaPackager.default_grouper):
            self.assertIsNotNone(item)
            self.assertIsInstance(item, MedusaPackager.MedusaPackageData)
        pass

    def test_sorted(self):
        data = self.package.sorted()
        self.assertEqual(len(data.preservation_files), 22)
        self.assertEqual(len(data.access_files), 21)

    def test_generate_deployment(self):
        raw_data = sorted(self.package.split_items(MedusaPackager.dash_grouper), key=lambda x: x.package_name)[0]
        data = raw_data.sorted()
        jobs = sorted(data.generate_deployment("/tmp"), key=lambda x: x.source)
        self.assertEqual(os.path.normpath(jobs[0].destination),
                         os.path.normpath("/tmp/3901805_ChicagoProfessionalCampus_1960/access/3901805_ChicagoProfessionalCampus_1960-61.tif"))
        self.assertEqual(os.path.normpath(jobs[0].source),
                         os.path.normpath("sample/20160429_MappingHsitory_mm/3901805/access/3901805_ChicagoProfessionalCampus_1960-61.tif"))
