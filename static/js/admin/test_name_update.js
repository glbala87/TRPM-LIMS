(function($) {
    $(document).ready(function() {
        // This function updates the test_name choices based on the selected test_type
        $('#id_test_type').change(function() {
            var testType = $(this).val();
            var testNames = TEST_CHOICES[testType] || [];
            var testNameField = $('#id_test_name');
            testNameField.empty();  // Clear the current options

            // Add the options for the selected test_type
            testNames.forEach(function(test) {
                testNameField.append(new Option(test[0], test[0]));
            });
        });

        // Initialize the test_name field based on the current test_type selection
        if ($('#id_test_type').val()) {
            $('#id_test_type').change();
        }
    });
})(django.jQuery);

// Add your choices data for each test_type as a JavaScript object
const TEST_CHOICES = {
    'HORMONES_AND_VITAMINS': [
        ['ANTI MULLERIAN HORMONE', 'Serum', 'Red/Yellow'],
        ['B-HCG IN BLOOD', 'Serum', 'Red/Yellow'],
        ['CORTISOL', 'Serum', 'Red/Yellow'],
        ['DHEA - S', 'Serum', 'Red/Yellow'],
        ['ESTRADIOL', 'Serum', 'Red/Yellow'],
        ['FREE T3', 'Serum', 'Red/Yellow'],
        ['FREE T4', 'Serum', 'Red/Yellow'],
        ['FSH', 'Serum', 'Red/Yellow'],
        ['LH', 'Serum', 'Red/Yellow'],
        ['PROGESTERONE (FREE)', 'Serum', 'Red/Yellow'],
        ['PROGESTERONE (TOTAL)', 'Serum', 'Red/Yellow'],
        ['PROLACTIN', 'Serum', 'Red/Yellow'],
        ['SEX HORMONE BINDING GLOBULIN(SHBG)', 'Serum', 'Red/Yellow'],
        ['TESTOSTERONE FREE', 'Serum', 'Red/Yellow'],
        ['TESTOSTERONE TOTAL', 'Serum', 'Red/Yellow'],
        ['THYROID STIMULATINGHORMONE (TSH)', 'Serum', 'Red/Yellow'],
        ['VITAMIN B12', 'Serum', 'Red/Yellow'],
        ['VITAMIN D3', 'Serum', 'Red/Yellow'],
        ['INSULIN', 'Serum', 'Red/Yellow'],
        ['PREGNANCY TEST (BLOOD)', 'Serum', 'Red/Yellow'],
        ['PREGNANCY TEST (SERUM)', 'Serum', 'Red/Yellow'],
        ['PREGNANCY TEST (URINE)', 'Urine', 'Sterile Container'],
        ['THYROID PEROXIDASEAUTOANTIBODIES (ATPO)', 'Serum', 'Red/Yellow'],
        ['VITAMIN B9 (FOLIC ACID)', 'Serum', 'Red/Yellow'],
    ],
    'BIOCHEMISTRY': [
        ['ALBUMIN', 'Serum', 'Red/Yellow'],
        ['ALKALINE PHOSPHATASE', 'Serum', 'Red/Yellow'],
        ['AMYLASE', 'Serum', 'Red/Yellow'],
        ['BILIRUBIN (direct)', 'Serum', 'Red/Yellow'],
        ['BILIRUBIN (indirect)', 'Serum', 'Red/Yellow'],
        ['BILIRUBIN (total)', 'Serum', 'Red/Yellow'],
        ['CALCIUM (total)', 'Serum', 'Red/Yellow'],
        ['CALCIUM (CORRECTED)', 'Serum', 'Red/Yellow'],
        ['Sodium', 'Serum', 'Red/Yellow'],
        ['Potassium', 'Serum', 'Red/Yellow'],
        ['Chloride', 'Serum', 'Red/Yellow'],
        ['CHOLESTEROL', 'Serum', 'Red/Yellow'],
        ['CREATININE', 'Serum', 'Red/Yellow'],
        ['CK, TOTAL', 'Serum', 'Red/Yellow'],
        ['CK MB', 'Serum', 'Red/Yellow'],
        ['GLUCOSE (FASTING)', 'Serum', 'Red/Yellow'],
        ['GLUCOSE (P.P)', 'Serum', 'Red/Yellow'],
        ['GLUCOSE (RANDOM)', 'Serum', 'Red/Yellow'],
        ['HDL', 'Serum', 'Red/Yellow'],
        ['IRON', 'Serum', 'Red/Yellow'],
        ['LDH', 'Serum', 'Red/Yellow'],
        ['LDL', 'Serum', 'Red/Yellow'],
        ['LIPASE', 'Serum', 'Red/Yellow'],
        ['MAGNESIUM', 'Serum', 'Red/Yellow'],
        ['PHOSPHORUS', 'Serum', 'Red/Yellow'],
        ['SGOT(AST)', 'Serum', 'Red/Yellow'],
        ['SGPT(ALT)', 'Serum', 'Red/Yellow'],
        ['TOTAL PROTEIN', 'Serum', 'Red/Yellow'],
        ['TRIGLYCERIDE', 'Serum', 'Red/Yellow'],
        ['UREA', 'Serum', 'Red/Yellow'],
        ['URIC ACID', 'Serum', 'Red/Yellow'],
        ['ZINC', 'Serum', 'Red/Yellow'],
    ],
    'IMMUNOLOGY': [
        ['ANTI THYROID PEROXIDASE Abs (TPO)', 'Serum', 'Red/Yellow'],
        ['H-PYLORI Ab', 'Serum', 'Red/Yellow'],
        // Add other tests here...
    ],
    'SEROLOGY': [
        ['CRP H.S', 'Serum', 'Red/Yellow'],
        ['MONOSPOT', 'Serum', 'Red/Yellow'],
        ['RHEUMATOID FACTOR', 'Serum', 'Red/Yellow'],
        ['SYPHILIS', 'Serum', 'Red/Yellow'],
    ],
    'CANCER_MARKERS': [
        ['CA-125', 'Serum', 'Red/Yellow'],
        ['PSA TOTAL', 'Serum', 'Red/Yellow'],
        ['PSA FREE', 'Serum', 'Red/Yellow'],
    ],
    'MICROBIOLOGY_ROUTINE': [
        ['TB GOLD QUANTIFERON', 'Blood', 'EDTA BLOOD (PURPLE)'],
        ['BLOOD CULTURE ANDSENSITIVITY', 'Blood', 'Sterile Container'],
        // Add other Microbiology Routine tests here...
    ],
    'MICROBIOLOGY_CULTURE': [
        ['SPUTUM CULTURE &SENSITIVITY', 'Sputum', 'Sterile Container'],
        ['SEMEN CULTURE &SENSITIVITY', 'Semen', 'Sterile Container'],
        ['STOOL CULTURE ANDSENSITIVITY', 'Stool', 'STOOL CONTAINER'],
        ['VAGINAL SWAB CULTURE &SENSITIVITY', 'Vaginal Swab', 'Sterile Container'],
        // Add other Microbiology Culture tests here...
    ]
};
