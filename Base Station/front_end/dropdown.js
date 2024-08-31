window.onload = function() {
    document.getElementById('itemSelection').addEventListener('change', function() {
        // Hide all selection areas first
        document.getElementById('customSelectionArea').style.display = 'none';
        // Show or Hide the selected areas
        const selectedValue = this.value;
        if (selectedValue === 'All') {
            document.getElementById('CycleAnalystSelectionArea').style.display = 'none';
            document.getElementById('TempaturesSelectionArea').style.display = 'none';
            document.getElementById('customSelectionArea').style.display = 'none';
            document.getElementById('submitSelectionArea').style.display = 'none';
        } else if (selectedValue === 'CycleAnalyst') {
            document.getElementById('CycleAnalystSelectionArea').style.display = 'block';
            document.getElementById('TempaturesSelectionArea').style.display = 'none';
            document.getElementById('customSelectionArea').style.display = 'none';
            document.getElementById('submitSelectionArea').style.display = 'block';
        } else if (selectedValue === 'Tempatures') {
            document.getElementById('TempaturesSelectionArea').style.display = 'block';
            document.getElementById('CycleAnalystSelectionArea').style.display = 'none';
            document.getElementById('customSelectionArea').style.display = 'none';
            document.getElementById('submitSelectionArea').style.display = 'block';
        } else if (selectedValue === 'Custom') {
            document.getElementById('customSelectionArea').style.display = 'block';
            document.getElementById('CycleAnalystSelectionArea').style.display = 'block';
            document.getElementById('TempaturesSelectionArea').style.display = 'block';
            document.getElementById('submitSelectionArea').style.display = 'block';
        } 
    });
};

function clearSelectedCheckboxes() {
    // Select all checkboxes
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    // Iterate over the NodeList of checkboxes and set their 'checked' property to false
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
}

function getSelectedCheckboxes() {    
    // Select all checked checkboxes within the list
    const checkedBoxes = document.querySelectorAll('input[type="checkbox"]:checked');
    const selectedIds = Array.from(checkedBoxes).map(box => box.id);
    items = selectedIds;
    updateContent();
}