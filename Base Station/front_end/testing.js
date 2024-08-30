let items = [];
let Allitems = ['ca_AmpHrs', 'ca_Voltage', 'ca_Current', 'ca_Speed', 'ca_Miles',
 'motor_temp', 'Battery_1', 'Battery_2',
  'IMU_Accel_x', 'IMU_Accel_y', 'IMU_Accel_z', 'IMU_Gyro_x', 'IMU_Gyro_y','IMU_Gyro_z',
  'Brake_Pedal', 'throttle', 'counter', 'time'];
var hidden = [false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false];
var objects = [];
var map_to = [
    14,15,16,17,18,
    3,4,5,
    8,9,10,11,12,13,
    6,7,
    2,1
]
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
    fetch('/2.data.csv')
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

objects[0]  = new odometer_counter(600,140, 'Amp Hours',       0.7                               );
// objects[1]  = new odometer        (225,100, 'Voltage',         0.7, 'V',       53,         43,  0);
// objects[2]  = new odometer        (375,100, 'Current',         0.7, 'amps',    150,       -20,  6);
// objects[3]  = new odometer        ( 75,100, 'Speed',           0.7, 'mph',     50,         0     );
// objects[4]  = new odometer_counter(600, 50, 'Miles',           0.7                               );
// objects[5]  = new odometer        (206,375, 'Motor Temp',      0.7, "°F",      150,        32,  4);
// objects[6]  = new odometer        ( 75,300, 'Temp 1',          0.7, "°F",      120,        32,  4);
// objects[7]  = new odometer        ( 75,450, 'Temp 2',          0.7, "°F",      120,        32,  4);
// objects[14] = new brake           (775,180, 'Brake Pedal',     1.0                               );
// objects[15] = new throttle        (775, 80, 'Throttle',        1.0                               );
// objects[16] = new plain_text      (250,490, 'Counter',         1.0                               );
// objects[17] = new plain_text      (600,490, 'Time',            1.0                               );

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

    objects[0].draw(lastTenEntries[9][map_to[i]]);
    
}

