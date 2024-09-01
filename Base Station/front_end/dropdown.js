window.onload = function() {
    // Add an event listener to the dropdown menu for item selection
    document.getElementById('itemSelection').addEventListener('change', function() {
        // Hide the custom selection area initially
        document.getElementById('customSelectionArea').style.display = 'none';
        
        // Get the selected value from the dropdown
        const selectedValue = this.value;
        
        // Display or hide sections based on the selected value
        if (selectedValue === 'All') {
            // Hide all sections when 'All' is selected
            document.getElementById('CycleAnalystSelectionArea').style.display = 'none';
            document.getElementById('TempaturesSelectionArea').style.display = 'none';
            document.getElementById('customSelectionArea').style.display = 'none';
            document.getElementById('submitSelectionArea').style.display = 'none';
        } else if (selectedValue === 'CycleAnalyst') {
            // Show only the Cycle Analyst section
            document.getElementById('CycleAnalystSelectionArea').style.display = 'block';
            document.getElementById('TempaturesSelectionArea').style.display = 'none';
            document.getElementById('customSelectionArea').style.display = 'none';
            document.getElementById('submitSelectionArea').style.display = 'block';
        } else if (selectedValue === 'Tempatures') {
            // Show only the Temperatures section
            document.getElementById('TempaturesSelectionArea').style.display = 'block';
            document.getElementById('CycleAnalystSelectionArea').style.display = 'none';
            document.getElementById('customSelectionArea').style.display = 'none';
            document.getElementById('submitSelectionArea').style.display = 'block';
        } else if (selectedValue === 'Custom') {
            // Show all sections when 'Custom' is selected
            document.getElementById('customSelectionArea').style.display = 'block';
            document.getElementById('CycleAnalystSelectionArea').style.display = 'block';
            document.getElementById('TempaturesSelectionArea').style.display = 'block';
            document.getElementById('submitSelectionArea').style.display = 'block';
        } 
    });
};

function clearSelectedCheckboxes() {
    // Get all checkbox elements on the page
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    // Uncheck all checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
}

function getSelectedCheckboxes() {    
    // Get all checked checkboxes
    const checkedBoxes = document.querySelectorAll('input[type="checkbox"]:checked');
    
    // Map the selected checkboxes to an array of their IDs
    const selectedIds = Array.from(checkedBoxes).map(box => box.id);
    
    // Store the selected checkbox IDs in the 'items' variable
    items = selectedIds;
    
    // Update the content based on the selected checkboxes
    updateContent();
}
