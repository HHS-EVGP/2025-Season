let items = [];
let Allitems = [
    'time', 'counter', 'throttle', 'Brake_Pedal',
    'motor_temp', 'Battery_1', 'Battery_2', 'Battery_3', 'Battery_4',
    'ca_AmpHrs', 'ca_Voltage', 'ca_Current', 'ca_Speed', 'ca_Miles'
    ];
var hidden = [false,false,false,false,false,false,false,false,false,false,false,false,false,false];
var objects = [];
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

objects[0]  = new plain_text      (600,490, 'Time',            1.0                               );
objects[1]  = new plain_text      (250,490, 'Counter',         1.0                               );
objects[2]  = new throttle        (775, 80, 'Throttle',        1.0                               );
objects[3]  = new brake           (775,180, 'Brake Pedal',     1.0                               );
objects[4]  = new odometer        (675,300, 'Motor Temp',      0.7, "°F",      150,        32,  4);
objects[5]  = new odometer        ( 75,300, 'Temp 1',          0.7, "°F",      120,        32,  4);
objects[6]  = new odometer        (225,300, 'Temp 2',          0.7, "°F",      120,        32,  4);
objects[7]  = new odometer        (375,300, 'Temp 3',          0.7, "°F",      120,        32,  4);
objects[8]  = new odometer        (525,300, 'Temp 4',          0.7, "°F",      120,        32,  4);
objects[9]  = new odometer_counter(600,140, 'Amp Hours',       0.7                               );
objects[10] = new odometer        (225,100, 'Voltage',         0.7, 'V',       53,         43,  0);
objects[11] = new odometer        (375,100, 'Current',         0.7, 'amps',    150,       -20,  6);
objects[12] = new odometer        ( 75,100, 'Speed',           0.7, 'mph',     50,         0     );
objects[13] = new odometer_counter(600, 50, 'Miles',           0.7                               );

function setup() {
    realWindowsWidth = windowWidth - 184;
    realWindowsHeight = windowHeight - 104;
    var canvas = createCanvas(windowWidth-184, windowHeight-104);
    canvas.parent('p5Canvas');
    textAlign(CENTER,CENTER);
    frameRate(20);
    for (let i = 0; i < objects.length; i++) {
        objects[i].setup();
    }
}
function map(value, minInput, maxInput, minOutput, maxOutput) {
    return (value - minInput) * (maxOutput - minOutput) / (maxInput - minInput) + minOutput;
}

function windowResized() {  
    realWindowsWidth = windowWidth - 184;
    realWindowsHeight = windowHeight - 104;
    resizeCanvas(windowWidth-184, windowHeight-104);
    for (let i = 0; i < objects.length; i++) {
        objects[i].setup();
    }
}
async function draw() {

    objects[3].draw(0.9);
    
}

