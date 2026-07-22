import unittest

from app.services import training_gov


class TrainingGovParserTest(unittest.TestCase):
    def test_extracts_qualification_units(self):
        html = """
        <html>
          <head><title>National Training Register - CPC31411 Certificate III in Construction Waterproofing</title></head>
          <body>
            <h2>Qualification details</h2>
            <h3>Packaging Rules</h3>
            <p>To achieve this qualification, the candidate must demonstrate competency in 19 units.</p>
            <h3>Units of competency</h3>
            CodeCPCCCM1012A | Title Work effectively and sustainably in the construction industry | Usage recommendation Superseded | Essential Core |
            CodeCPCCCM1013A | Title Plan and organise work | Usage recommendation Superseded | Essential Core |
          </body>
        </html>
        """

        product = training_gov._parse_training_page("CPC31411", "https://training.gov.au/training/details/CPC31411", html)

        self.assertEqual(product.code, "CPC31411")
        self.assertEqual(product.title, "Certificate III in Construction Waterproofing")
        self.assertEqual(product.product_type, "qualification")
        self.assertIn("19 units", product.summary)
        self.assertEqual(product.units[0]["code"], "CPCCCM1012A")
        self.assertEqual(product.units[0]["essential"], "Core")


if __name__ == "__main__":
    unittest.main()
