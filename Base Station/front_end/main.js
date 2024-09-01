// Initialize an array to store the selected items to be displayed
let items = [];

// List of all possible data items that can be visualized
let Allitems = [
    'time', 'counter', 'throttle', 'Brake_Pedal',
    'motor_temp', 'Battery_1', 'Battery_2', 'Battery_3', 'Battery_4',
    'ca_AmpHrs', 'ca_Voltage', 'ca_Current', 'ca_Speed', 'ca_Miles',
    'ca_Voltage_graph', 'ca_Current_graph', 'ca_Speed_graph',
    'throttle_graph', 'Brake_Pedal_graph'
];

// Array to track visibility state of each object; false means hidden, true means visible
var hidden = [false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false];

// Array to hold object instances for visualization
const objects = [];

// Variable to store the last ten entries from the CSV file
var lastTenEntries;

// Function to update the content displayed based on the selected dropdown option
function updateContent() {
    // If "All" is selected, set all items to be displayed
    if(document.getElementById("itemSelection").value == "All"){
        items = Allitems;
    }
}

// Asynchronous function to fetch the latest CSV file and process its data
async function fetchAndProcessCSV() {
    // Fetch the list of available CSV files from the server
    const fileListResponse = await fetch('/list-files'); // Ensure this endpoint is set up on your server
    if (!fileListResponse.ok) {
      throw new Error('Error fetching the list of files');
    }
    const files = await fileListResponse.json();

    // Check if any CSV files are available
    if (files.length === 0) {
      console.warn("No CSV files found.");
      return;
    }

    // Fetch and process the newest CSV file
    const newestFile = files[files.length - 1];
    fetch(`/${newestFile}`)
        .then(response => response.text())
        .then(text => {
            const lines = text.trim().split('\n');
            const lastTenLines = lines.slice(-10);
            lastTenEntries = lastTenLines.map(line => line.split(','));
        })
        .catch(error => console.error('Error fetching CSV:', error));
}

// Initial setup call to configure the content based on the selected option
updateContent();

// Variables to hold the real dimensions of the window for canvas setup
var realWindowsWidth, realWindowsHeight;

// Create instances of objects to visualize different data metrics
objects[0]  = new plain_text      (650,185, 'Time',            0.9                              );
objects[1]  = new plain_text      (650,240, 'Counter',         0.9                              );
objects[2]  = new throttle        (775, 80, 'Throttle',        1.0                              );
objects[3]  = new brake           (775,170, 'Brake Pedal',     1.0                              );
objects[4]  = new odometer        ( 60,240, 'Motor Temp',      0.55, "°F",     150,        32, 4);
objects[5]  = new odometer        (180,240, 'Temp 1',          0.55, "°F",     120,        32, 4);
objects[6]  = new odometer        (300,240, 'Temp 2',          0.55, "°F",     120,        32, 4);
objects[7]  = new odometer        (420,240, 'Temp 3',          0.55, "°F",     120,        32, 4);
objects[8]  = new odometer        (540,240, 'Temp 4',          0.55, "°F",     120,        32, 4);
objects[9]  = new odometer_counter(600,140, 'Amp Hours',       0.7                              );
objects[10] = new odometer        (225,100, 'Voltage',         0.7, 'V',       53,         43, 0);
objects[11] = new odometer        (375,100, 'Current',         0.7, 'amps',    150,       -20, 6);
objects[12] = new odometer        ( 75,100, 'Speed',           0.7, 'mph',     50,         0    );
objects[13] = new odometer_counter(600, 50, 'Miles',           0.7                              );
objects[14] = new graph           (315,300, 'Voltage',         1.0, "Counter", "Voltage","V"    );
objects[15] = new graph           (525,300, 'Current',         1.0, "Counter", "Current","amps" );
objects[16] = new graph           (105,300, 'Speed',           1.0, "Counter", "Speed","mph"    );
objects[17] = new graph           (735,300, 'Throttle',        1.0, "Counter", "Throttle","%"   );
objects[18] = new graph           (945,300, 'Brake',           1.0, "Counter", "Brake","%"      );

// Function to set up the canvas and initialize objects for visualization
function setup() {
    // Adjust canvas dimensions based on window size
    realWindowsWidth = windowWidth - 184;
    realWindowsHeight = windowHeight - 104;
    var canvas = createCanvas(1220-184, windowHeight-104);
    // var canvas = createCanvas(windowWidth-184, windowHeight-104); // Alternative canvas size
    canvas.parent('p5Canvas'); // Attach canvas to the HTML element with ID 'p5Canvas'
    textAlign(CENTER,CENTER); // Center text alignment
    frameRate(20); // Set the frame rate for drawing
    for (let i = 0; i < objects.length; i++) {
        objects[i].setup(); // Set up each object for visualization
    }
}

// Asynchronous function to fetch data and redraw objects
async function draw() {
    fetchAndProcessCSV(); // Fetch the latest data from the CSV file
    
    // If no new data is available, exit the draw function
    if (lastTenEntries == null){
        return;
    }

    // Loop through each object to update its state and draw it
    for (let i = 0; i < objects.length; i++) {
        // Check if the current item should be displayed on the screen
        if(items.includes(Allitems[i])){
            // If the object was previously hidden, set it up again
            if(hidden[i]){ 
                hidden[i] = false;
                objects[i].setup();
            }

            // Update and draw the object with the latest data
            if(i >= 0 && i <= 13){
                objects[i].draw(lastTenEntries[9][i]);
            }else if(i >= 14 && i <= 16){
                const CountColumnValues = lastTenEntries.map(row => row[1]);
                const ColumnValues = lastTenEntries.map(row => row[i-4]);
                objects[i].draw(CountColumnValues, ColumnValues);
            }else if(i == 17 || i == 18){
                const CountColumnValues = lastTenEntries.map(row => row[1]);
                const ColumnValues = lastTenEntries.map(row => row[i-15]);
                objects[i].draw(CountColumnValues, ColumnValues);
            }

        }else{
            // If the object should not be displayed and is not already hidden, hide it
            if(!hidden[i]){
                objects[i].hide();
                hidden[i] = true;
            }
        }
    }
}
