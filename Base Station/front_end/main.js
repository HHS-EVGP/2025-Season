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
objects[1]  = new odometer        (225,100, 'Voltage',         0.7, 'V',       53,         43,  0);
objects[2]  = new odometer        (375,100, 'Current',         0.7, 'amps',    150,       -20,  6);
objects[3]  = new odometer        ( 75,100, 'Speed',           0.7, 'mph',     50,         0     );
objects[4]  = new odometer_counter(600, 50, 'Miles',           0.7                               );
objects[5]  = new odometer        (206,375, 'Motor Temp',      0.7, "°F",      150,        32,  4);
objects[6]  = new odometer        ( 75,300, 'Temp 1',          0.7, "°F",      120,        32,  4);
objects[7]  = new odometer        ( 75,450, 'Temp 2',          0.7, "°F",      120,        32,  4);
// objects[8]  = new graph           (400,200, 'Acceleration. X', 0.9, "Counter", "m per s^2"       );
// objects[9]  = new graph           (589,200, 'Acceleration. Y', 0.9, "Counter", "m per s^2"       );
// objects[10] = new graph           (778,200, 'Acceleration. Z', 0.9, "Counter", "m per s^2"       );
// objects[11] = new graph           (400,344, 'Gyroscopic. X',   0.9, "Counter", "Value?"          );
// objects[12] = new graph           (589,344, 'Gyroscopic. Y',   0.9, "Counter", "Value?"          );
// objects[13] = new graph           (778,344, 'Gyroscopic. Z',   0.9, "Counter", "Value?"          );
objects[14] = new brake           (775,180, 'Brake Pedal',     1.0                               );
objects[15] = new throttle        (775, 80, 'Throttle',        1.0                               );
objects[16] = new plain_text      (250,490, 'Counter',         1.0                               );
objects[17] = new plain_text      (600,490, 'Time',            1.0                               );

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

    // console.log(lastTenEntries);

    fetchAndProcessCSV();


    if (lastTenEntries != null){
        for (let i = 0; i < objects.length; i++) {
            if(items.includes(Allitems[i])){
                if(hidden[i]){
                    hidden[i] = false;
                    objects[i].setup();
                }
                //Update the object if it is live HERE

                if(i >= 0 && i <= 7){
                    if(lastTenEntries[9][map_to[i]] != ""){
                        objects[i].draw(lastTenEntries[9][map_to[i]]);
                    }
                }else if(i >= 8 && i <= 13){
                    // var x = [], y = [];
                    // for(let o = 0; o < 10; o++){
                    //     if(lastTenEntries[o][i] != ""){
                    //         y.push(parseInt(lastTenEntries[o][map_to[i]]));
                    //     }else{
                    //         y.push(null);
                    //     }
                    //     x.push(parseInt(lastTenEntries[o][2]));
                    // }
                    // objects[i].draw(x,y);
                }else if(i == 14 || i == 15){
                    if(lastTenEntries[9][map_to[i]] != ""){
                        let min_input = 0
                        let max_input = 10000

                        let input = map(lastTenEntries[9][map_to[i]],min_input,max_input,0,1);
                        if(input > 1){
                            input = 1;
                        }else if(input < 0){
                            input = 0;
                        }
                        objects[i].draw(input);
                    }else{
                        objects[i].draw(0);
                    }
                }else if(i == 16 || i == 17){
                    objects[i].draw(lastTenEntries[9][map_to[i]]);
                }
    
            }else{
                if(!hidden[i]){
                    objects[i].hide();
                    hidden[i] = true;
                }
            }
        }
    }
}

