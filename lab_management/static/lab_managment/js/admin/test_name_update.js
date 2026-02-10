(function($) {
    $(document).ready(function() {
        // This function updates the test_name choices based on the selected test_type
        $('#id_test_type').change(function() {
            var testType = $(this).val();
            var testNames = TEST_CHOICES[testType] || [];  // Retrieve the test names for the selected type
            var testNameField = $('#id_test_name');
            testNameField.empty();  // Clear the current options

            // Add the options for the selected test_type
            if (testNames.length > 0) {
                testNames.forEach(function(test) {
                    testNameField.append(new Option(test[0], test[0]));  // Add new options for the test names
                });
            } else {
                // If no test names are available for the selected type, add a placeholder
                testNameField.append(new Option("No tests available", ""));
            }
        });

        // Initialize the test_name field based on the current test_type selection
        if ($('#id_test_type').val()) {
            $('#id_test_type').change();  // Trigger the change event to update the test names
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
        // Add more test names...
    ],
    'BIOCHEMISTRY': [
        ['ALBUMIN', 'Serum', 'Red/Yellow'],
        ['ALKALINE PHOSPHATASE', 'Serum', 'Red/Yellow'],
        // Add more test names...
    ],
    // Add more categories and test names...
};
