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
objects[14] = new graph           (105,300, 'Speed',           1.0, "Counter", "Speed","mph"    );
objects[15] = new graph           (315,300, 'Voltage',         1.0, "Counter", "Voltage","V"    );
objects[16] = new graph           (525,300, 'Current',         1.0, "Counter", "Current","amps" );
objects[17] = new graph           (735,300, 'Throttle',        1.0, "Counter", "Throttle","%"   );
objects[18] = new graph           (945,300, 'Brake',           1.0, "Counter", "Brake","%"      );

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

