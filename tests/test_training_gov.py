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

    def test_extracts_training_codes_from_canvas_metadata(self):
        codes = training_gov.extract_training_product_codes(
            "DEV Sew Garments MSTTX3014",
            "This page covers MSTAT3007 and repeats msttx3014.",
        )

        self.assertEqual(codes, ["MSTTX3014", "MSTAT3007"])

    def test_assigns_unit_code_aqf_indicator(self):
        product = training_gov.TrainingProduct(
            code="MSTTX3014",
            title="Set up, adjust and maintain industrial sewing machines",
            product_type="unit of competency",
            source_url="https://training.gov.au/training/details/MSTTX3014",
            raw_text="Qualifications that include this unit: Certificate IV in Apparel and Fashion",
        )

        suggestion = training_gov.aqf_suggestion(product)

        self.assertEqual(suggestion["aqf_level"], 3)
        self.assertEqual(suggestion["method"], "unit_code_indicator")
        self.assertIn("do not have a formal AQF level", suggestion["reason"])
        self.assertEqual(suggestion["training_product"]["code"], "MSTTX3014")

    def test_uses_qualification_title_before_code_indicator(self):
        product = training_gov.TrainingProduct(
            code="MST40119",
            title="Certificate IV in Textile Design, Development and Production",
            product_type="qualification",
        )

        suggestion = training_gov.aqf_suggestion(product)

        self.assertEqual(suggestion["aqf_level"], 4)
        self.assertEqual(suggestion["method"], "qualification")


if __name__ == "__main__":
    unittest.main()
