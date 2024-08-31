let items = [];
let Allitems = [
    'time', 'counter', 'throttle', 'Brake_Pedal',
    'motor_temp', 'Battery_1', 'Battery_2', 'Battery_3', 'Battery_4',
    'ca_AmpHrs', 'ca_Voltage', 'ca_Current', 'ca_Speed', 'ca_Miles',
    'ca_Voltage_graph', 'ca_Current_graph', 'ca_Speed_graph',
    'throttle_graph', 'Brake_Pedal_graph'

    ];
var hidden = [false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false];
const objects = [];
var lastTenEntries;

function updateContent() {
    // Get the selected value from the dropdown
    var school = document.getElementById("schoolSelection").value;
    // If set to All, set all items
    if(document.getElementById("itemSelection").value == "All"){
        items = Allitems;
    }
}


async function fetchAndProcessCSV() {
    fetch('/001.data.csv') // TODO: Make this select from 001, 002, 003, and so on
        .then(response => response.text())
        .then(text => {
            const lines = text.trim().split('\n');
            // Assuming there's no header row, adjust if there is one
            const lastTenLines = lines.slice(-10);
            lastTenEntries = lastTenLines.map(line => line.split(','));
            // return lastTenEntries, lastTenEntries[9];
            // console.log("lastTenEntries",lastTenEntries);
            // console.log("lastEntrie",lastTenEntries[9]);
        })
        .catch(error => console.error('Error fetching CSV:', error));
}

updateContent();
var realWindowsWidth, realWindowsHeight;

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

function setup() {
    realWindowsWidth = windowWidth - 184;
    realWindowsHeight = windowHeight - 104;
    var canvas = createCanvas(windowWidth-184, windowHeight-104);
    canvas.parent('p5Canvas');
    textAlign(CENTER,CENTER);
    frameRate(20);
    objectSetup();
}
function map(value, minInput, maxInput, minOutput, maxOutput) {
    return (value - minInput) * (maxOutput - minOutput) / (maxInput - minInput) + minOutput;
}

function objectSetup(){
    for (let i = 0; i < objects.length; i++) {
        objects[i].setup();
    }
}


async function draw() {
    fetchAndProcessCSV();
    
    // If the new data failed, try again
    if (lastTenEntries == null){
        return;
    }

    // loop through each object
    for (let i = 0; i < objects.length; i++) {
        // Is this object set to be on the screen
        // If not, hide
        if(items.includes(Allitems[i])){
            //If the object was hidden, set back up
            if(hidden[i]){ 
                hidden[i] = false;
                objects[i].setup();
            }
            
            //Update the object(s)
            if(i >= 0 && i <= 13){
                objects[i].draw(lastTenEntries[9][i]);
            }else if(i >= 14 && i <= 16){
                const CountColumnValues = lastTenEntries.map(row => row[1]);
                const ColumnValues = lastTenEntries.map(row => row[i-4]);
                objects[i].draw(CountColumnValues,ColumnValues)
            }else if(i == 17 || i == 18){
                const CountColumnValues = lastTenEntries.map(row => row[1]);
                const ColumnValues = lastTenEntries.map(row => row[i-15]);
                objects[i].draw(CountColumnValues,ColumnValues)
            }

        }else{
            if(!hidden[i]){
                objects[i].hide();
                hidden[i] = true;
            }
        }
    }
    

}

